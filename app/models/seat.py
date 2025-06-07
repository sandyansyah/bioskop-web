from app import db

class SeatType(db.Model):
    __tablename__ = 'seat_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price_modifier = db.Column(db.Float, default=1.0)  # Faktor pengali harga (1.0 = harga normal)
    description = db.Column(db.Text, nullable=True)
    
    # Relasi
    seats = db.relationship('Seat', backref='seat_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<SeatType {self.name}>'

class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.String(5), nullable=False)  # A, B, C, dst.
    number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, dst.
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    seat_type_id = db.Column(db.Integer, db.ForeignKey('seat_types.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relasi
    booked_seats = db.relationship('BookedSeat', backref='seat', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('row', 'number', 'room_id', name='unique_seat_in_room'),
    )
    
    def __repr__(self):
        return f'<Seat {self.row}{self.number} in Room {self.room_id}>'
    
    @property
    def seat_label(self):
        return f'{self.row}{self.number}'
    
    def is_booked(self, schedule_id):
        """Memeriksa apakah kursi sudah dipesan untuk jadwal tertentu"""
        from app.models.booking import BookedSeat, Booking
        
        count = BookedSeat.query.join(
            Booking, BookedSeat.booking_id == Booking.id
        ).filter(
            BookedSeat.seat_id == self.id,
            Booking.schedule_id == schedule_id
        ).count()
        
        return count > 0