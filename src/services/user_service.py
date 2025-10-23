"""
User service for user management operations.
"""

from datetime import datetime
from ..extensions import db
from ..models import User
from ..utils.categories import create_default_categories


class UserService:
    """Service for handling user operations."""
    
    @staticmethod
    def create_user(username, email, password, first_name, last_name, **kwargs):
        """Create a new user."""
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"
        
        if User.query.filter_by(username=username).first():
            return None, "Username already taken"
        
        # Create user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default categories
        create_default_categories(user.id)
        
        return user, None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username."""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def update_user_settings(user, **kwargs):
        """Update user settings."""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """Change user password."""
        from werkzeug.security import check_password_hash
        
        if not check_password_hash(user.password_hash, old_password):
            return False, "Current password is incorrect"
        
        user.set_password(new_password)
        db.session.commit()
        return True, None
    
    @staticmethod
    def delete_user(user):
        """Delete user and all associated data."""
        try:
            db.session.delete(user)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def reset_user_data(user):
        """Reset all user data except account."""
        try:
            # Delete in correct order to respect foreign key constraints
            from ..models import (
                Transaction, BudgetAllocation, IncomeSource, Budget, 
                BudgetPeriod, Category, Subcategory, RecurringIncomeSource,
                RecurringBudgetAllocation, Account
            )
            
            # Delete transactions
            Transaction.query.filter_by(user_id=user.id).delete()
            
            # Delete budget allocations
            BudgetAllocation.query.join(Budget).filter(Budget.user_id == user.id).delete()
            
            # Delete income sources
            IncomeSource.query.join(Budget).filter(Budget.user_id == user.id).delete()
            
            # Delete budgets
            Budget.query.filter_by(user_id=user.id).delete()
            
            # Delete budget periods
            BudgetPeriod.query.filter_by(user_id=user.id).delete()
            
            # Delete subcategories
            Subcategory.query.join(Category).filter(Category.user_id == user.id).delete()
            
            # Delete categories
            Category.query.filter_by(user_id=user.id).delete()
            
            # Delete recurring income sources
            RecurringIncomeSource.query.filter_by(user_id=user.id).delete()
            
            # Delete recurring allocations
            RecurringBudgetAllocation.query.filter_by(user_id=user.id).delete()
            
            # Keep accounts but reset balances
            Account.query.filter_by(user_id=user.id).update({'current_balance': 0})
            
            db.session.commit()
            
            # Recreate default categories
            create_default_categories(user.id)
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
