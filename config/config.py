import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'superclaveultrasecreta123'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'finanzas.db'
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Pagination settings
    ITEMS_PER_PAGE = 20
    
    # Default limits for queries
    DEFAULT_RECENT_ITEMS_LIMIT = 5
    DEFAULT_TOP_CATEGORIES_LIMIT = 5
    
    # Date format
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    # Override SECRET_KEY to require it in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    
    def __init__(self):
        super().__init__()
        if not self.SECRET_KEY:
            print("WARNING: No SECRET_KEY set for production. Please set the SECRET_KEY environment variable.")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_NAME = ':memory:'  # Use in-memory database for tests

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}