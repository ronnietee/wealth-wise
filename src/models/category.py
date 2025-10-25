"""
Category and Subcategory models for organizing transactions.
"""

from datetime import datetime
from ..extensions import db


class Category(db.Model):
    """Category model for organizing transactions."""
    
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_template = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategories = db.relationship('Subcategory', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Subcategory(db.Model):
    """Subcategory model for detailed transaction categorization."""
    
    __tablename__ = 'subcategory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships are defined in Category model
    
    def __repr__(self):
        return f'<Subcategory {self.name}>'
