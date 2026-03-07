"""
Configuration for Movie Magic Application
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'moviemagic-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///moviemagic.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    
    # DynamoDB Tables
    DYNAMODB_TABLE_USERS = os.environ.get('DYNAMODB_TABLE_USERS', 'MovieMagicUsers')
    DYNAMODB_TABLE_MOVIES = os.environ.get('DYNAMODB_TABLE_MOVIES', 'MovieMagicMovies')
    DYNAMODB_TABLE_BOOKINGS = os.environ.get('DYNAMODB_TABLE_BOOKINGS', 'MovieMagicBookings')
    
    # SNS Configuration
    SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

