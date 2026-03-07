"""
Database Seeder for Movie Magic
Run this script to add sample movies and shows to the database
"""

from app import create_app, db
from app.models import Movie, Show
from datetime import date, time, timedelta
import uuid

def seed_database():
    """Seed the database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        Show.query.delete()
        Movie.query.delete()
        db.session.commit()
        
        print("Seeding database with sample movies...")
        
        # Sample movies
        movies = [
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Pathaan",
                description="An Indian RAW agent goes on a mission to stop a terrorist who has links with a rogue scientist from causing a huge devastation.",
                genre="Action",
                duration=146,
                rating=8.5,
                poster_url="https://upload.wikimedia.org/wikipedia/en/e/ed/Pathaan_%28film%29.jpg",
                release_date=date(2023, 1, 25),
                location="Mumbai"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Jawan",
                description="A man is on a mission to deliver justice to the ones responsible for the chaos faced by the nation.",
                genre="Action",
                duration=165,
                rating=8.2,
                poster_url="https://upload.wikimedia.org/wikipedia/en/9/95/Jawan_film.jpg",
                release_date=date(2023, 9, 7),
                location="Delhi"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Dunki",
                description="A group of friends use an illegal immigration route to travel from India to Canada, hoping to find a better life.",
                genre="Comedy",
                duration=132,
                rating=7.8,
                poster_url="https://upload.wikimedia.org/wikipedia/en/7/77/Dunki_film.jpg",
                release_date=date(2023, 12, 21),
                location="Bangalore"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Animal",
                description="The story revolves around a family of four, where the youngest son goes on a path of self-destruction after a traumatic childhood.",
                genre="Drama",
                duration=201,
                rating=8.0,
                poster_url="https://upload.wikimedia.org/wikipedia/en/7/75/Animal_film.jpg",
                release_date=date(2023, 12, 1),
                location="Mumbai"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Salaar: Part 1",
                description="A bloodied man tells his story, tracing back his connection to a city called Khansaar and to a man named Deva.",
                genre="Action",
                duration=175,
                rating=8.0,
                poster_url="https://upload.wikimedia.org/wikipedia/en/7/77/Salaar_film.jpg",
                release_date=date(2023, 12, 22),
                location="Hyderabad"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Oppenheimer",
                description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                genre="Biography",
                duration=180,
                rating=9.0,
                poster_url="https://upload.wikimedia.org/wikipedia/en/4/4a/Oppenheimer_%28film%29.jpg",
                release_date=date(2023, 7, 21),
                location="Chennai"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Barbie",
                description="Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land.",
                genre="Comedy",
                duration=114,
                rating=7.5,
                poster_url="https://upload.wikimedia.org/wikipedia/en/3/3e/Barbie_%28film%29.jpg",
                release_date=date(2023, 7, 21),
                location="Mumbai"
            ),
            Movie(
                movie_id=str(uuid.uuid4())[:8],
                title="Leo",
                description="A man is drawn into the world of crime when his peaceful life is disrupted by a dangerous gang.",
                genre="Action",
                duration=164,
                rating=7.6,
                poster_url="https://upload.wikimedia.org/wikipedia/en/2/2e/Leo_%282023_film%29.jpg",
                release_date=date(2023, 10, 19),
                location="Chennai"
            ),
        ]
        
        # Add movies to database
        for movie in movies:
            db.session.add(movie)
        
        db.session.commit()
        print(f"Added {len(movies)} movies")
        
        # Add showtimes for each movie
        print("Adding showtimes...")
        show_count = 0
        
        for movie in Movie.query.all():
            # Add 2-3 shows per movie for the next few days
            for day_offset in range(1, 4):
                show_date = date.today() + timedelta(days=day_offset)
                
                # Morning show
                show1 = Show(
                    show_id=str(uuid.uuid4())[:8],
                    movie_id=movie.id,
                    show_date=show_date,
                    show_time=time(10, 30),
                    venue="PVR Cinemas " + movie.location,
                    total_seats=100,
                    available_seats=100,
                    price=250.0
                )
                db.session.add(show1)
                show_count += 1
                
                # Evening show
                show2 = Show(
                    show_id=str(uuid.uuid4())[:8],
                    movie_id=movie.id,
                    show_date=show_date,
                    show_time=time(18, 30),
                    venue="PVR Cinemas " + movie.location,
                    total_seats=100,
                    available_seats=100,
                    price=350.0
                )
                db.session.add(show2)
                show_count += 1
                
                # Night show
                if movie.rating >= 8.0:  # Only for high-rated movies
                    show3 = Show(
                        show_id=str(uuid.uuid4())[:8],
                        movie_id=movie.id,
                        show_date=show_date,
                        show_time=time(21, 30),
                        venue="PVR Cinemas " + movie.location,
                        total_seats=100,
                        available_seats=100,
                        price=400.0
                    )
                    db.session.add(show3)
                    show_count += 1
        
        db.session.commit()
        print(f"Added {show_count} showtimes")
        
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print(f"Total Movies: {Movie.query.count()}")
        print(f"Total Shows: {Show.query.count()}")

if __name__ == '__main__':
    seed_database()

