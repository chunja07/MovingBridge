"""
Configuration settings for different environments
"""
import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Security headers
    TALISMAN_CONFIG = {
        'force_https': False,
        'strict_transport_security': True,
        'content_security_policy': {
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
            'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "fonts.googleapis.com"],
            'font-src': ["'self'", "fonts.gstatic.com"],
            'img-src': ["'self'", "data:", "*.googleusercontent.com"]
        }
    }

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movingbridge_dev.db'
    
    # Disable HTTPS enforcement for development
    WTF_CSRF_SSL_STRICT = False
    SESSION_COOKIE_SECURE = False
    
    # More lenient CSP for development
    TALISMAN_CONFIG = {
        'force_https': False,
        'strict_transport_security': False,
        'content_security_policy': False
    }

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Enable security features for production
    WTF_CSRF_SSL_STRICT = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Strict CSP for production
    TALISMAN_CONFIG = {
        'force_https': True,
        'strict_transport_security': True,
        'strict_transport_security_max_age': 31536000,
        'content_security_policy': {
            'default-src': "'self'",
            'script-src': ["'self'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
            'style-src': ["'self'", "cdn.jsdelivr.net", "fonts.googleapis.com"],
            'font-src': ["'self'", "fonts.gstatic.com"],
            'img-src': ["'self'", "data:"]
        }
    }

class TestConfig(Config):
    """Test environment configuration"""
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SSL_STRICT = False
    SESSION_COOKIE_SECURE = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])