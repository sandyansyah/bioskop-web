# Import semua model agar tersedia di namespace app.models
from app.models.user import User
from app.models.movie import Movie, Genre, movie_genres
from app.models.theater import Theater, Room
from app.models.seat import Seat, SeatType
from app.models.schedule import Schedule
from app.models.booking import Booking, BookedSeat, Payment