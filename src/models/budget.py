"""
Budget-related models for financial planning.
"""

from datetime import datetime
from ..extensions import db


class BudgetPeriod(db.Model):
    """Budget period model for organizing budgets by time periods."""
    
    __tablename__ = 'budget_period'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "January 2024", "Q1 2024", "Custom Budget"
    period_type = db.Column(db.String(20), nullable=False)  # 'monthly', 'quarterly', 'yearly', 'custom'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Only one active budget period per user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    budgets = db.relationship('Budget', backref='period', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BudgetPeriod {self.name}>'


class Budget(db.Model):
    """Budget model for financial planning."""
    
    __tablename__ = 'budget'
    
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('budget_period.id'), nullable=False)
    total_income = db.Column(db.Float, default=0)
    balance_brought_forward = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('BudgetAllocation', backref='budget', lazy=True, cascade='all, delete-orphan')
    income_sources = db.relationship('IncomeSource', backref='budget', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Budget {self.id}>'


class BudgetAllocation(db.Model):
    """Budget allocation model for assigning budget amounts to categories."""
    
    __tablename__ = 'budget_allocation'
    
    id = db.Column(db.Integer, primary_key=True)
    allocated_amount = db.Column(db.Float, default=0)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    
    # Relationships
    subcategory = db.relationship('Subcategory', backref='budget_allocations', lazy=True)
    
    def __repr__(self):
        return f'<BudgetAllocation {self.allocated_amount}>'
