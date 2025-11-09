"""
Income source models for tracking income.
"""

from datetime import datetime
from ..extensions import db


class IncomeSource(db.Model):
    """Income source model for budget periods."""
    
    __tablename__ = 'income_source'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    is_recurring_source = db.Column(db.Boolean, default=False)
    recurring_source_id = db.Column(db.Integer, db.ForeignKey('recurring_income_source.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<IncomeSource {self.name}: {self.amount}>'


class RecurringIncomeSource(db.Model):
    """Recurring income source model for ongoing income tracking."""
    
    __tablename__ = 'recurring_income_source'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    period_type = db.Column(db.String(20), nullable=False, default='monthly')  # monthly, quarterly, yearly, custom
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='recurring_income_sources')
    
    def __repr__(self):
        return f'<RecurringIncomeSource {self.name}: {self.amount}>'
