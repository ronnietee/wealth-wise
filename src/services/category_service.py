"""
Category service for managing categories and subcategories.
"""

from ..extensions import db
from ..models import Category, Subcategory


class CategoryService:
    """Service for handling category operations."""
    
    @staticmethod
    def get_user_categories(user_id):
        """Get all categories for a user."""
        categories = Category.query.filter_by(user_id=user_id).all()
        result = []
        
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'is_template': category.is_template,
                'created_at': category.created_at.isoformat(),
                'subcategories': []
            }
            
            for subcategory in category.subcategories:
                category_data['subcategories'].append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'created_at': subcategory.created_at.isoformat()
                })
            
            result.append(category_data)
        
        return result
    
    @staticmethod
    def create_category(user_id, name, is_template=False):
        """Create a new category."""
        category = Category(
            name=name,
            user_id=user_id,
            is_template=is_template
        )
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def create_subcategory(category_id, name):
        """Create a new subcategory."""
        subcategory = Subcategory(
            name=name,
            category_id=category_id
        )
        db.session.add(subcategory)
        db.session.commit()
        return subcategory
    
    @staticmethod
    def update_category(category_id, user_id, name):
        """Update a category."""
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            return None
        
        category.name = name
        db.session.commit()
        return category
    
    @staticmethod
    def update_subcategory(subcategory_id, name):
        """Update a subcategory."""
        subcategory = Subcategory.query.get(subcategory_id)
        if not subcategory:
            return None
        
        subcategory.name = name
        db.session.commit()
        return subcategory
    
    @staticmethod
    def delete_category(category_id, user_id):
        """Delete a category and all its subcategories."""
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            return False
        
        db.session.delete(category)
        db.session.commit()
        return True
    
    @staticmethod
    def delete_subcategory(subcategory_id):
        """Delete a subcategory."""
        subcategory = Subcategory.query.get(subcategory_id)
        if not subcategory:
            return False
        
        db.session.delete(subcategory)
        db.session.commit()
        return True
