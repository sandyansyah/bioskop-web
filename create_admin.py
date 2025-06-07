from app import create_app, db
from app.models.user import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Cek apakah admin sudah ada
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("Admin user already exists!")
            return
        
        # Buat admin baru
        admin = User(
            username='admin',
            email='admin@example.com',
            password='123', # password akan di-hash otomatis
            full_name='Administrator',
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: 123")
        print("PENTING: Ubah password ini setelah login pertama!")

if __name__ == '__main__':
    create_admin_user()