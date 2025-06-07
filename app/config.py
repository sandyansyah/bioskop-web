import os
from datetime import timedelta

class Config:
    # Konfigurasi dasar
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-should-be-changed-in-production'
    
    # Konfigurasi database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cinema.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi upload file
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Konfigurasi session
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Konfigurasi pagination
    MOVIES_PER_PAGE = 12
    
    # Konfigurasi pembayaran (contoh untuk integrasi dengan payment gateway)
    PAYMENT_API_KEY = os.environ.get('PAYMENT_API_KEY') or 'test_key'
    PAYMENT_SECRET = os.environ.get('PAYMENT_SECRET') or 'test_secret'
    
    # Mode debug
    DEBUG = os.environ.get('FLASK_DEBUG') or True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Dalam production, gunakan environment variable untuk secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # Dan gunakan database PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'