# Movie Magic - Smart Movie Ticket Booking System

A cloud-based movie ticket booking application built with Flask, AWS EC2, DynamoDB, and SNS.

## Features

- **User Authentication**: Register, login, and profile management
- **Movie Browsing**: Search and filter movies by location and genre
- **Interactive Seat Selection**: Visual seat layout for choosing seats
- **Payment Gateway**: Secure payment with Card, UPI, Net Banking, Wallet
- **Real-time Booking**: Instant booking confirmation with AWS SNS
- **Booking History**: View and manage past bookings
- **Cloud-native**: Deployed on AWS EC2 with DynamoDB storage

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / AWS DynamoDB (production)
- **Notifications**: AWS SNS
- **Cloud**: AWS EC2
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript

## Project Structure

```
moviemagic/
├── app/
│   ├── __init__.py       # Application factory
│   ├── models.py         # Database models
│   ├── utils.py          # Utility functions
│   ├── routes/          # Route blueprints
│   │   ├── auth.py      # Authentication routes
│   │   ├── main.py      # Main routes
│   │   └── booking.py   # Booking routes
│   ├── services/        # AWS services
│   │   ├── dynamodb_service.py
│   │   └── sns_service.py
│   └── templates/       # HTML templates
├── templates/          # Frontend templates
├── movies_data.py      # Movie data
├── run_app.py          # Application entry point
├── seed_data.py        # Database seeder
└── requirements.txt    # Python dependencies
```

## Setup

### Prerequisites

- Python 3.8+
- AWS Account (for production)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

5. Run the database seeder:
   ```bash
   python seed_data.py
   ```

6. Run the application:
   ```bash
   python run_app.py
   ```

7. Open http://localhost:5000 in your browser

## AWS Configuration

### DynamoDB Tables

Create the following tables in DynamoDB:

1. **MovieMagicUsers**
   - Primary Key: UserID (String)

2. **MovieMagicMovies**
   - Primary Key: MovieID (String)

3. **MovieMagicBookings**
   - Primary Key: BookingID (String)

### SNS Topic

1. Create an SNS topic for booking notifications
2. Note the Topic ARN
3. Add the ARN to your `.env` file

### IAM Permissions

Create an IAM user with the following permissions:
- DynamoDB read/write access
- SNS publish access

## Deployment on EC2

### 1. Launch EC2 Instance

- Choose Ubuntu 20.04 LTS
- Configure security groups (HTTP, HTTPS, SSH)

### 2. Install Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### 3. Deploy Application

```bash
# Clone repository
git clone <your-repo>
cd moviemagic

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env
```

### 4. Configure Gunicorn and Nginx

Create systemd service file for Gunicorn and configure Nginx as reverse proxy.

### 5. Start Services

```bash
sudo systemctl start moviemagic
sudo systemctl enable moviemagic
```

## Usage

1. Register a new account
2. Browse movies on the homepage
3. Select a movie and choose showtime
4. Select seats from the interactive layout
5. Complete payment (Card/UPI/Net Banking/Wallet)
6. Receive confirmation via email/SMS

## Screenshots

- Home page with featured movies
- Movie listing with genre/location filters
- Interactive seat selection
- Payment gateway
- Booking confirmation

## License

MIT License

## Author

Movie Magic Team

## Acknowledgments

- Flask Documentation
- AWS Documentation
- Bootstrap 5

