from datetime import datetime
from app import db

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relasi
    movies = db.relationship('Movie', secondary='movie_genres', backref='genres')
    
    def __repr__(self):
        return f'<Genre {self.name}>'

# Tabel asosiasi untuk many-to-many relationship antara Movie dan Genre
movie_genres = db.Table('movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False)  # Durasi dalam menit
    release_date = db.Column(db.Date, nullable=True)
    poster_image = db.Column(db.String(255), nullable=True)  # Path ke file poster
    trailer_url = db.Column(db.String(255), nullable=True)
    director = db.Column(db.String(100), nullable=True)
    cast = db.Column(db.Text, nullable=True)
    rating = db.Column(db.String(10), nullable=True)  # Rating film (G, PG, PG-13, R, dll)
    is_showing = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relasi
    schedules = db.relationship('Schedule', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def get_genres_str(self):
        return ', '.join(genre.name for genre in self.genres)