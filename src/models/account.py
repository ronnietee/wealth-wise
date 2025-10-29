"""
Account model for tracking different financial accounts.
"""

from datetime import datetime
from ..extensions import db


class Account(db.Model):
    """Account model for tracking different financial accounts."""
    
    __tablename__ = 'account'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # 'checking', 'savings', 'credit', 'investment', 'cash', 'other'
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))  # Last 4 digits or masked
    current_balance = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Account {self.name}: {self.account_type}>'
