"""
Movie Magic - Smart Movie Ticket Booking System
Flask Application with AWS DynamoDB Integration (with local fallback)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import os

# Try to import boto3, but make it optional
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    from decimal import Decimal
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception
    Decimal = float

app = Flask(__name__)

# Security & Config
app.secret_key = 'moviemagic-secret-key-2024'
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:440744249462:moviemagic"


# AWS Services (initialized lazily)
dynamodb = None
sns = None

# --- IN-MEMORY STORAGE FOR LOCAL DEVELOPMENT ---
# Using dictionaries/lists as per reference guide for initial development
users = []  # List to store user dictionaries
bookings = []  # List to store booking dictionaries
movies = []  # List to store movie dictionaries
booking_counter = 1

# DynamoDB Tables (will be initialized when credentials available)
users_table = None
bookings_table = None
movies_table = None
USE_DYNAMODB = False  # Always use in-memory storage for local development

def init_aws():
    """Initialize AWS services - using in-memory storage for local development"""
    global USE_DYNAMODB
    USE_DYNAMODB = False
    print("Using in-memory storage (local mode)")
    return False

# Initialize AWS on startup
init_aws()

# --- HELPER FUNCTIONS ---

def replace_decimals(obj):
    """Convert DynamoDB Decimals to Integers/Floats"""
    if isinstance(obj, list):
        return [replace_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: replace_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def send_email_notification(booking):
    """Send booking confirmation via SNS"""
    if not SNS_TOPIC_ARN or not USE_DYNAMODB:
        print(f"Email would be sent to {booking.get('user_name')} for booking {booking.get('booking_id')}")
        return True
    try:
        msg = f"Hello {booking['user_name']},\n\nYour booking for {booking['movie_name']} is confirmed!\nBooking ID: {booking['booking_id']}\nSeats: {booking['seats']}\nAmount Paid: Rs. {booking['amount_paid']}\n\nEnjoy the show!"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="MovieMagic Ticket Confirmed",
            Message=msg
        )
        return True
    except Exception as e:
        print(f"SNS Error: {e}")
        return False

# --- ROUTES ---

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/home1')
def home1():
    """Home page after login"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home1.html', user=session.get('user'))

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    """Contact page"""
    return render_template('contact_us.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    global users
    
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        name = request.form['name']
        
        # Check if using DynamoDB
        if USE_DYNAMODB:
            try:
                response = users_table.get_item(Key={'email': email})
                if 'Item' in response:
                    flash('Email already registered', 'danger')
                    return redirect(url_for('signup'))
                
                users_table.put_item(Item={
                    'id': str(uuid.uuid4()), 
                    'name': name, 
                    'email': email, 
                    'password': password, 
                    'theme': 'dark'
                })
                flash('Account created! Please login.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('Error creating account', 'danger')
                print(f"Signup Error: {e}")
        else:
            # Use in-memory storage
            for user in users:
                if user['email'] == email:
                    flash('Email already registered', 'danger')
                    return redirect(url_for('signup'))
            
            new_user = {
                'id': str(len(users) + 1),
                'name': name,
                'email': email,
                'password': password,
                'theme': 'dark'
            }
            users.append(new_user)
            print(f"✅ Current Users List: {users}")
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    global users
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Admin Login Check
        if email == "admin@moviemagic.com" and password == "admin123":
            session['user'] = {'name': 'Administrator', 'email': email, 'is_admin': True, 'theme': 'dark'}
            return redirect(url_for('admin_dashboard'))

        # Check if using DynamoDB
        if USE_DYNAMODB:
            try:
                response = users_table.get_item(Key={'email': email})
                if 'Item' in response:
                    user = replace_decimals(response['Item'])
                    if check_password_hash(user['password'], password):
                        session['user'] = {
                            'name': user['name'], 
                            'email': user['email'],
                            'theme': user.get('theme', 'dark')
                        }
                        return redirect(url_for('dashboard'))
                flash('Invalid credentials', 'danger')
            except Exception as e:
                flash('Login error', 'danger')
                print(f"Login Error: {e}")
        else:
            # Use in-memory storage
            for user in users:
                if user['email'] == email and check_password_hash(user['password'], password):
                    session['user'] = {
                        'name': user['name'], 
                        'email': user['email'],
                        'theme': user.get('theme', 'dark')
                    }
                    print(f"👤 Logged In User Session: {session['user']}")
                    return redirect(url_for('dashboard'))
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# --- DASHBOARD & MOVIES ---

@app.route('/dashboard')
def dashboard():
    """User dashboard with movies"""
    global movies
    
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    movie_list = []
    
    if USE_DYNAMODB:
        try:
            response = movies_table.scan()
            movie_list = replace_decimals(response.get('Items', []))
        except Exception as e:
            print(f"Dashboard Error: {e}")
    else:
        # Use in-memory storage
        movie_list = movies
    
    return render_template('dashboard.html', movies=movie_list, user=session.get('user'))

@app.route('/movie/<movie_id>')
def movie_details(movie_id):
    """Movie detail page"""
    global movies
    
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    movie = None
    
    if USE_DYNAMODB:
        try:
            response = movies_table.get_item(Key={'movie_id': movie_id})
            movie = replace_decimals(response.get('Item'))
        except Exception as e:
            print(f"Movie Details Error: {e}")
    else:
        # Use in-memory storage
        for m in movies:
            if m.get('movie_id') == movie_id:
                movie = m
                break
    
    if not movie:
        flash('Movie not found', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('movie_details.html', movie=movie)

# --- BOOKING & PAYMENT ---

@app.route('/booking')
def booking():
    """Booking page"""
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    return render_template('booking.html',
                           movie=request.args.get('movie'),
                           theater=request.args.get('theater'),
                           address=request.args.get('address'),
                           price=request.args.get('price'))

@app.route('/payment', methods=['POST'])
def payment():
    """Payment page"""
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    return render_template('payment.html', booking_details=request.form)

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    """Confirm booking and store"""
    global bookings, booking_counter
    
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    data = request.form
    try:
        booking_id = f"MM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        fake_payment_id = f"PAY-{str(uuid.uuid4())[:12].upper()}"

        booking_item = {
            'booking_id': booking_id,
            'movie_name': data.get('movie'),
            'theater': data.get('theater'),
            'date': data.get('date'),
            'time': data.get('time'),
            'seats': data.get('seats'),
            'amount_paid': data.get('amount'),
            'address': data.get('address'),
            'booked_by': session['user']['email'],
            'user_name': session['user']['name'],
            'payment_id': fake_payment_id,
            'booking_time': datetime.now().isoformat()
        }
        
        if USE_DYNAMODB:
            bookings_table.put_item(Item=booking_item)
        
        # Always store in memory too
        bookings.append(booking_item)
        print(f"🎟️ Booking Added: {booking_item}")
        print(f"📦 All Bookings: {bookings}")
        
        # Send SNS notification
        send_email_notification(booking_item)
        
        return render_template('confirmation.html', booking=booking_item)
    except Exception as e:
        print(f"Booking Error: {e}")
        flash('Booking failed.', 'danger')
        return redirect(url_for('dashboard'))

# --- USER PROFILE ---

@app.route('/profile')
def profile():
    """User profile page"""
    global users, bookings
    
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    user_email = session['user']['email']
    user_bookings = []
    user_info = {}
    
    if USE_DYNAMODB:
        try:
            user_response = users_table.get_item(Key={'email': user_email})
            if 'Item' in user_response:
                user_info = replace_decimals(user_response['Item'])
                if 'theme' not in user_info:
                    user_info['theme'] = 'dark'
            
            response = bookings_table.scan()
            all_bookings = replace_decimals(response.get('Items', []))
            user_bookings = [b for b in all_bookings if b.get('booked_by') == user_email]
        except Exception as e:
            print(f"Profile Error: {e}")
    else:
        # Use in-memory storage
        for user in users:
            if user['email'] == user_email:
                user_info = user
                break
        if not user_info:
            user_info = session['user']
        
        user_bookings = [b for b in bookings if b.get('booked_by') == user_email]
    
    return render_template('profile.html', user=user_info, bookings=user_bookings)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    global users
    
    if 'user' not in session: 
        return redirect(url_for('login'))
    
    email = session['user']['email']
    
    fields = {
        'first_name': request.form.get('first_name', ''),
        'last_name': request.form.get('last_name', ''),
        'mobile': request.form.get('mobile', ''),
        'birthday': request.form.get('birthday', ''),
        'gender': request.form.get('gender', ''),
        'married': request.form.get('married', ''),
        'theme': request.form.get('theme', 'dark')
    }
    fields['name'] = f"{fields['first_name']} {fields['last_name']}".strip() or session['user']['name']

    if USE_DYNAMODB:
        try:
            users_table.update_item(
                Key={'email': email},
                UpdateExpression="set #n=:n, first_name=:fn, last_name=:ln, mobile=:m, birthday=:b, gender=:g, married=:ma, theme=:t",
                ExpressionAttributeNames={'#n': 'name'},
                ExpressionAttributeValues={
                    ':n': fields['name'], ':fn': fields['first_name'], ':ln': fields['last_name'],
                    ':m': fields['mobile'], ':b': fields['birthday'], ':g': fields['gender'], 
                    ':ma': fields['married'], ':t': fields['theme']
                }
            )
        except Exception as e:
            flash('Error updating profile', 'danger')
            print(f"Update Profile Error: {e}")
    else:
        # Update in-memory
        for user in users:
            if user['email'] == email:
                user['name'] = fields['name']
                user['theme'] = fields['theme']
                user['first_name'] = fields['first_name']
                user['last_name'] = fields['last_name']
                user['mobile'] = fields['mobile']
                user['birthday'] = fields['birthday']
                user['gender'] = fields['gender']
                user['married'] = fields['married']
                break
    
    session['user']['name'] = fields['name']
    session['user']['theme'] = fields['theme']
    session.modified = True
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

# --- ADMIN PORTAL ---

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    global movies
    
    if 'user' not in session or not session.get('user', {}).get('is_admin'):
        return redirect(url_for('login'))
    
    movie_list = []
    
    if USE_DYNAMODB:
        try:
            response = movies_table.scan()
            movie_list = replace_decimals(response.get('Items', []))
        except Exception as e:
            print(f"Admin Dashboard Error: {e}")
    else:
        movie_list = movies
    
    return render_template('admin.html', movies=movie_list)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    """Add new movie"""
    global movies
    
    if 'user' not in session or not session.get('user', {}).get('is_admin'): 
        return redirect(url_for('login'))
    
    try:
        price = request.form['price'] or 0
        rating = request.form['rating'] or 0

        movie_item = {
            'movie_id': str(uuid.uuid4()),
            'title': request.form['title'],
            'genre': request.form['genre'],
            'language': request.form['language'],
            'duration': request.form['duration'],
            'image': request.form['image'],
            'trailer': request.form['trailer'],
            'price': Decimal(str(price)) if USE_DYNAMODB else price,
            'rating': Decimal(str(rating)) if USE_DYNAMODB else rating,
            'theater': request.form['theater'],
            'address': request.form['address'],
            'description': request.form['description']
        }
        
        if USE_DYNAMODB:
            movies_table.put_item(Item=movie_item)
        
        # Also add to in-memory
        movies.append(movie_item)
        flash('Movie added successfully!', 'success')
    except Exception as e:
        print(f"Add Movie Error: {e}")
        flash('Error adding movie', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_movie/<movie_id>', methods=['POST'])
def edit_movie(movie_id):
    """Edit existing movie"""
    if 'user' not in session or not session.get('user', {}).get('is_admin'): 
        return redirect(url_for('login'))
    
    try:
        price = request.form['price'] or 0
        rating = request.form['rating'] or 0

        if USE_DYNAMODB:
            movies_table.update_item(
                Key={'movie_id': movie_id},
                UpdateExpression="set title=:t, genre=:g, #l=:l, #d=:d, image=:i, trailer=:tr, price=:p, rating=:r, theater=:th, address=:a, description=:desc",
                ExpressionAttributeNames={'#l': 'language', '#d': 'duration'},
                ExpressionAttributeValues={
                    ':t': request.form['title'], ':g': request.form['genre'],
                    ':l': request.form['language'], ':d': request.form['duration'],
                    ':i': request.form['image'], ':tr': request.form['trailer'],
                    ':p': Decimal(str(price)), ':r': Decimal(str(rating)),
                    ':th': request.form['theater'], ':a': request.form['address'],
                    ':desc': request.form['description']
                }
            )
        
        flash('Movie updated successfully!', 'success')
    except Exception as e:
        print(f"Edit Movie Error: {e}")
        flash('Error updating movie', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_movie/<movie_id>')
def delete_movie(movie_id):
    """Delete movie"""
    global movies
    
    if 'user' not in session or not session.get('user', {}).get('is_admin'): 
        return redirect(url_for('login'))
    
    try:
        if USE_DYNAMODB:
            movies_table.delete_item(Key={'movie_id': movie_id})
        
        # Also remove from in-memory
        movies = [m for m in movies if m.get('movie_id') != movie_id]
        
        flash('Movie deleted', 'success')
    except Exception as e:
        print(f"Delete Movie Error: {e}")
        flash('Error deleting movie', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# --- SEED INITIAL DATA ---
# Add some sample movies if using in-memory storage
if not USE_DYNAMODB and not movies:
    movies = [
        {
            'movie_id': str(uuid.uuid4()),
            'title': 'Pathaan',
            'genre': 'Action',
            'language': 'Hindi',
            'duration': 146,
            'image': 'https://m.media-amazon.com/images/M/MV5BMzdjNmQxZjYtNjAyMS00NGY2LWE4YzgtMWQ2MWRmYjMxYzVmXkEyXkFqcGdeQXVyMTkzODUwNzk5._V1_.jpg',
            'trailer': 'https://youtube.com',
            'price': 350,
            'rating': 8.5,
            'theater': 'PVR Cinemas, MG Road',
            'address': 'MG Road, Bangalore',
            'description': 'An Indian spy embarks on a dangerous mission.'
        },
        {
            'movie_id': str(uuid.uuid4()),
            'title': 'Jawan',
            'genre': 'Action',
            'language': 'Hindi',
            'duration': 165,
            'image': 'https://m.media-amazon.com/images/M/MV5BODQ2NDQ4NDEtNTQxOS00NzAxLTgwMjUtMDI1N2FjYjMzYjYmXkEyXkFqcGdeQXVyMTUzNTgzNzM0._V1_.jpg',
            'trailer': 'https://youtube.com',
            'price': 350,
            'rating': 8.7,
            'theater': 'INOX, Forum',
            'address': 'Forum Mall, Bangalore',
            'description': 'A high-octane action thriller.'
        },
        {
            'movie_id': str(uuid.uuid4()),
            'title': 'Dunki',
            'genre': 'Comedy',
            'language': 'Hindi',
            'duration': 147,
            'image': 'https://m.media-amazon.com/images/M/MV5BY2RmMTk1MGEtZDg0NS00NThlLWE3NzAtM2M4NDE4MjM1YzE5XkEyXkFqcGdeQXVyMTUzNDQ4Mzk5._V1_.jpg',
            'trailer': 'https://youtube.com',
            'price': 300,
            'rating': 7.8,
            'theater': 'Cinepolis, Orion Mall',
            'address': 'Orion Mall, Bangalore',
            'description': 'A comedy-drama about illegal immigration.'
        },
        {
            'movie_id': str(uuid.uuid4()),
            'title': 'Animal',
            'genre': 'Action',
            'language': 'Hindi',
            'duration': 201,
            'image': 'https://m.media-amazon.com/images/M/MV5BMDBmYTgxYzItMzhhZi00NmRiLWIzMy1hNmFmMjQ1ZTE1NzYxXkEyXkFqcGdeQXVyMTUzNDQ4Mzk5._V1_.jpg',
            'trailer': 'https://youtube.com',
            'price': 400,
            'rating': 8.9,
            'theater': 'PVR Cinemas, Phoenix',
            'address': 'Phoenix Marketcity, Bangalore',
            'description': 'A transformation story.'
        },
        {
            'movie_id': str(uuid.uuid4()),
            'title': 'Oppenheimer',
            'genre': 'Drama',
            'language': 'English',
            'duration': 180,
            'image': 'https://m.media-amazon.com/images/M/MV5BMDBmYTgxYzItMzhhZi00NmRiLWIzMy1hNmFmMjQ1ZTE1NzYxXkEyXkFqcGdeQXVyMTkxNjUyNjc1._V1_.jpg',
            'trailer': 'https://youtube.com',
            'price': 500,
            'rating': 9.2,
            'theater': 'PVR Cinemas, Orbit',
            'address': 'Orbit Mall, Bangalore',
            'description': 'The story of atomic bomb creator.'
        },
        {
            'movie_id': str(uuid.uuid4()),
            'title': 'Leo',
            'genre': 'Action',
            'language': 'Tamil',
            'duration': 165,
            'image': 'https://m.media-amazon.com/images/M/MV5BMjkxMzM5NjUtNmZjNi00NzkyLWI2OGQtZjMxMDJhYjcyZjc4XkEyXkFqcGdeQXVyMTAzMDg4NzE0._V1_.jpg',
            'trailer': 'https://youtube.com',
            'price': 350,
            'rating': 8.4,
            'theater': 'Asian Cineverse',
            'address': 'Whitefield, Bangalore',
            'description': 'A cafe owner gets caught in danger.'
        }
    ]
    print(f"✅ Loaded {len(movies)} sample movies (in-memory)")



if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=True)










