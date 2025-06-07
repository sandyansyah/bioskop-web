from datetime import datetime, timedelta
from app import db

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relasi
    bookings = db.relationship('Booking', backref='schedule', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Schedule {self.movie.title} at {self.start_time}>'
    
    @property
    def end_time(self):
        """Menghitung waktu berakhir berdasarkan durasi film"""
        return self.start_time + timedelta(minutes=self.movie.duration)
    
    @property
    def formatted_date(self):
        """Format tanggal untuk tampilan"""
        return self.start_time.strftime("%A, %d %B %Y")
    
    @property
    def formatted_time(self):
        """Format waktu untuk tampilan"""
        return self.start_time.strftime("%H:%M")
    
    def is_past(self):
        """Memeriksa apakah jadwal sudah lewat"""
        return datetime.utcnow() > self.start_time
    
    def get_available_seats_count(self):
        """Menghitung jumlah kursi yang tersedia"""
        from app.models.booking import BookedSeat, Booking
        
        # Hitung total kursi di ruangan
        total_seats = self.room.capacity
        
        # Hitung kursi yang sudah dipesan
        booked_seats = db.session.query(BookedSeat).join(
            Booking, BookedSeat.booking_id == Booking.id
        ).filter(
            Booking.schedule_id == self.id
        ).count()
        
        return total_seats - booked_seats
    
    def is_sold_out(self):
        """Memeriksa apakah semua kursi sudah habis terjual"""
        return self.get_available_seats_count() <= 0