from flask import Blueprint, render_template, redirect, url_for
from app.models.movie import Movie, Genre
from app.models.theater import Theater
from app.models.schedule import Schedule
from datetime import datetime, timedelta
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Ambil film-film yang sedang tayang
    now_showing = Movie.query.filter_by(is_showing=True).order_by(desc(Movie.release_date)).limit(6).all()
    
    # Ambil film yang akan datang (dengan tanggal rilis di masa depan)
    today = datetime.today().date()
    coming_soon = Movie.query.filter(Movie.release_date > today).order_by(Movie.release_date).limit(4).all()
    
    # Ambil jadwal untuk hari ini dan 2 hari ke depan (lebih banyak jadwal)
    today_start = datetime.now()
    future_end = (datetime.now() + timedelta(days=2)).replace(hour=23, minute=59, second=59)
    
    upcoming_schedules = Schedule.query.filter(
        Schedule.start_time.between(today_start, future_end),
        Schedule.is_active == True
    ).order_by(Schedule.start_time).limit(15).all()
    
    # Debug info
    print(f"Total jadwal yang ditampilkan: {len(upcoming_schedules)}")
    for schedule in upcoming_schedules:
        print(f"- {schedule.movie.title} di {schedule.room.theater.name} pada {schedule.start_time.strftime('%d/%m/%Y %H:%M')}")
    
    # Ambil semua genre untuk menu filter
    genres = Genre.query.all()
    
    # Ambil semua bioskop untuk menu filter
    theaters = Theater.query.all()
    
    return render_template(
        'index.html',
        title='Beranda',
        now_showing=now_showing,
        coming_soon=coming_soon,
        upcoming_schedules=upcoming_schedules,
        genres=genres,
        theaters=theaters
    )

@main_bp.route('/about')
def about():
    return render_template('about.html', title='Tentang Kami')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html', title='Kontak')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')