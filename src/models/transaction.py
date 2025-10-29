"""
Transaction model for financial transactions.
"""

from datetime import datetime
from ..extensions import db


class Transaction(db.Model):
    """Transaction model for recording financial transactions."""
    
    __tablename__ = 'transaction'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    comment = db.Column(db.Text)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategory = db.relationship('Subcategory', backref='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount}>'
