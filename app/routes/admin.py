from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, DateField, SelectField, BooleanField, SubmitField, SelectMultipleField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app import db
from app.models.user import User
from app.models.movie import Movie, Genre
from app.models.theater import Theater, Room
from app.models.seat import Seat, SeatType
from app.models.schedule import Schedule
from app.models.booking import Booking, Payment
from functools import wraps
from datetime import datetime, timedelta, time
import os
import uuid
import random

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator untuk membatasi akses hanya untuk admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Anda tidak memiliki akses ke halaman ini', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Form untuk Movie
class MovieForm(FlaskForm):
    title = StringField('Judul Film', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Deskripsi', validators=[Optional()])
    duration = IntegerField('Durasi (menit)', validators=[DataRequired(), NumberRange(min=1)])
    release_date = DateField('Tanggal Rilis', validators=[Optional()])
    poster_image = FileField('Poster', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    trailer_url = StringField('URL Trailer', validators=[Length(max=255), Optional()])
    director = StringField('Sutradara', validators=[Length(max=100), Optional()])
    cast = TextAreaField('Pemeran', validators=[Optional()])
    rating = StringField('Rating', validators=[Length(max=10), Optional()])
    genres = SelectMultipleField('Genre', coerce=int)
    is_showing = BooleanField('Sedang Tayang')
    submit = SubmitField('Simpan')

# Form untuk Theater
class TheaterForm(FlaskForm):
    name = StringField('Nama Bioskop', validators=[DataRequired(), Length(max=100)])
    location = StringField('Lokasi', validators=[Length(max=200), Optional()])
    description = TextAreaField('Deskripsi', validators=[Optional()])
    submit = SubmitField('Simpan')

# Form untuk Room
class RoomForm(FlaskForm):
    name = StringField('Nama Studio', validators=[DataRequired(), Length(max=50)])
    capacity = IntegerField('Kapasitas', validators=[DataRequired(), NumberRange(min=1)])
    theater_id = SelectField('Bioskop', coerce=int, validators=[DataRequired()])
    room_type = StringField('Tipe Studio', validators=[Length(max=50), Optional()])
    is_active = BooleanField('Aktif')
    submit = SubmitField('Simpan')

# Form untuk Schedule
class ScheduleForm(FlaskForm):
    movie_id = SelectField('Film', coerce=int, validators=[DataRequired()])
    room_id = SelectField('Studio', coerce=int, validators=[DataRequired()])
    start_time = StringField('Waktu Mulai', validators=[DataRequired()], 
                           description='Format: YYYY-MM-DD HH:MM')
    price = FloatField('Harga Tiket', validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Aktif')
    submit = SubmitField('Simpan')

def generate_default_schedules(movie_id, days=7):
    """
    Generate jadwal default untuk film baru
    - 3 jadwal per hari (pagi, siang, malam)
    - Untuk 7 hari ke depan
    """
    movie = Movie.query.get(movie_id)
    if not movie:
        return False
    
    # Dapatkan semua studio yang aktif
    rooms = Room.query.filter_by(is_active=True).all()
    if not rooms:
        return False
    
    # Pilih beberapa studio secara acak (maksimal 3)
    selected_rooms = random.sample(rooms, min(3, len(rooms)))
    
    # Waktu default untuk pemutaran: pagi, siang, malam
    show_times = [
        {"hour": 10, "minute": 30},  # 10:30 pagi
        {"hour": 14, "minute": 0},   # 14:00 siang
        {"hour": 19, "minute": 0}    # 19:00 malam
    ]
    
    # Harga default
    default_price = 50000
    
    # Generate jadwal untuk 7 hari ke depan
    today = datetime.now().date()
    schedules_created = 0
    
    for day_offset in range(days):
        # Tanggal jadwal
        schedule_date = today + timedelta(days=day_offset)
        
        # Untuk setiap studio
        for room in selected_rooms:
            # Untuk setiap waktu pemutaran
            for show_time in show_times:
                # Buat objek datetime
                start_time = datetime.combine(
                    schedule_date, 
                    time(hour=show_time["hour"], minute=show_time["minute"])
                )
                
                # Lewati jika jadwal di masa lalu
                if start_time < datetime.now():
                    continue
                
                # Buat jadwal baru
                schedule = Schedule(
                    movie_id=movie.id,
                    room_id=room.id,
                    start_time=start_time,
                    price=default_price,
                    is_active=True
                )
                
                db.session.add(schedule)
                schedules_created += 1
    
    db.session.commit()
    return schedules_created

# Dashboard Admin
@admin_bp.route('/')
@login_required
@admin_required
def index():
    # Hitung statistik untuk dashboard
    total_movies = Movie.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_bookings = Booking.query.count()
    total_theaters = Theater.query.count()
    
    # Hitung pendapatan
    revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0
    
    # Booking terbaru
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        total_movies=total_movies,
        total_users=total_users,
        total_bookings=total_bookings,
        total_theaters=total_theaters,
        revenue=revenue,
        recent_bookings=recent_bookings
    )

# CRUD Film
@admin_bp.route('/movies')
@login_required
@admin_required
def movies():
    movies = Movie.query.order_by(Movie.title).all()
    return render_template('admin/movies.html', title='Kelola Film', movies=movies)

@admin_bp.route('/movies/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_movie():
    form = MovieForm()
    
    # Populate genre choices
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]
    
    if form.validate_on_submit():
        filename = None
        
        # Handle poster upload
        if form.poster_image.data:
            f = form.poster_image.data
            filename = str(uuid.uuid4()) + os.path.splitext(f.filename)[1]
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        movie = Movie(
            title=form.title.data,
            description=form.description.data,
            duration=form.duration.data,
            release_date=form.release_date.data,
            poster_image=filename,
            trailer_url=form.trailer_url.data,
            director=form.director.data,
            cast=form.cast.data,
            rating=form.rating.data,
            is_showing=form.is_showing.data
        )
        
        db.session.add(movie)
        db.session.flush()  # Get movie ID without committing
        
        # Add genres
        if form.genres.data:
            for genre_id in form.genres.data:
                genre = Genre.query.get(genre_id)
                if genre:
                    movie.genres.append(genre)
        
        db.session.commit()
        
        # Generate jadwal otomatis jika film sedang tayang
        if movie.is_showing:
            schedules_count = generate_default_schedules(movie.id)
            if schedules_count > 0:
                flash(f'Film berhasil ditambahkan dengan {schedules_count} jadwal otomatis', 'success')
            else:
                flash('Film berhasil ditambahkan, tetapi tidak bisa membuat jadwal otomatis', 'warning')
        else:
            flash('Film berhasil ditambahkan', 'success')
            
        return redirect(url_for('admin.movies'))
    
    return render_template('admin/movie_form.html', title='Tambah Film', form=form)

@admin_bp.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)
    
    # Populate genre choices
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]
    
    if request.method == 'GET':
        form.genres.data = [genre.id for genre in movie.genres]
    
    if form.validate_on_submit():
        # Handle poster upload
        if form.poster_image.data:
            # Delete old poster if exists
            if movie.poster_image:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], movie.poster_image))
                except OSError:
                    pass
            
            f = form.poster_image.data
            filename = str(uuid.uuid4()) + os.path.splitext(f.filename)[1]
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            movie.poster_image = filename
        
        # Cek apakah status is_showing berubah
        was_showing = movie.is_showing
        will_be_showing = form.is_showing.data
        
        movie.title = form.title.data
        movie.description = form.description.data
        movie.duration = form.duration.data
        movie.release_date = form.release_date.data
        movie.trailer_url = form.trailer_url.data
        movie.director = form.director.data
        movie.cast = form.cast.data
        movie.rating = form.rating.data
        movie.is_showing = will_be_showing
        
        # Update genres
        movie.genres = []
        if form.genres.data:
            for genre_id in form.genres.data:
                genre = Genre.query.get(genre_id)
                if genre:
                    movie.genres.append(genre)
        
        db.session.commit()
        
        # Jika film baru diubah menjadi 'Sedang Tayang' dan sebelumnya tidak, buat jadwal otomatis
        if will_be_showing and not was_showing:
            # Hitung jumlah jadwal yang sudah ada
            existing_schedules = Schedule.query.filter_by(movie_id=movie.id).count()
            
            # Jika belum ada jadwal, buat jadwal otomatis
            if existing_schedules == 0:
                schedules_count = generate_default_schedules(movie.id)
                if schedules_count > 0:
                    flash(f'Film berhasil diperbarui dan ditambahkan {schedules_count} jadwal otomatis', 'success')
                else:
                    flash('Film berhasil diperbarui, tetapi tidak bisa membuat jadwal otomatis', 'warning')
            else:
                flash('Film berhasil diperbarui', 'success')
        else:
            flash('Film berhasil diperbarui', 'success')
            
        return redirect(url_for('admin.movies'))
    
    return render_template('admin/movie_form.html', title='Edit Film', form=form, movie=movie)

