from app import db

class Theater(db.Model):
    __tablename__ = 'theaters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relasi
    rooms = db.relationship('Room', backref='theater', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Theater {self.name}>'

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    theater_id = db.Column(db.Integer, db.ForeignKey('theaters.id'), nullable=False)
    room_type = db.Column(db.String(50), nullable=True)  # Regular, IMAX, 3D, VIP, dll
    is_active = db.Column(db.Boolean, default=True)
    
    # Relasi
    seats = db.relationship('Seat', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Room {self.name} at {self.theater.name}>'
    
    def get_available_seats(self, schedule_id):
        """Mendapatkan kursi yang tersedia untuk jadwal tertentu"""
        from app.models.seat import Seat
        from app.models.booking import BookedSeat
        
        # Dapatkan semua kursi di ruangan ini
        all_seats = Seat.query.filter_by(room_id=self.id).all()
        
        # Dapatkan kursi yang sudah dipesan untuk jadwal ini
        booked_seat_ids = db.session.query(BookedSeat.seat_id).join(
            BookedSeat.booking
        ).filter_by(schedule_id=schedule_id).all()
        
        # Buat set dari ID kursi yang sudah dipesan
        booked_seat_ids = {seat_id for (seat_id,) in booked_seat_ids}
        
        # Filter kursi yang belum dipesan
        available_seats = [seat for seat in all_seats if seat.id not in booked_seat_ids]
        
        return available_seats