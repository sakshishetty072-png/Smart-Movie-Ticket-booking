"""
Seed script to populate DynamoDB with sample movies
Run this script to add sample movies to the database
"""

import boto3
from decimal import Decimal
import uuid

# AWS Configuration
AWS_REGION = 'ap-south-1'
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
movies_table = dynamodb.Table('MovieMagic_Movies')

# Sample Movies Data
sample_movies = [
    {
        'movie_id': str(uuid.uuid4()),
        'title': 'Pathaan',
        'genre': 'Action',
        'language': 'Hindi',
        'duration': 146,
        'image': 'https://m.media-amazon.com/images/M/MV5BMzdjNmQxZjYtNjAyMS00NGY2LWE4YzgtMWQ2MWRmYjMxYzVmXkEyXkFqcGdeQXVyMTkzODUwNzk5._V1_.jpg',
        'trailer': 'https://youtube.com',
        'price': Decimal(350),
        'rating': Decimal(8.5),
        'theater': 'PVR Cinemas, MG Road',
        'address': 'MG Road, Bangalore',
        'description': 'An Indian spy embarks on a dangerous mission to track down a terrorist.'
    },
    {
        'movie_id': str(uuid.uuid4()),
        'title': 'Jawan',
        'genre': 'Action',
        'language': 'Hindi',
        'duration': 165,
        'image': 'https://m.media-amazon.com/images/M/MV5BODQ2NDQ4NDEtNTQxOS00NzAxLTgwMjUtMDI1N2FjYjMzYjYmXkEyXkFqcGdeQXVyMTUzNTgzNzM0._V1_.jpg',
        'trailer': 'https://youtube.com',
        'price': Decimal(350),
        'rating': Decimal(8.7),
        'theater': 'INOX, Forum',
        'address': 'Forum Mall, Bangalore',
        'description': 'A high-octane action thriller with a personal vendetta.'
    },
    {
        'movie_id': str(uuid.uuid4()),
        'title': 'Dunki',
        'genre': 'Comedy',
        'language': 'Hindi',
        'duration': 147,
        'image': 'https://m.media-amazon.com/images/M/MV5BY2RmMTk1MGEtZDg0NS00NThlLWE3NzAtM2M4NDE4MjM1YzE5XkEyXkFqcGdeQXVyMTUzNDQ4Mzk5._V1_.jpg',
        'trailer': 'https://youtube.com',
        'price': Decimal(300),
        'rating': Decimal(7.8),
        'theater': 'Cinepolis, Orion Mall',
        'address': 'Orion Mall, Bangalore',
        'description': 'A comedy-drama about illegal immigration journey.'
    },
    {
        'movie_id': str(uuid.uuid4()),
        'title': 'Animal',
        'genre': 'Action',
        'language': 'Hindi',
        'duration': 201,
        'image': 'https://m.media-amazon.com/images/M/MV5BMDBmYTgxYzItMzhhZi00NmRiLWIzMy1hNmFmMjQ1ZTE1NzYxXkEyXkFqcGdeQXVyMTUzNDQ4Mzk5._V1_.jpg',
        'trailer': 'https://youtube.com',
        'price': Decimal(400),
        'rating': Decimal(8.9),
        'theater': 'PVR Cinemas, Phoenix',
        'address': 'Phoenix Marketcity, Bangalore',
        'description': 'A son undergoes transformation after father goes missing.'
    },
    {
        'movie_id': str(uuid.uuid4()),
        'title': 'Salaar',
        'genre': 'Action',
        'language': 'Telugu',
        'duration': 175,
        'image': 'https://m.media-amazon.com/images/M/MV5BM2I0YTFjOTUtMzMwNi00YzQyLWFhNDAtZGFiNTk4YjNlNjZkXkEyXkFqcGdeQXVyMTY3ODkyNDk4._V1_.jpg',
        'trailer': 'https://youtube.com',
        'price': Decimal(350),
        'rating': Decimal(8.3),
        'theater': 'Sri Venkateswara Cinemas',
        'address': 'Jayanagar, Bangalore',
        'description': 'Action drama about bond between two childhood friends.'
    },
    {
        'movie_id': str(uuid.uuid4()),
        'title': 'Oppenheimer',
        'genre': 'Drama',
        'language': 'English',
        'duration': 180,
        'image': 'https://m.media-amazon.com/images/M/MV5BMDBmYTgxYzItMzhhZi00NmRiLWIzMy1hNmFmMjQ1ZTE1NzYxXkEyXkFqcGdeQXVyMTkxNjUyNjc1._V1_.jpg',
        'trailer': 'https://youtube.com',
        'price': Decimal(500),
        'rating': Decimal(9.2),
        'theater': 'PVR Cinemas, Orbit',
        'address': 'Orbit Mall, Bangalore',
        'description': 'Story of American scientist Oppenheimer and atomic bomb.'
    }
]

def seed_movies():
    """Add sample movies to DynamoDB"""
    print("Seeding movies to DynamoDB...")
    
    for movie in sample_movies:
        try:
            movies_table.put_item(Item=movie)
            print(f"Added: {movie['title']}")
        except Exception as e:
            print(f"Error adding {movie['title']}: {e}")
    
    print("\nSeeding completed!")
    print(f"Total movies added: {len(sample_movies)}")

if __name__ == '__main__':
    seed_movies()

