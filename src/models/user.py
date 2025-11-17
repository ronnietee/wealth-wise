"""
User model and related functionality.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash
from ..extensions import db


class User(db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    theme = db.Column(db.String(10), default='dark')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Subscription/trial fields
    trial_start = db.Column(db.DateTime, nullable=True)
    trial_end = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(30), default='trial')  # trial, active, past_due, cancelled, inactive
    subscription_plan = db.Column(db.String(20), nullable=True)  # monthly, yearly
    next_billing_at = db.Column(db.DateTime, nullable=True)
    auto_renew = db.Column(db.Boolean, default=True)
    payfast_token = db.Column(db.String(255), nullable=True)
    payfast_subscription_id = db.Column(db.String(255), nullable=True)
    billing_currency = db.Column(db.String(10), default='ZAR')
    
    # Onboarding fields (optional for existing users)
    country = db.Column(db.String(100), nullable=True, default=None)
    preferred_name = db.Column(db.String(100), nullable=True, default=None)
    referral_source = db.Column(db.String(100), nullable=True, default=None)
    referral_details = db.Column(db.Text, nullable=True, default=None)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Legal acceptance fields
    terms_accepted = db.Column(db.Boolean, default=False, nullable=False)
    privacy_policy_accepted = db.Column(db.Boolean, default=False, nullable=False)
    terms_accepted_at = db.Column(db.DateTime, nullable=True)
    privacy_policy_accepted_at = db.Column(db.DateTime, nullable=True)
    terms_version = db.Column(db.String(50), nullable=True)
    privacy_policy_version = db.Column(db.String(50), nullable=True)
    
    # Admin fields
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    budget_periods = db.relationship('BudgetPeriod', backref='user', lazy=True, cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash for the user."""
        self.password_hash = generate_password_hash(password)
    
    def __repr__(self):
        return f'<User {self.username}>'
