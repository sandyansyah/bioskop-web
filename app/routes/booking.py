from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models.schedule import Schedule
from app.models.seat import Seat
from app.models.booking import Booking, BookedSeat
from app.models.theater import Room
import json

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/select-seats/<int:schedule_id>')
@login_required
def select_seats(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Pastikan jadwal masih aktif
    if not schedule.is_active:
        flash('Jadwal tidak tersedia', 'danger')
        return redirect(url_for('movies.detail', movie_id=schedule.movie_id))
    
    # Pastikan jadwal belum lewat
    if schedule.is_past():
        flash('Jadwal sudah berlalu', 'danger')
        return redirect(url_for('movies.detail', movie_id=schedule.movie_id))
    
    # Dapatkan semua kursi di ruangan
    room = Room.query.get(schedule.room_id)
    
    # Dapatkan semua kursi dalam ruangan
    all_seats = Seat.query.filter_by(room_id=room.id).order_by(Seat.row, Seat.number).all()
    
    # Dapatkan data kursi yang sudah dipesan
    booked_seats = []
    for seat in all_seats:
        if seat.is_booked(schedule_id):
            booked_seats.append(seat.id)
    
    # Kelompokkan kursi berdasarkan baris
    seats_by_row = {}
    for seat in all_seats:
        if seat.row not in seats_by_row:
            seats_by_row[seat.row] = []
        seats_by_row[seat.row].append(seat)
    
    # Urutkan baris
    sorted_rows = sorted(seats_by_row.keys())
    
    return render_template(
        'booking/select_seats.html',
        title='Pilih Kursi',
        schedule=schedule,
        room=room,
        seats_by_row=seats_by_row,
        sorted_rows=sorted_rows,
        booked_seats=booked_seats,
        base_price=schedule.price
    )

@booking_bp.route('/process-seats', methods=['POST'])
@login_required
def process_seats():
    data = request.get_json()
    
    if not data or 'scheduleId' not in data or 'selectedSeats' not in data:
        return jsonify({'success': False, 'message': 'Data tidak valid'}), 400
    
    schedule_id = data['scheduleId']
    selected_seat_ids = data['selectedSeats']
    
    # Pastikan ada kursi yang dipilih
    if not selected_seat_ids:
        return jsonify({'success': False, 'message': 'Silakan pilih kursi'}), 400
    
    # Dapatkan jadwal
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Hitung total harga
    total_price = schedule.price * len(selected_seat_ids)
    
    # Simpan data sementara di session
    session['booking_data'] = {
        'schedule_id': schedule_id,
        'selected_seats': selected_seat_ids,
        'total_price': total_price
    }
    
    return jsonify({
        'success': True, 
        'redirectUrl': url_for('booking.checkout')
    })

@booking_bp.route('/checkout')
@login_required
def checkout():
    # Ambil data dari session
    booking_data = session.get('booking_data')
    
    if not booking_data:
        flash('Silakan pilih kursi terlebih dahulu', 'warning')
        return redirect(url_for('movies.list'))
    
    schedule_id = booking_data['schedule_id']
    selected_seat_ids = booking_data['selected_seats']
    total_price = booking_data['total_price']
    
    # Dapatkan jadwal
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Dapatkan kursi yang dipilih
    selected_seats = Seat.query.filter(Seat.id.in_(selected_seat_ids)).all()
    
    return render_template(
        'booking/checkout.html',
        title='Checkout',
        schedule=schedule,
        selected_seats=selected_seats,
        total_price=total_price
    )

@booking_bp.route('/confirm', methods=['POST'])
@login_required
def confirm():
    # Ambil data dari session
    booking_data = session.get('booking_data')
    
    if not booking_data:
        flash('Silakan pilih kursi terlebih dahulu', 'warning')
        return redirect(url_for('movies.list'))
    
    schedule_id = booking_data['schedule_id']
    selected_seat_ids = booking_data['selected_seats']
    total_price = booking_data['total_price']
    
    # Buat pemesanan baru
    booking = Booking(
        user_id=current_user.id,
        schedule_id=schedule_id,
        total_price=total_price
    )
    
    db.session.add(booking)
    db.session.flush()  # Dapatkan ID booking tanpa commit
    
    # Tambahkan kursi yang dipesan
    for seat_id in selected_seat_ids:
        booked_seat = BookedSeat(booking_id=booking.id, seat_id=seat_id)
        db.session.add(booked_seat)
    
    db.session.commit()
    
    # Hapus data dari session
    session.pop('booking_data', None)
    
    # Redirect ke halaman pembayaran
    return redirect(url_for('payment.process', booking_id=booking.id))

@booking_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    
    return render_template(
        'booking/my_bookings.html',
        title='Pemesanan Saya',
        bookings=bookings
    )

@booking_bp.route('/view/<int:booking_id>')
@login_required
def view_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Pastikan pemesanan milik user yang sedang login
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak diizinkan melihat pemesanan ini', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Dapatkan kursi yang dipesan
    booked_seats = Seat.query.join(
        BookedSeat, Seat.id == BookedSeat.seat_id
    ).filter(
        BookedSeat.booking_id == booking.id
    ).all()
    
    return render_template(
        'booking/view_booking.html',
        title='Detail Pemesanan',
        booking=booking,
        booked_seats=booked_seats
    )

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Pastikan pemesanan milik user yang sedang login
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak diizinkan membatalkan pemesanan ini', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Pastikan pemesanan masih bisa dibatalkan (status masih pending)
    if booking.status != 'pending':
        flash('Pemesanan tidak dapat dibatalkan', 'danger')
        return redirect(url_for('booking.view_booking', booking_id=booking.id))
    
    booking.cancel()
    flash('Pemesanan berhasil dibatalkan', 'success')
    
    return redirect(url_for('booking.my_bookings'))