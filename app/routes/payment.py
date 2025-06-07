from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from app import db
from app.models.booking import Booking, Payment
import uuid
import datetime

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

class PaymentForm(FlaskForm):
    payment_method = SelectField('Metode Pembayaran', 
                                choices=[('credit_card', 'Kartu Kredit/Debit'), 
                                         ('bank_transfer', 'Transfer Bank'),
                                         ('e_wallet', 'E-Wallet')],
                                validators=[DataRequired()])
    
    card_number = StringField('Nomor Kartu', validators=[Length(min=16, max=16)], 
                             description='Masukkan nomor kartu kredit/debit (16 digit)')
    card_holder = StringField('Nama Pemilik Kartu', validators=[Length(max=100)])
    expiry_date = StringField('Tanggal Kadaluarsa', validators=[Length(min=5, max=5)], 
                             description='Format: MM/YY')
    cvv = StringField('CVV', validators=[Length(min=3, max=3)], 
                     description='3 digit di belakang kartu')
    
    # Bank transfer fields
    bank_name = SelectField('Bank', 
                           choices=[('bca', 'BCA'), ('mandiri', 'Mandiri'), 
                                    ('bni', 'BNI'), ('bri', 'BRI')],
                           description='Pilih bank untuk transfer')
    
    # E-Wallet fields
    wallet_type = SelectField('Jenis E-Wallet', 
                             choices=[('gopay', 'GoPay'), ('ovo', 'OVO'), 
                                      ('dana', 'DANA'), ('linkaja', 'LinkAja')],
                             description='Pilih e-wallet')
    phone_number = StringField('Nomor HP', validators=[Length(max=15)], 
                              description='Nomor HP yang terdaftar di e-wallet')
    
    submit = SubmitField('Bayar Sekarang')

@payment_bp.route('/process/<int:booking_id>')
@login_required
def process(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Pastikan pemesanan milik user yang sedang login
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak diizinkan mengakses pembayaran ini', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Pastikan pemesanan masih pending
    if booking.status != 'pending':
        flash('Pembayaran sudah selesai atau dibatalkan', 'info')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    # Jika pembayaran sudah ada, tampilkan form dengan data yang sudah ada
    payment = Payment.query.filter_by(booking_id=booking_id).first()
    
    form = PaymentForm()
    
    if payment:
        form.payment_method.data = payment.payment_method
    
    return render_template(
        'payment/process.html',
        title='Pembayaran',
        booking=booking,
        form=form,
        payment=payment
    )

@payment_bp.route('/submit/<int:booking_id>', methods=['POST'])
@login_required
def submit(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Pastikan pemesanan milik user yang sedang login
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak diizinkan mengakses pembayaran ini', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Pastikan pemesanan masih pending
    if booking.status != 'pending':
        flash('Pembayaran sudah selesai atau dibatalkan', 'info')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    form = PaymentForm()
    
    if form.validate_on_submit():
        # Cek apakah sudah ada pembayaran untuk booking ini
        payment = Payment.query.filter_by(booking_id=booking_id).first()
        
        if not payment:
            # Buat pembayaran baru
            payment = Payment(
                booking_id=booking_id,
                payment_method=form.payment_method.data,
                amount=booking.total_price,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
        
        # Di aplikasi nyata, di sini kita akan memanggil payment gateway
        # Untuk demo, kita akan langsung mengupdate status pembayaran
        transaction_id = str(uuid.uuid4())
        payment.complete_payment(transaction_id)
        
        flash('Pembayaran berhasil!', 'success')
        
        # Redirect ke halaman sukses
        return redirect(url_for('payment.success', booking_id=booking_id))
    
    # Jika form tidak valid, tampilkan kembali form dengan error
    return render_template(
        'payment/process.html',
        title='Pembayaran',
        booking=booking,
        form=form
    )

@payment_bp.route('/success/<int:booking_id>')
@login_required
def success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Pastikan pemesanan milik user yang sedang login
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak diizinkan mengakses halaman ini', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    payment = Payment.query.filter_by(booking_id=booking_id).first()
    
    if not payment or payment.status != 'completed':
        flash('Pembayaran belum selesai', 'warning')
        return redirect(url_for('payment.process', booking_id=booking_id))
    
    return render_template(
        'payment/success.html',
        title='Pembayaran Berhasil',
        booking=booking,
        payment=payment
    )

@payment_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Pastikan pemesanan milik user yang sedang login
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Anda tidak diizinkan membatalkan pembayaran ini', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Pastikan pemesanan masih pending
    if booking.status != 'pending':
        flash('Pembayaran sudah selesai atau dibatalkan', 'info')
        return redirect(url_for('booking.view_booking', booking_id=booking_id))
    
    # Batalkan pemesanan
    booking.status = 'cancelled'
    
    # Batalkan pembayaran jika ada
    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if payment:
        payment.status = 'failed'
    
    db.session.commit()
    
    flash('Pembayaran dibatalkan', 'info')
    return redirect(url_for('booking.my_bookings'))