from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="root123",
    database="moviemagic"
)
cursor = db.cursor(dictionary=True)

# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        values = (request.form['name'], request.form['email'], request.form['password'])
        cursor.execute(sql, values)
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and user['password'] == password:   # replace with hashed check in production
            # Store user info in session
            session['user_id'] = user['user_id']
            session['user'] = user['username']   # ✅ this is what shows in "Welcome, ..."
            session['email'] = user['email']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/home')
def home():
    # Fetch movies and bookings
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    cursor.execute("SELECT * FROM bookings WHERE user_id=%s", (session['user_id'],))
    bookings = cursor.fetchall()

    return render_template('home.html', user=session['user'], movies=movies, bookings=bookings)

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('movie', '')
        cursor.execute("SELECT * FROM movies WHERE title LIKE %s", ("%" + query + "%",))
        movies = cursor.fetchall()
        return render_template('search.html', movies=movies)
    return render_template('search.html', movies=[])

@app.route('/book/<int:movie_id>', methods=['GET','POST'])
def book(movie_id):
    cursor.execute("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
    movie = cursor.fetchone()

    # Example show times (could be stored in DB)
    movie['show_times'] = ["10:00 AM", "2:00 PM", "6:00 PM", "9:00 PM"]

    # Example theaters (replace with DB query if you have a theaters table)
    theaters = [
        {"name": "PVR Cinemas", "location": "City Center"},
        {"name": "INOX", "location": "Mall Road"},
        {"name": "Cinepolis", "location": "Downtown"}
    ]

    today = date.today().isoformat()

    if request.method == 'POST':
        sql = """INSERT INTO bookings (user_id, movie_id, seat_number, location, booking_date)
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (session['user_id'], movie_id, request.form['seats'],
                  request.form['address'], request.form['date'])
        cursor.execute(sql, values)
        db.commit()

        # Update available seats (reduce by number of seats booked)
        seats_booked = len(request.form['seats'].split(","))
        new_seats = movie['available_seats'] - seats_booked
        cursor.execute("UPDATE movies SET available_seats=%s WHERE movie_id=%s", (new_seats, movie_id))
        db.commit()

        return render_template('ticket.html',
                               title=movie['title'],
                               date=request.form['date'],
                               time=request.form['time'],
                               seats=request.form['seats'],
                               address=request.form['address'],
                               amount=request.form['amount'],
                               user=session['user'])
    return render_template('book.html', movie=movie, theaters=theaters, today=today)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)