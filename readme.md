README - Sistem Pemesanan Tiket Bioskop
Deskripsi
Sistem Pemesanan Tiket Bioskop adalah aplikasi web berbasis Flask yang memungkinkan pengguna untuk melihat film yang sedang tayang, memilih jadwal penayangan, memilih kursi, dan melakukan pembayaran tiket bioskop secara online. Aplikasi ini juga dilengkapi dengan panel admin untuk mengelola film, bioskop, jadwal, dan pemesanan.
Teknologi yang Digunakan

Backend: Python 3.12, Flask
Database: SQLite (dapat diubah ke PostgreSQL/MySQL untuk produksi)
ORM: SQLAlchemy
Frontend: HTML, CSS, JavaScript, Bootstrap 5
Authentication: Flask-Login
Forms: Flask-WTF
Password Hashing: Flask-Bcrypt
Database Migration: Flask-Migrate

Cara Menjalankan Aplikasi
Prasyarat

Python 3.12.x
pip (Python package manager)

Langkah Instalasi

Clone repositori
bashgit clone https://github.com/sandyansyah/bioskop-web.git
cd bioskop-web

Buat virtual environment
bashpython -m venv venv

# Aktifkan virtual environment
# Di Windows
venv\Scripts\activate
# Di Linux/Mac
source venv/bin/activate

Instal dependensi
bashpip install -r requirements.txt

Siapkan database
bash# Inisialisasi migrasi
flask db init

# Buat migrasi awal
flask db migrate -m "Initial migration"

# Terapkan migrasi
flask db upgrade

Buat folder uploads
bash# Di Windows
mkdir app\static\uploads
# Di Linux/Mac
mkdir -p app/static/uploads

Buat akun admin (lihat bagian Akun Admin di bawah)
Jalankan aplikasi
bashpython run.py

Akses aplikasi
Buka browser dan kunjungi http://localhost:5000

Akun Admin
Aplikasi memerlukan akun admin untuk mengelola konten. Anda dapat membuat akun admin dengan menggunakan cara berikut:
Cara 1: Registrasi dan Update Database

Registrasi pengguna biasa melalui halaman registrasi (/auth/register)
Gunakan Python shell untuk mengubah status pengguna menjadi admin:

bash# Aktifkan virtual environment terlebih dahulu
# Lalu masuk ke Python shell
python

# Di dalam Python shell:
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Ubah username sesuai dengan yang Anda daftarkan
    user = User.query.filter_by(username='admin').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"User {user.username} telah diubah menjadi admin!")
    else:
        print("User tidak ditemukan!")
Cara 2: Menggunakan Script untuk Membuat Admin
Buat file create_admin.py dengan konten berikut:
pythonfrom app import create_app, db
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
            password='admin123', # password akan di-hash otomatis
            full_name='Administrator',
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("PENTING: Ubah password ini setelah login pertama!")

if __name__ == '__main__':
    create_admin_user()
Jalankan script:
bashpython create_admin.py
Kredensial Admin Default
Setelah menjalankan script di atas, Anda bisa login dengan:

Username: admin
Password: admin123

PENTING: Ubah password default segera setelah login pertama kali!
Fitur-fitur Utama
Fitur Pengguna

Registrasi dan login
Melihat daftar film yang sedang tayang
Melihat detail film dan jadwal
Memilih kursi secara interaktif
Melakukan pembayaran
Melihat riwayat pemesanan
Mencetak tiket elektronik

Fitur Admin

Dashboard dengan statistik
Manajemen film (tambah, edit, hapus)
Manajemen bioskop dan studio
Pengaturan denah kursi
Manajemen jadwal tayang
Melihat laporan pemesanan dan pembayaran
Manajemen pengguna

Struktur Proyek
cinema_booking/
│
├── app/
│   ├── __init__.py           # Inisialisasi aplikasi Flask
│   ├── config.py             # Konfigurasi aplikasi
│   ├── models/               # Model database
│   ├── routes/               # Route aplikasi
│   ├── static/               # Aset statis (CSS, JS, gambar)
│   └── templates/            # Template HTML
│
├── migrations/               # Migrasi database
├── venv/                     # Virtual environment
├── .gitignore
├── requirements.txt          # Dependensi
└── run.py                    # Script untuk menjalankan aplikasi
Catatan Penggunaan

Aplikasi ini menggunakan SQLite sebagai database default, yang cocok untuk pengembangan dan demo.
Untuk penggunaan produksi, pertimbangkan untuk mengubah ke PostgreSQL atau MySQL.
Semua pembayaran diproses dalam mode simulasi, tidak ada transaksi nyata yang terjadi.

Kontribusi
Kontribusi selalu disambut baik! Silakan ajukan pull request atau buat issue jika Anda menemukan masalah.

CinemaTicket - Sistem Pemesanan Tiket Bioskop Online
Deskripsi
CinemaTicket adalah aplikasi web berbasis Flask yang menyediakan sistem lengkap untuk pemesanan tiket bioskop secara online. Aplikasi ini memungkinkan pengguna untuk melihat film yang sedang tayang, memilih jadwal penayangan, memilih kursi, dan melakukan pembayaran. Admin juga dapat mengelola film, bioskop, studio, jadwal, dan melihat data pemesanan.
Teknologi yang Digunakan

