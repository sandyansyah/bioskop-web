import uuid
from datetime import datetime
from app import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(10), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled, completed
    
    # Relasi
    booked_seats = db.relationship('BookedSeat', backref='booking', lazy='dynamic', cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='booking', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, user_id, schedule_id, total_price):
        self.user_id = user_id
        self.schedule_id = schedule_id
        self.total_price = total_price
        self.booking_code = self._generate_booking_code()
    
    def _generate_booking_code(self):
        """Generate a unique booking code"""
        return uuid.uuid4().hex[:8].upper()
    
    def __repr__(self):
        return f'<Booking {self.booking_code}>'
    
    def add_seat(self, seat_id):
        """Tambahkan kursi ke pemesanan"""
        booked_seat = BookedSeat(booking_id=self.id, seat_id=seat_id)
        db.session.add(booked_seat)
        return booked_seat
    
    def get_seat_labels(self):
        """Dapatkan label kursi yang dipesan (mis. A1, B5, dll)"""
        from app.models.seat import Seat
        
        seats = Seat.query.join(
            BookedSeat, Seat.id == BookedSeat.seat_id
        ).filter(
            BookedSeat.booking_id == self.id
        ).all()
        
        return [f"{seat.row}{seat.number}" for seat in seats]
    
    def cancel(self):
        """Batalkan pemesanan"""
        self.status = 'cancelled'
        db.session.commit()

class BookedSeat(db.Model):
    __tablename__ = 'booked_seats'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Tambahkan constraint untuk mencegah duplikasi kursi dalam pemesanan
    __table_args__ = (
        db.UniqueConstraint('booking_id', 'seat_id', name='unique_seat_booking'),
    )
    
    def __repr__(self):
        return f'<BookedSeat {self.seat_id} for Booking {self.booking_id}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    payment_method = db.Column(db.String(50), nullable=False)  # credit_card, transfer, e-wallet
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)  # ID dari payment gateway
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    
    def __repr__(self):
        return f'<Payment {self.id} for Booking {self.booking_id}>'
    
    def complete_payment(self, transaction_id):
        """Menyelesaikan pembayaran"""
        self.transaction_id = transaction_id
        self.status = 'completed'
        self.booking.status = 'paid'
        db.session.commit()