@admin_bp.route('/movies/delete/<int:movie_id>', methods=['POST'])
@login_required
@admin_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Delete poster if exists
    if movie.poster_image:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], movie.poster_image))
        except OSError:
            pass
    
    db.session.delete(movie)
    db.session.commit()
    
    flash('Film berhasil dihapus', 'success')
    return redirect(url_for('admin.movies'))

# CRUD Theater
@admin_bp.route('/theaters')
@login_required
@admin_required
def theaters():
    theaters = Theater.query.all()
    return render_template('admin/theaters.html', title='Kelola Bioskop', theaters=theaters)

@admin_bp.route('/theaters/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_theater():
    form = TheaterForm()
    
    if form.validate_on_submit():
        theater = Theater(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data
        )
        
        db.session.add(theater)
        db.session.commit()
        
        flash('Bioskop berhasil ditambahkan', 'success')
        return redirect(url_for('admin.theaters'))
    
    return render_template('admin/theater_form.html', title='Tambah Bioskop', form=form)

@admin_bp.route('/theaters/edit/<int:theater_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_theater(theater_id):
    theater = Theater.query.get_or_404(theater_id)
    form = TheaterForm(obj=theater)
    
    if form.validate_on_submit():
        theater.name = form.name.data
        theater.location = form.location.data
        theater.description = form.description.data
        
        db.session.commit()
        
        flash('Bioskop berhasil diperbarui', 'success')
        return redirect(url_for('admin.theaters'))
    
    return render_template('admin/theater_form.html', title='Edit Bioskop', form=form, theater=theater)

@admin_bp.route('/theaters/delete/<int:theater_id>', methods=['POST'])
@login_required
@admin_required
def delete_theater(theater_id):
    theater = Theater.query.get_or_404(theater_id)
    
    db.session.delete(theater)
    db.session.commit()
    
    flash('Bioskop berhasil dihapus', 'success')
    return redirect(url_for('admin.theaters'))

# CRUD Room
@admin_bp.route('/rooms')
@login_required
@admin_required
def rooms():
    rooms = Room.query.join(Theater).order_by(Theater.name, Room.name).all()
    return render_template('admin/rooms.html', title='Kelola Studio', rooms=rooms)

@admin_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_room():
    form = RoomForm()
    
    # Populate theater choices
    form.theater_id.choices = [(t.id, t.name) for t in Theater.query.order_by(Theater.name).all()]
    
    if form.validate_on_submit():
        room = Room(
            name=form.name.data,
            capacity=form.capacity.data,
            theater_id=form.theater_id.data,
            room_type=form.room_type.data,
            is_active=form.is_active.data
        )
        
        db.session.add(room)
        db.session.commit()
        
        # Redirect ke halaman untuk menambahkan kursi
        flash('Studio berhasil ditambahkan. Silakan tambahkan kursi untuk studio ini.', 'success')
        return redirect(url_for('admin.manage_seats', room_id=room.id))
    
    return render_template('admin/room_form.html', title='Tambah Studio', form=form)

@admin_bp.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)
    
    # Populate theater choices
    form.theater_id.choices = [(t.id, t.name) for t in Theater.query.order_by(Theater.name).all()]
    
    if form.validate_on_submit():
        room.name = form.name.data
        room.capacity = form.capacity.data
        room.theater_id = form.theater_id.data
        room.room_type = form.room_type.data
        room.is_active = form.is_active.data
        
        db.session.commit()
        
        flash('Studio berhasil diperbarui', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/room_form.html', title='Edit Studio', form=form, room=room)

@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    
    db.session.delete(room)
    db.session.commit()
    
    flash('Studio berhasil dihapus', 'success')
    return redirect(url_for('admin.rooms'))

# Manage Seats
@admin_bp.route('/rooms/<int:room_id>/seats')
@login_required
@admin_required
def manage_seats(room_id):
    room = Room.query.get_or_404(room_id)
    
    # Get all seats in the room
    seats = Seat.query.filter_by(room_id=room_id).order_by(Seat.row, Seat.number).all()
    
    # Group seats by row
    seats_by_row = {}
    for seat in seats:
        if seat.row not in seats_by_row:
            seats_by_row[seat.row] = []
        seats_by_row[seat.row].append(seat)
    
    # Sort rows
    sorted_rows = sorted(seats_by_row.keys())
    
    return render_template(
        'admin/manage_seats.html',
        title=f'Kelola Kursi - {room.name}',
        room=room,
        seats_by_row=seats_by_row,
        sorted_rows=sorted_rows
    )

@admin_bp.route('/seats/generate/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def generate_seats(room_id):
    room = Room.query.get_or_404(room_id)
    
    # Get parameters from form
    rows = request.form.get('rows', type=int)
    seats_per_row = request.form.get('seats_per_row', type=int)
    
    if not rows or not seats_per_row:
        flash('Jumlah baris dan kursi per baris harus diisi', 'danger')
        return redirect(url_for('admin.manage_seats', room_id=room_id))
    
    # Generate rows as uppercase letters (A, B, C, ...)
    row_labels = [chr(65 + i) for i in range(min(rows, 26))]
    
    # Delete existing seats
    Seat.query.filter_by(room_id=room_id).delete()
    
    # Create new seats
    seats_created = 0
    for row in row_labels:
        for num in range(1, seats_per_row + 1):
            seat = Seat(row=row, number=num, room_id=room_id, is_active=True)
            db.session.add(seat)
            seats_created += 1
    
    # Update room capacity
    room.capacity = rows * seats_per_row
    
    db.session.commit()
    
    flash(f'Berhasil membuat {seats_created} kursi untuk studio {room.name}', 'success')
    return redirect(url_for('admin.manage_seats', room_id=room_id))

@admin_bp.route('/seats/update/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def update_seats(room_id):
    # Pastikan room ada
    room = Room.query.get_or_404(room_id)
    
    # Dapatkan data dari request
    data = request.get_json()
    if not data or 'seatChanges' not in data:
        return jsonify({'success': False, 'message': 'Data tidak valid'}), 400
    
    seat_changes = data['seatChanges']
    
    # Update status kursi
    updated_count = 0
    for seat_id, is_active in seat_changes.items():
        seat = Seat.query.get(int(seat_id))
        if seat and seat.room_id == room_id:
            seat.is_active = bool(is_active)
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Berhasil memperbarui {updated_count} kursi',
        'updatedCount': updated_count
    })

# CRUD Schedule
@admin_bp.route('/schedules')
@login_required
@admin_required
def schedules():
    schedules = Schedule.query.join(Movie).join(Room).order_by(Schedule.start_time.desc()).all()
    return render_template('admin/schedules.html', title='Kelola Jadwal', schedules=schedules)

@admin_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_schedule():
    form = ScheduleForm()
    
    # Populate movie choices
    form.movie_id.choices = [(m.id, m.title) for m in Movie.query.filter_by(is_showing=True).order_by(Movie.title).all()]
    
    # Populate room choices
    rooms = Room.query.filter_by(is_active=True).all()
    form.room_id.choices = [(r.id, f"{r.theater.name} - {r.name}") for r in rooms]
    
    if form.validate_on_submit():
        try:
            start_time = datetime.strptime(form.start_time.data, '%Y-%m-%d %H:%M')
            
            schedule = Schedule(
                movie_id=form.movie_id.data,
                room_id=form.room_id.data,
                start_time=start_time,
                price=form.price.data,
                is_active=form.is_active.data
            )
            
            db.session.add(schedule)
            db.session.commit()
            
            flash('Jadwal berhasil ditambahkan', 'success')
            return redirect(url_for('admin.schedules'))
            
        except ValueError:
            flash('Format tanggal dan waktu tidak valid. Gunakan format YYYY-MM-DD HH:MM', 'danger')
    
    return render_template('admin/schedule_form.html', title='Tambah Jadwal', form=form)

@admin_bp.route('/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Pre-populate form
    form = ScheduleForm(obj=schedule)
    
    # Populate movie choices
    form.movie_id.choices = [(m.id, m.title) for m in Movie.query.order_by(Movie.title).all()]
    
    # Populate room choices
    form.room_id.choices = [(r.id, f"{r.theater.name} - {r.name}") for r in Room.query.join(Theater).order_by(Theater.name, Room.name).all()]
    
    # Set start_time string
    if request.method == 'GET':
        form.start_time.data = schedule.start_time.strftime('%Y-%m-%d %H:%M')
    
    if form.validate_on_submit():
        try:
            start_time = datetime.strptime(form.start_time.data, '%Y-%m-%d %H:%M')
            
            schedule.movie_id = form.movie_id.data
            schedule.room_id = form.room_id.data
            schedule.start_time = start_time
            schedule.price = form.price.data
            schedule.is_active = form.is_active.data
            
            db.session.commit()
            
            flash('Jadwal berhasil diperbarui', 'success')
            return redirect(url_for('admin.schedules'))
            
        except ValueError:
            flash('Format tanggal dan waktu tidak valid. Gunakan format YYYY-MM-DD HH:MM', 'danger')
    
    return render_template('admin/schedule_form.html', title='Edit Jadwal', form=form, schedule=schedule)

@admin_bp.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
@login_required
@admin_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    db.session.delete(schedule)
    db.session.commit()
    
    flash('Jadwal berhasil dihapus', 'success')
    return redirect(url_for('admin.schedules'))

@admin_bp.route('/schedules/generate/<int:movie_id>', methods=['POST'])
@login_required
@admin_required
def generate_movie_schedules(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Generate jadwal
    schedules_count = generate_default_schedules(movie.id)
    
    if schedules_count > 0:
        flash(f'Berhasil membuat {schedules_count} jadwal untuk film {movie.title}', 'success')
    else:
        flash(f'Gagal membuat jadwal untuk film {movie.title}', 'danger')
    
    return redirect(url_for('admin.schedules'))

# Bookings Management
@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', title='Kelola Pemesanan', bookings=bookings)

@admin_bp.route('/bookings/<int:booking_id>')
@login_required
@admin_required
def view_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Get booked seats
    from app.models.seat import Seat
    from app.models.booking import BookedSeat
    
    booked_seats = Seat.query.join(
        BookedSeat, Seat.id == BookedSeat.seat_id
    ).filter(
        BookedSeat.booking_id == booking.id
    ).all()
    
    return render_template(
        'admin/view_booking.html',
        title='Detail Pemesanan',
        booking=booking,
        booked_seats=booked_seats
    )

# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', title='Kelola Pengguna', users=users)

@admin_bp.route('/users/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent self-demotion
    if user.id == current_user.id:
        flash('Anda tidak dapat mengubah status admin Anda sendiri', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'administrator' if user.is_admin else 'pengguna biasa'
    flash(f'Status {user.username} berhasil diubah menjadi {status}', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/complete-booking/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == 'paid':
        booking.status = 'completed'
        db.session.commit()
        flash('Pemesanan berhasil ditandai sebagai selesai', 'success')
    else:
        flash('Hanya pemesanan dengan status "Dibayar" yang dapat ditandai selesai', 'danger')
    
    return redirect(url_for('admin.bookings'))