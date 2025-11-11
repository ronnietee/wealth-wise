"""
Recurring allocation model for ongoing budget allocations.
"""

from datetime import datetime
from ..extensions import db


class RecurringBudgetAllocation(db.Model):
    """Recurring budget allocation model for ongoing budget allocations."""
    
    __tablename__ = 'recurring_budget_allocation'
    
    id = db.Column(db.Integer, primary_key=True)
    allocated_amount = db.Column(db.Float, default=0)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    period_type = db.Column(db.String(20), nullable=False, default='monthly')  # monthly, quarterly, yearly, custom
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='recurring_allocations')
    subcategory = db.relationship('Subcategory', backref='recurring_allocations')
    
    def __repr__(self):
        return f'<RecurringBudgetAllocation {self.allocated_amount}>'
