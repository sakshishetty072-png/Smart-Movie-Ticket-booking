# Movie Magic - Flask Application
# Run this with: python app_new.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'moviemagic_secret_key_2024'

# Import movies data
from movies_data import MOVIES

# In-memory storage for bookings
bookings = []
booking_id_counter = 1

# Home page
@app.route('/')
def index():
    return redirect(url_for('login'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple login (accepts any username/password)
        if username and password:
            session['user'] = username
            session['theme'] = 'dark'
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter username and password')
    
    return render_template('login.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if username and email and password:
            session['user'] = username
            session['email'] = email
            session['theme'] = 'dark'
            return redirect(url_for('dashboard'))
        else:
            flash('Please fill all fields')
    
    return render_template('signup.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Dashboard with search and filter
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    genre_filter = request.args.get('genre', '')
    
    # Filter movies
    filtered_movies = MOVIES
    
    if search_query:
        filtered_movies = [m for m in filtered_movies 
                         if search_query.lower() in m['title'].lower()]
    
    if genre_filter:
        filtered_movies = [m for m in filtered_movies 
                         if m['genre'].lower() == genre_filter.lower()]
    
    return render_template('dashboard.html', 
                         movies=filtered_movies,
                         search_query=search_query,
                         selected_genre=genre_filter)

# Booking page
@app.route('/booking')
def booking():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    movie = request.args.get('movie', '')
    theater = request.args.get('theater', '')
    address = request.args.get('address', '')
    price = request.args.get('price', '250')
    
    return render_template('booking.html',
                         movie=movie,
                         theater=theater,
                         address=address,
                         price=price)

# Payment page
@app.route('/payment', methods=['POST'])
def payment():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    movie = request.form.get('movie', '')
    theater = request.form.get('theater', '')
    address = request.form.get('address', '')
    price = float(request.form.get('price', '250'))
    selected_seats = request.form.get('selected_seats', '')
    
    seats_list = selected_seats.split(',') if selected_seats else []
    total_price = price * len(seats_list)
    
    return render_template('payment.html',
                         movie=movie,
                         theater=theater,
                         address=address,
                         price=price,
                         selected_seats=selected_seats,
                         seats_count=len(seats_list),
                         total_price=total_price)

# Confirmation page
@app.route('/confirmation', methods=['POST'])
def confirmation():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    global booking_id_counter
    
    movie = request.form.get('movie', '')
    theater = request.form.get('theater', '')
    selected_seats = request.form.get('selected_seats', '')
    total_price = float(request.form.get('total_price', '0'))
    
    # Generate booking ID
    booking_id = f"MM{booking_id_counter:05d}"
    booking_id_counter += 1
    
    # Store booking
    booking = {
        'id': booking_id,
        'user': session.get('user'),
        'movie': movie,
        'theater': theater,
        'seats': selected_seats,
        'total': total_price
    }
    bookings.append(booking)
    
    return render_template('confirmation.html',
                         booking_id=booking_id,
                         movie=movie,
                         theater=theater,
                         seats=selected_seats,
                         total=total_price)

# Profile page
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_bookings = [b for b in bookings if b.get('user') == session.get('user')]
    
    return render_template('profile.html',
                         name=session.get('user'),
                         email=session.get('email', 'user@email.com'),
                         bookings=user_bookings)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact_us.html')

if __name__ == '__main__':
    print("🎬 Starting Movie Magic...")
    print(f"📽️ Loaded {len(MOVIES)} movies")
    app.run(debug=True, host='0.0.0.0', port=5000)