Backend: Python 3.12, Flask
Database: SQLite (development), dapat diadaptasi ke PostgreSQL/MySQL (production)
ORM: SQLAlchemy
Frontend: HTML, CSS, JavaScript, Bootstrap 5
Authentication: Flask-Login
Forms: Flask-WTF, WTForms
Password Hashing: Flask-Bcrypt
Migrasi Database: Flask-Migrate

Fitur Utama
Pengguna

Registrasi dan login akun
Melihat film yang sedang tayang dan akan datang
Melihat detail film dan jadwal tayang
Pemilihan kursi secara visual dan interaktif
Proses pembayaran (simulasi)
Melihat dan mengelola tiket yang telah dibeli

Admin

Dashboard dengan statistik
Manajemen film (tambah, edit, hapus)
Manajemen bioskop dan studio
Pengaturan kursi untuk setiap studio
Manajemen jadwal tayang (manual dan otomatis)
Manajemen pengguna
Melihat dan mengelola pemesanan

Struktur Proyek
cinema_booking/
│
├── app/
│   ├── __init__.py           # Inisialisasi aplikasi Flask
│   ├── config.py             # Konfigurasi aplikasi
│   ├── models/               # Model database
│   ├── routes/               # Route aplikasi
│   ├── static/               # Aset statis (CSS, JS, gambar)
│   └── templates/            # Template HTML
│
├── migrations/               # Migrasi database
├── venv/                     # Virtual environment
├── seed_data.py              # Script untuk mengisi data awal
├── create_admin.py           # Script untuk membuat akun admin
├── requirements.txt          # Dependensi
└── run.py                    # Script untuk menjalankan aplikasi
Petunjuk Instalasi
Prasyarat

Python 3.12 atau lebih baru
pip (Python package manager)

Langkah-langkah Instalasi

Clone repositori
bashgit clone https://github.com/sandyansyah/cinema-booking.git
cd cinema-booking

Buat virtual environment
bashpython -m venv venv

# Aktifkan virtual environment
# Di Windows
venv\Scripts\activate
# Di Linux/Mac
source venv/bin/activate

Instal dependensi
bashpip install -r requirements.txt

Buat struktur folder uploads
bashmkdir -p app/static/uploads

Inisialisasi database
bashflask db init
flask db migrate -m "Initial migration"
flask db upgrade

Isi data awal
bashpython seed_data.py

Buat akun admin
bashpython create_admin.py

Jalankan aplikasi
bashpython run.py

Akses aplikasi
Buka browser dan kunjungi http://127.0.0.1:5000

Kredensial Default
Admin

Username: admin
Password: 123

Petunjuk Penggunaan
Sebagai Pengguna

Registrasi/Login: Buat akun baru atau login dengan akun yang sudah ada
Jelajahi Film: Lihat film yang sedang tayang atau akan datang
Pilih Film: Klik pada film untuk melihat detail dan jadwal
Pesan Tiket: Pilih jadwal, kursi, dan lanjutkan ke pembayaran
Bayar Tiket: Pilih metode pembayaran dan selesaikan transaksi
Kelola Tiket: Lihat dan kelola tiket yang telah dibeli di halaman Tiket Saya

Sebagai Admin

Login: Gunakan kredensial admin untuk mengakses panel admin
Dashboard: Lihat statistik umum sistem
Kelola Film: Tambah, edit, atau hapus film
Kelola Bioskop: Atur bioskop dan studio
Kelola Jadwal: Atur jadwal penayangan film
Kelola Pengguna: Lihat dan atur hak akses pengguna
Lihat Pemesanan: Pantau dan kelola pemesanan tiket

Mengatasi Masalah Umum
Error: "TypeError: list() takes 0 positional arguments but 1 was given"
Jika Anda mengalami error ini, perbaiki file app/routes/movies.py dengan mengganti:
pythonprint(f"Tanggal dengan jadwal: {list(schedules_by_date.keys())}")
menjadi:
pythonprint(f"Tanggal dengan jadwal: {', '.join(schedules_by_date.keys())}")
Jadwal tidak muncul di halaman detail film
Pastikan:

Film memiliki status "Sedang Tayang"
Sudah ada jadwal yang dibuat untuk film tersebut
Jadwal berada dalam rentang waktu 7 hari ke depan dari sekarang
Studio dan bioskop terkait sudah dibuat dan aktif

Pemilihan kursi tidak berfungsi
Pastikan:

Kursi sudah dibuat untuk studio terkait
Kursi memiliki status "Aktif"
JavaScript di browser diaktifkan

Pengembangan Lebih Lanjut
Menambahkan Payment Gateway
Untuk mengintegrasikan payment gateway sungguhan, modifikasi app/routes/payment.py dan tambahkan integrasi dengan layanan seperti Midtrans, Xendit, atau provider pembayaran lainnya.
Menggunakan Database Production
Untuk menggunakan database PostgreSQL atau MySQL:

Instal package tambahan: pip install psycopg2 (PostgreSQL) atau pip install mysqlclient (MySQL)
Ubah SQLALCHEMY_DATABASE_URI di app/config.py

Deployment
Untuk deployment ke server production:

Gunakan WSGI server seperti Gunicorn: pip install gunicorn
Buat file wsgi.py:
pythonfrom app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

Jalankan dengan Gunicorn: gunicorn wsgi:app
