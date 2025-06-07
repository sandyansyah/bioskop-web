from app import create_app, db
from app.models.movie import Genre
from app.models.seat import SeatType

def seed_genres():
    """Menambahkan data genre film"""
    genres = [
        "Action", "Adventure", "Animation", "Comedy", "Crime", 
        "Documentary", "Drama", "Fantasy", "Horror", "Mystery", 
        "Romance", "Sci-Fi", "Thriller", "Western", "Family"
    ]
    
    # Periksa apakah genre sudah ada
    existing_genres = [g.name for g in Genre.query.all()]
    
    # Tambahkan hanya genre yang belum ada
    for genre_name in genres:
        if genre_name not in existing_genres:
            genre = Genre(name=genre_name)
            db.session.add(genre)
            print(f"Menambahkan genre: {genre_name}")
    
    db.session.commit()
    print(f"Total {len(Genre.query.all())} genre tersedia")

def seed_seat_types():
    """Menambahkan tipe kursi bioskop"""
    seat_types = [
        {"name": "Regular", "price_modifier": 1.0, "description": "Kursi biasa dengan harga normal"},
        {"name": "Premium", "price_modifier": 1.5, "description": "Kursi lebih nyaman dengan ruang kaki lebih luas"},
        {"name": "VIP", "price_modifier": 2.0, "description": "Kursi mewah dengan layanan khusus"},
        {"name": "Couple", "price_modifier": 2.2, "description": "Kursi sofa untuk berdua tanpa pemisah"}
    ]
    
    # Periksa apakah tipe kursi sudah ada
    existing_types = [t.name for t in SeatType.query.all()]
    
    # Tambahkan hanya tipe yang belum ada
    for type_data in seat_types:
        if type_data["name"] not in existing_types:
            seat_type = SeatType(
                name=type_data["name"],
                price_modifier=type_data["price_modifier"],
                description=type_data["description"]
            )
            db.session.add(seat_type)
            print(f"Menambahkan tipe kursi: {type_data['name']}")
    
    db.session.commit()
    print(f"Total {len(SeatType.query.all())} tipe kursi tersedia")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_genres()
        seed_seat_types()
        print("Data awal berhasil ditambahkan!")