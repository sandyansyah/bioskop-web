from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from app.config import Config

# Inisialisasi ekstensi
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inisialisasi ekstensi dengan app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # Konfigurasi login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'
    login_manager.login_message_category = 'info'
    
    # Import dan daftarkan blueprint
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.movies import movies_bp
    from app.routes.booking import booking_bp
    from app.routes.payment import payment_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    
    # Buat semua tabel database jika belum ada
    with app.app_context():
        db.create_all()
    
    return app

# Import model untuk memastikan mereka terdaftar dengan SQLAlchemy
from app.models import user, movie, theater, schedule, seat, booking