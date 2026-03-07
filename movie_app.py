"""
Movie Magic - Smart Movie Ticket Booking System
Complete Working Application with Filters and 25 Movies
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'moviemagic-secret-key-2024'

# In-memory storage
users = []
bookings = []
movies = []

# ======================== SEED 25 MOVIES WITH REAL IMAGES ========================
movies = [
    {'movie_id': '1', 'title': 'Pathaan', 'genre': 'Action', 'language': 'Hindi', 'duration': 146, 'image': 'https://m.media-amazon.com/images/M/MV5BMzdjNmQxZjYtNjAyMS00NGY2LWE4YzgtMWQ2MWRmYjMxYzVmXkEyXkFqcGdeQXVyMTkzODUwNzk5._V1_.jpg', 'price': 350, 'rating': 8.5, 'theater': 'PVR Cinemas', 'address': 'MG Road, Bangalore', 'description': 'An Indian spy embarks on a dangerous mission.'},
    {'movie_id': '2', 'title': 'Jawan', 'genre': 'Action', 'language': 'Hindi', 'duration': 165, 'image': 'https://m.media-amazon.com/images/M/MV5BODQ2NDQ4NDEtNTQxOS00NzAxLTgwMjUtMDI1N2FjYjMzYjYmXkEyXkFqcGdeQXVyMTUzNTgzNzM0._V1_.jpg', 'price': 350, 'rating': 8.7, 'theater': 'INOX Forum', 'address': 'Forum Mall, Bangalore', 'description': 'A high-octane action thriller.'},
    {'movie_id': '3', 'title': 'Dunki', 'genre': 'Comedy', 'language': 'Hindi', 'duration': 147, 'image': 'https://m.media-amazon.com/images/M/MV5BY2RmMTk1MGEtZDg0NS00NThlLWE3NzAtM2M4NDE4MjM1YzE5XkEyXkFqcGdeQXVyMTUzNDQ4Mzk5._V1_.jpg', 'price': 300, 'rating': 7.8, 'theater': 'Cinepolis', 'address': 'Orion Mall, Bangalore', 'description': 'A comedy-drama about illegal immigration.'},
    {'movie_id': '4', 'title': 'Animal', 'genre': 'Action', 'language': 'Hindi', 'duration': 201, 'image': 'https://m.media-amazon.com/images/M/MV5BMDBmYTgxYzItMzhhZi00NmRiLWIzMy1hNmFmMjQ1ZTE1NzYxXkEyXkFqcGdeQXVyMTUzNDQ4Mzk5._V1_.jpg', 'price': 400, 'rating': 8.9, 'theater': 'PVR Phoenix', 'address': 'Phoenix Marketcity', 'description': 'A violent tale of revenge.'},
    {'movie_id': '5', 'title': 'Oppenheimer', 'genre': 'Drama', 'language': 'English', 'duration': 180, 'image': 'https://m.media-amazon.com/images/M/MV5BMDBmYTgxYzItMzhhZi00NmRiLWIzMy1hNmFmMjQ1ZTE1NzYxXkEyXkFqcGdeQXVyMTkxNjUyNjc1._V1_.jpg', 'price': 500, 'rating': 9.2, 'theater': 'PVR Orbit', 'address': 'Orbit Mall', 'description': 'The story of atomic bomb creator.'},
    {'movie_id': '6', 'title': 'Leo', 'genre': 'Action', 'language': 'Tamil', 'duration': 165, 'image': 'https://m.media-amazon.com/images/M/MV5BMjkxMzM5NjUtNmZjNi00NzkyLWI2OGQtZjMxMDJhYjcyZjc4XkEyXkFqcGdeQXVyMTAzMDg4NzE0._V1_.jpg', 'price': 350, 'rating': 8.4, 'theater': 'Asian Cineverse', 'address': 'Whitefield', 'description': 'A cafe owner gets caught in danger.'},
    {'movie_id': '7', 'title': 'Dhoom 3', 'genre': 'Action', 'language': 'Hindi', 'duration': 170, 'image': 'https://m.media-amazon.com/images/M/MV5BMTQ2MzE2MDg4NF5BMl5BanBnXkFtZTcwNzQxMjQ0Mw@@._V1_.jpg', 'price': 350, 'rating': 8.1, 'theater': 'PVR Cinemas', 'address': 'Bangalore', 'description': 'A circus entertainer turned terrorist.'},
    {'movie_id': '8', 'title': 'Barbie', 'genre': 'Comedy', 'language': 'English', 'duration': 114, 'image': 'https://m.media-amazon.com/images/M/MV5BNjU3N2QxNzYtMWM4NS00MTdhLTg0YjgtMjM4MDRkZjUwZDkyXkEyXkFqcGdeQXVyMTkzODUwNzk5._V1_.jpg', 'price': 400, 'rating': 7.8, 'theater': 'INOX', 'address': 'Bangalore', 'description': 'Barbie explores the real world.'},
    {'movie_id': '9', 'title': 'Pushpa 2', 'genre': 'Action', 'language': 'Telugu', 'duration': 180, 'image': 'https://m.media-amazon.com/images/M/MV5BMGMxMGRkMWYtNTY2Yy00YjQ3LThjNTMtNDQ0ZDI5ZjdkYjcxXkEyXkFqcGdeQXVyMTY1MzkyNDk2._V1_.jpg', 'price': 380, 'rating': 8.6, 'theater': 'Asian Cineplex', 'address': 'Bangalore', 'description': 'Pushpa continues his journey.'},
    {'movie_id': '10', 'title': 'Devara', 'genre': 'Action', 'language': 'Telugu', 'duration': 175, 'image': 'https://m.media-amazon.com/images/M/MV5BODcwNWE3OTMtMzViMS00Y2JhLWIzMzktMWU2ZDg1N2M5NzE0XkEyXkFqcGdeQXVyMTExNzQ3MDE0._V1_.jpg', 'price': 360, 'rating': 8.3, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'A powerful story of a sea warrior.'},
    {'movie_id': '11', 'title': 'KGF: Chapter 2', 'genre': 'Action', 'language': 'Kannada', 'duration': 168, 'image': 'https://m.media-amazon.com/images/M/MV5BM2Q5YjNjZWMtY2FmMi00NDEyLWJjZGMtOWJmOTg5YjM5YjQ3XkEyXkFqcGdeQXVyMTI5ODk3MzM2._V1_.jpg', 'price': 350, 'rating': 9.0, 'theater': 'Cinepolis', 'address': 'Bangalore', 'description': 'Rocky becomes the ruler of KGF.'},
    {'movie_id': '12', 'title': 'Vikram', 'genre': 'Action', 'language': 'Tamil', 'duration': 175, 'image': 'https://m.media-amazon.com/images/M/MV5BMjMyNzMyODI1NF5BMl5BanBnXkFtZTcwNjYwNTc2Nw@@._V1_.jpg', 'price': 350, 'rating': 8.8, 'theater': 'Asian Movies', 'address': 'Bangalore', 'description': 'A special investigator hunts a drug syndicate.'},
    {'movie_id': '13', 'title': 'RRR', 'genre': 'Action', 'language': 'Telugu', 'duration': 187, 'image': 'https://m.media-amazon.com/images/M/MV5BODVjYjY3ZTMtZVVjMC00YmI4LWExNGQtM2Y5NDI2MjlkNThkXkEyXkFqcGdeQXVyMTkxNjUyNjc1._V1_.jpg', 'price': 380, 'rating': 9.1, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'Two revolutionaries fight for freedom.'},
    {'movie_id': '14', 'title': 'Bahubali 2', 'genre': 'Action', 'language': 'Telugu', 'duration': 167, 'image': 'https://m.media-amazon.com/images/M/MV5BTAzMmQyNGEtZmU5YS00YjQ5LTljYjgtMjY4MzRiNjc2ZTQ3XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg', 'price': 400, 'rating': 9.0, 'theater': 'INOX', 'address': 'Bangalore', 'description': 'The legend of Bahubali continues.'},
    {'movie_id': '15', 'title': '3 Idiots', 'genre': 'Comedy', 'language': 'Hindi', 'duration': 170, 'image': 'https://m.media-amazon.com/images/M/MV5BNTcxMjc3MTgwMl5BMl5BanBnXkFtZTcwNjM4NjQ4MQ@@._V1_.jpg', 'price': 280, 'rating': 9.0, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'Three engineering students navigate college.'},
    {'movie_id': '16', 'title': 'PK', 'genre': 'Comedy', 'language': 'Hindi', 'duration': 153, 'image': 'https://m.media-amazon.com/images/M/MV5BMmRjNmUxN2E2MzQxN15BMl5BanBnXkFtZTcwMTE2MDY2Nw@@._V1_.jpg', 'price': 300, 'rating': 8.5, 'theater': 'Cinepolis', 'address': 'Bangalore', 'description': 'An alien explores human religion.'},
    {'movie_id': '17', 'title': 'Dangal', 'genre': 'Drama', 'language': 'Hindi', 'duration': 161, 'image': 'https://m.media-amazon.com/images/M/MV5BMTQ4MDU1NjIyOF5BMl5BanBnXkFtZTcwNjEwOTkzMw@@._V1_.jpg', 'price': 320, 'rating': 9.3, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'A wrestler trains his daughters.'},
    {'movie_id': '18', 'title': 'Avatar: The Way of Water', 'genre': 'Sci-Fi', 'language': 'English', 'duration': 192, 'image': 'https://m.media-amazon.com/images/M/MV5BMTcxNjM0NDIyMl5BMl5BanBnXkFtZTcwMTQ5MDIzMw@@._V1_.jpg', 'price': 550, 'rating': 8.7, 'theater': 'INOX', 'address': 'Bangalore', 'description': 'Jake returns to protect his family.'},
    {'movie_id': '19', 'title': 'Top Gun: Maverick', 'genre': 'Action', 'language': 'English', 'duration': 131, 'image': 'https://m.media-amazon.com/images/M/MV5BMmExMWI2ZGUtYWJmMi00Y2ZiLWE4NzMtYjAwMjhhOThlMmQ4XkEyXkFqcGdeQXVyMTExNzQ3MDE0._V1_.jpg', 'price': 450, 'rating': 9.1, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'Maverick trains new Top Gun pilots.'},
    {'movie_id': '20', 'title': 'Joker', 'genre': 'Drama', 'language': 'English', 'duration': 122, 'image': 'https://m.media-amazon.com/images/M/MV5BNzY3OTA5NzA5Nl5BMl5BanBnXkFtZTcwNjA0OTY5Nw@@._V1_.jpg', 'price': 380, 'rating': 8.9, 'theater': 'Cinepolis', 'address': 'Bangalore', 'description': 'A failed comedian descends into madness.'},
    {'movie_id': '21', 'title': 'Spider-Man: Spider-Verse', 'genre': 'Animation', 'language': 'English', 'duration': 140, 'image': 'https://m.media-amazon.com/images/M/MV5BMjMwNDkyMTQ3Nl5BMl5BanBnXkFtZTcwOTQ2OTY1Nw@@._V1_.jpg', 'price': 400, 'rating': 9.0, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'Miles Morales journeys across the Spider-Verse.'},
    {'movie_id': '22', 'title': 'Fast X', 'genre': 'Action', 'language': 'English', 'duration': 141, 'image': 'https://m.media-amazon.com/images/M/MV5BMDdlNWY5NzktNWQwYy00NmEwLWFlZTMtZTI1ODMyOGQ1ZTQ2XkEyXkFqcGdeQXVyMTkxNjUyNjc1._V1_.jpg', 'price': 450, 'rating': 7.8, 'theater': 'INOX', 'address': 'Bangalore', 'description': 'Dom faces the most lethal opponent.'},
    {'movie_id': '23', 'title': 'Guardians of the Galaxy', 'genre': 'Action', 'language': 'English', 'duration': 150, 'image': 'https://m.media-amazon.com/images/M/MV5BYWJkZTk4ZDQtMzRiNi00M2FjLWFmNDktNjE2ZmUwYjU0NWUxXkEyXkFqcGdeQXVyMTkxNjUyNjc1._V1_.jpg', 'price': 420, 'rating': 8.6, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'The Guardians protect Rocket.'},
    {'movie_id': '24', 'title': 'Mission: Impossible 7', 'genre': 'Action', 'language': 'English', 'duration': 163, 'image': 'https://m.media-amazon.com/images/M/MV5BMjMzODE1MTQyOV5BMl5BanBnXkFtZTcwNzMzNjkwNw@@._V1_.jpg', 'price': 450, 'rating': 8.5, 'theater': 'INOX', 'address': 'Bangalore', 'description': 'Ethan Hunt faces his most dangerous mission.'},
    {'movie_id': '25', 'title': 'Interstellar', 'genre': 'Sci-Fi', 'language': 'English', 'duration': 169, 'image': 'https://m.media-amazon.com/images/M/MV5BZjk4Y2I2YzUtNWU1Ny00OWQ5LWI3ZDgtOTNmNWFlMTkwMGEyXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg', 'price': 380, 'rating': 9.2, 'theater': 'PVR', 'address': 'Bangalore', 'description': 'Explorers travel through a wormhole in space.'}
]

# ======================== ROUTES ========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home1')
def home1():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home1.html', user=session.get('user'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global users
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        name = request.form['name']
        for user in users:
            if user['email'] == email:
                flash('Email already registered', 'danger')
                return redirect(url_for('signup'))
        new_user = {'id': str(len(users)+1), 'name': name, 'email': email, 'password': password, 'theme': 'dark'}
        users.append(new_user)
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global users
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "admin@moviemagic.com" and password == "admin123":
            session['user'] = {'name': 'Administrator', 'email': email, 'is_admin': True, 'theme': 'dark'}
            return redirect(url_for('admin_dashboard'))
        for user in users:
            if user['email'] == email and check_password_hash(user['password'], password):
                session['user'] = {'name': user['name'], 'email': user['email'], 'theme': user.get('theme', 'dark')}
                return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# ======================== DASHBOARD WITH FILTERS ========================

@app.route('/dashboard')
def dashboard():
    global movies
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    genre_filter = request.args.get('genre', '')
    language_filter = request.args.get('language', '')
    search_query = request.args.get('q', '').strip()
    
    filtered_movies = movies.copy()
    
    if genre_filter:
        filtered_movies = [m for m in filtered_movies if m.get('genre', '').lower() == genre_filter.lower()]
    if language_filter:
        filtered_movies = [m for m in filtered_movies if m.get('language', '').lower() == language_filter.lower()]
    if search_query:
        query = search_query.lower()
        filtered_movies = [m for m in filtered_movies if query in m.get('title', '').lower() or query in m.get('genre', '').lower()]
    
    genres = sorted(set(m.get('genre', '') for m in movies if m.get('genre')))
    languages = sorted(set(m.get('language', '') for m in movies if m.get('language')))
    
    return render_template('dashboard.html', movies=filtered_movies, user=session.get('user'),
                         genres=genres, languages=languages, selected_genre=genre_filter,
                         selected_language=language_filter, search_query=search_query)

@app.route('/movie/<movie_id>')
def movie_details(movie_id):
    global movies
    if 'user' not in session: 
        return redirect(url_for('login'))
    movie = None
    for m in movies:
        if m.get('movie_id') == movie_id:
            movie = m
            break
    if not movie:
        flash('Movie not found', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('movie_details.html', movie=movie)

# ======================== BOOKING ========================

@app.route('/booking')
def booking():
    if 'user' not in session: 
        return redirect(url_for('login'))
    return render_template('booking.html', movie=request.args.get('movie'),
                           theater=request.args.get('theater'), address=request.args.get('address'),
                           price=request.args.get('price'))

@app.route('/payment', methods=['POST'])
def payment():
    if 'user' not in session: 
        return redirect(url_for('login'))
    return render_template('payment.html', booking_details=request.form)

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    global bookings
    if 'user' not in session: 
        return redirect(url_for('login'))
    data = request.form
    try:
        booking_id = f"MM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        booking_item = {
            'booking_id': booking_id, 'movie_name': data.get('movie'), 'theater': data.get('theater'),
            'date': data.get('date'), 'time': data.get('time'), 'seats': data.get('seats'),
            'amount_paid': data.get('amount'), 'address': data.get('address'),
            'booked_by': session['user']['email'], 'user_name': session['user']['name'],
            'payment_id': f"PAY-{str(uuid.uuid4())[:12].upper()}", 'booking_time': datetime.now().isoformat()
        }
        bookings.append(booking_item)
        return render_template('confirmation.html', booking=booking_item)
    except Exception as e:
        print(f"Booking Error: {e}")
        flash('Booking failed.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/profile')
def profile():
    global users, bookings
    if 'user' not in session: 
        return redirect(url_for('login'))
    user_email = session['user']['email']
    user_info = next((u for u in users if u['email'] == user_email), session['user'])
    user_bookings = [b for b in bookings if b.get('booked_by') == user_email]
    return render_template('profile.html', user=user_info, bookings=user_bookings)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    global users
    if 'user' not in session: 
        return redirect(url_for('login'))
    email = session['user']['email']
    fields = {'first_name': request.form.get('first_name', ''), 'last_name': request.form.get('last_name', ''),
              'mobile': request.form.get('mobile', ''), 'theme': request.form.get('theme', 'dark')}
    fields['name'] = f"{fields['first_name']} {fields['last_name']}".strip() or session['user']['name']
    for user in users:
        if user['email'] == email:
            user.update(fields)
            break
    session['user'].update(fields)
    flash('Profile updated!', 'success')
    return redirect(url_for('profile'))

# ======================== ADMIN ========================

@app.route('/admin')
def admin_dashboard():
    global movies
    if 'user' not in session or not session.get('user', {}).get('is_admin'):
        return redirect(url_for('login'))
    return render_template('admin.html', movies=movies)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    global movies
    if 'user' not in session or not session.get('user', {}).get('is_admin'): 
        return redirect(url_for('login'))
    movie_item = {'movie_id': str(uuid.uuid4()), 'title': request.form['title'], 'genre': request.form['genre'],
                  'language': request.form['language'], 'duration': request.form['duration'],
                  'image': request.form['image'], 'price': float(request.form['price'] or 0),
                  'rating': float(request.form['rating'] or 0), 'theater': request.form['theater'],
                  'address': request.form['address'], 'description': request.form['description']}
    movies.append(movie_item)
    flash('Movie added!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_movie/<movie_id>')
def delete_movie(movie_id):
    global movies
    if 'user' not in session or not session.get('user', {}).get('is_admin'): 
        return redirect(url_for('login'))
    movies = [m for m in movies if m.get('movie_id') != movie_id]
    flash('Movie deleted', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    print(f"Loaded {len(movies)} movies with filters!")
    app.run(host='0.0.0.0', port=5000, debug=True)
</parameter>
</create_file>
