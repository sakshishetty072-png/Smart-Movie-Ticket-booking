"""
Movie Magic - Smart Movie Ticket Booking System
Main Flask Application
"""

from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os
import uuid
from movies_data import MOVIES

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'moviemagic-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviemagic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    theater = db.Column(db.String(100))
    show_date = db.Column(db.String(20))
    show_time = db.Column(db.String(20))
    seats_booked = db.Column(db.Integer, nullable=False)
    seat_numbers = db.Column(db.String(200))
    total_price = db.Column(db.Float, nullable=False)
    booking_status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ROUTES ====================

@app.route('/')
def home():
    featured_movies = MOVIES[:8]
    return render_template('home1.html', movies=featured_movies)

@app.route('/movies')
def movies():
    genre = request.args.get('genre')
    location = request.args.get('location')
    
    filtered_movies = MOVIES
    if genre:
        filtered_movies = [m for m in filtered_movies if m['genre'].lower() == genre.lower()]
    if location:
        filtered_movies = [m for m in filtered_movies if location.lower() in m.get('address', '').lower()]
    
    genres = list(set(m['genre'] for m in MOVIES))
    return render_template('movie_details.html', movies=filtered_movies, genres=genres)

@app.route('/movie/<title>')
def movie_detail(title):
    movie = next((m for m in MOVIES if m['title'] == title), None)
    if not movie:
        flash('Movie not found', 'danger')
        return redirect(url_for('movies'))
    return render_template('movie_details.html', movie=movie)

@app.route('/book/<title>', methods=['GET', 'POST'])
@login_required
def book_ticket(title):
    movie = next((m for m in MOVIES if m['title'] == title), None)
    if not movie:
        flash('Movie not found', 'danger')
        return redirect(url_for('movies'))
    
    if request.method == 'POST':
        seats = request.form.getlist('seats')
        show_date = request.form.get('show_date')
        show_time = request.form.get('show_time')
        
        if not seats:
            flash('Please select at least one seat', 'warning')
            return render_template('booking.html', movie=movie)
        
        booking_id = 'MM' + str(uuid.uuid4())[:8].upper()
        total_price = movie['price'] * len(seats)
        
        booking = Booking(
            booking_id=booking_id,
            user_id=current_user.id,
            movie_title=movie['title'],
            theater=movie['theater'],
            show_date=show_date,
            show_time=show_time,
            seats_booked=len(seats),
            seat_numbers=','.join(seats),
            total_price=total_price
        )
        db.session.add(booking)
        db.session.commit()
        
        flash(f'Booking successful! Booking ID: {booking_id}', 'success')
        return redirect(url_for('confirmation', booking_id=booking_id))
    
    return render_template('booking.html', movie=movie)

@app.route('/confirmation/<booking_id>')
@login_required
def confirmation(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id).first_or_404()
    return render_template('confirmation.html', booking=booking)

@app.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('dashboard.html', bookings=bookings)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('Please fill in all required fields', 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists', 'danger')
            return render_template('signup.html')
        
        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.phone = request.form.get('phone')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact_us.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = [m for m in MOVIES if query.lower() in m['title'].lower() or query.lower() in m['genre'].lower()]
    return render_template('movie_details.html', movies=results, search_query=query)

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🎬 Starting Movie Magic...")
    print(f"📽️ Loaded {len(MOVIES)} movies")
    app.run(host='0.0.0.0', port=5000, debug=True)
