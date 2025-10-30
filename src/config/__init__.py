"""
Configuration management for the Wealth Wise application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///wealthwise.db')
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@steward.com')
    
    # Application configuration
    APP_NAME = 'STEWARD'

    # Subscription and billing
    SUBSCRIPTIONS_ENABLED = os.environ.get('SUBSCRIPTIONS_ENABLED', 'true').lower() in ['true', 'on', '1']
    ENFORCE_PAYMENT_AFTER_TRIAL = os.environ.get('ENFORCE_PAYMENT_AFTER_TRIAL', 'false').lower() in ['true', 'on', '1']
    TRIAL_DAYS = int(os.environ.get('TRIAL_DAYS', 30))
    DEFAULT_CURRENCY = os.environ.get('DEFAULT_CURRENCY', 'ZAR')

    # PayFast configuration
    PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID', '')
    PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY', '')
    PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE', '')  # recommended in production
    PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'true').lower() in ['true', 'on', '1']
    PAYFAST_RETURN_URL = os.environ.get('PAYFAST_RETURN_URL', 'http://localhost:5000/payfast/return')
    PAYFAST_CANCEL_URL = os.environ.get('PAYFAST_CANCEL_URL', 'http://localhost:5000/payfast/cancel')
    PAYFAST_NOTIFY_URL = os.environ.get('PAYFAST_NOTIFY_URL', 'http://localhost:5000/api/subscriptions/webhook/payfast')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///wealthwise_dev.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost/wealthwise')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
