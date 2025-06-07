from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.movie import Movie, Genre
from app.models.schedule import Schedule
from app.models.theater import Theater, Room
from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.sql import func

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

@movies_bp.route('/')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Filter berdasarkan parameter URL
    genre_id = request.args.get('genre', None, type=int)
    search_query = request.args.get('search', None, type=str)
    
    # Buat query dasar
    query = Movie.query.filter_by(is_showing=True)
    
    # Terapkan filter jika ada
    if genre_id:
        query = query.filter(Movie.genres.any(id=genre_id))
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Movie.title.ilike(search_term)) | 
            (Movie.description.ilike(search_term)) |
            (Movie.director.ilike(search_term))
        )
    
    # Urutkan dan paginate
    movies = query.order_by(desc(Movie.release_date)).paginate(page=page, per_page=per_page)
    
    # Ambil semua genre untuk filter sidebar
    genres = Genre.query.all()
    
    return render_template(
        'movies/list.html',
        title='Daftar Film',
        movies=movies,
        genres=genres,
        current_genre=genre_id,
        search_query=search_query
    )

@movies_bp.route('/<int:movie_id>')
def detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Ambil jadwal untuk film ini mulai hari ini sampai 7 hari ke depan
    today = datetime.now()
    next_week = today + timedelta(days=7)
    
    # Query jadwal dan pastikan .all() di akhir
    schedules = Schedule.query.filter(
        Schedule.movie_id == movie_id,
        Schedule.start_time.between(today, next_week),
        Schedule.is_active == True
    ).order_by(Schedule.start_time).all()
    
    # Debug: print jumlah jadwal
    print(f"Jumlah jadwal untuk film {movie.title}: {len(schedules)}")
    
    # Kelompokkan jadwal berdasarkan tanggal
    schedules_by_date = {}
    for schedule in schedules:
        date_str = schedule.start_time.strftime("%Y-%m-%d")
        if date_str not in schedules_by_date:
            schedules_by_date[date_str] = {
                'date': schedule.start_time.date(),
                'formatted_date': schedule.formatted_date,
                'schedules_by_theater': {}
            }
        
        theater_id = schedule.room.theater_id
        if theater_id not in schedules_by_date[date_str]['schedules_by_theater']:
            schedules_by_date[date_str]['schedules_by_theater'][theater_id] = {
                'theater': schedule.room.theater,
                'schedules': []
            }
        
        schedules_by_date[date_str]['schedules_by_theater'][theater_id]['schedules'].append(schedule)
    
    # Debug: print tanggal yang memiliki jadwal
    print(f"Tanggal dengan jadwal: {[k for k in schedules_by_date.keys()]}")
    
    # Urutkan tanggal
    sorted_dates = sorted(schedules_by_date.keys())
    
    return render_template(
        'movies/detail.html',
        title=movie.title,
        movie=movie,
        schedules_by_date=schedules_by_date,
        sorted_dates=sorted_dates
    )

@movies_bp.route('/coming-soon')
def coming_soon():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    today = datetime.today().date()
    
    # Ambil film yang akan datang
    movies = Movie.query.filter(
        Movie.release_date > today
    ).order_by(Movie.release_date).paginate(page=page, per_page=per_page)
    
    return render_template(
        'movies/coming_soon.html',
        title='Film Yang Akan Datang',
        movies=movies
    )