"""
Category service for managing categories and subcategories.
"""

from ..extensions import db
from ..models import Category, Subcategory


class CategoryService:
    """Service for handling category operations."""
    
    @staticmethod
    def get_user_categories(user_id):
        """Get all categories for a user with allocation data."""
        from ..models import Budget, BudgetPeriod, BudgetAllocation
        
        categories = Category.query.filter_by(user_id=user_id).all()
        result = []
        
        # Get active budget allocations and spent amounts
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        allocations = {}
        spent_amounts = {}
        
        if active_period:
            budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
            if budget:
                # Get allocations
                budget_allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).all()
                for allocation in budget_allocations:
                    allocations[allocation.subcategory_id] = allocation.allocated_amount
                
                # Get spent amounts from transactions
                from ..models import Transaction
                transactions = Transaction.query.filter(
                    Transaction.user_id == user_id,
                    Transaction.transaction_date >= active_period.start_date,
                    Transaction.transaction_date <= active_period.end_date
                ).all()
                
                for transaction in transactions:
                    subcategory_id = transaction.subcategory_id
                    if subcategory_id not in spent_amounts:
                        spent_amounts[subcategory_id] = 0
                    # Only count negative amounts (expenses) as spent
                    if transaction.amount < 0:
                        spent_amounts[subcategory_id] += abs(transaction.amount)
        
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'is_template': category.is_template,
                'created_at': category.created_at.isoformat(),
                'subcategories': []
            }
            
            for subcategory in category.subcategories:
                allocated = allocations.get(subcategory.id, 0)
                spent = spent_amounts.get(subcategory.id, 0)
                balance = allocated - spent
                
                subcategory_data = {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'created_at': subcategory.created_at.isoformat(),
                    'allocated': allocated,
                    'spent': spent,
                    'balance': balance
                }
                category_data['subcategories'].append(subcategory_data)
            
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
        """Delete a subcategory and handle related data."""
        try:
            subcategory = Subcategory.query.get(subcategory_id)
            if not subcategory:
                return False
            
            # Delete related budget allocations first
            from ..models import BudgetAllocation, RecurringBudgetAllocation
            BudgetAllocation.query.filter_by(subcategory_id=subcategory_id).delete()
            RecurringBudgetAllocation.query.filter_by(subcategory_id=subcategory_id).delete()
            
            # Delete related transactions
            from ..models import Transaction
            Transaction.query.filter_by(subcategory_id=subcategory_id).delete()
            
            # Now delete the subcategory
            db.session.delete(subcategory)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting subcategory {subcategory_id}: {str(e)}")
            db.session.rollback()
            return False
