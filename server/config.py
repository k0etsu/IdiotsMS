"""
Configuration settings for the IdiotsMS Account Management Flask application
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * int(os.getenv('JWT_EXPIRES_IN_DAYS', 7))  # days to seconds

    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'idiotsms_accounts')

    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = f"{os.getenv('RATE_LIMIT_MAX_REQUESTS', '100')}/{int(os.getenv('RATE_LIMIT_WINDOW_MS', '900000'))//1000} seconds"

    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000'] if os.getenv('NODE_ENV') != 'production' else ['https://yourdomain.com']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
