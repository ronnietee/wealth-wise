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
        from ..models import Budget, BudgetPeriod, BudgetAllocation, RecurringBudgetAllocation
        
        categories = Category.query.filter_by(user_id=user_id).all()
        result = []
        
        # Get active budget allocations and spent amounts
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        allocations = {}
        spent_amounts = {}
        
        # Get all active recurring allocations to check if a subcategory has a recurring allocation
        recurring_allocations = RecurringBudgetAllocation.query.filter_by(
            user_id=user_id, 
            is_active=True
        ).all()
        subcategory_has_recurring = {alloc.subcategory_id: True for alloc in recurring_allocations}
        
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
                # Check if this subcategory has an active recurring allocation
                is_recurring = subcategory_has_recurring.get(subcategory.id, False)
                
                subcategory_data = {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'created_at': subcategory.created_at.isoformat(),
                    'allocated': allocated,
                    'spent': spent,
                    'balance': balance,
                    'is_recurring_allocation': is_recurring
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
    
    @staticmethod
    def create_onboarding_categories(user_id, categories, subcategories, custom_category_names, custom_subcategory_names):
        """Create categories and subcategories from onboarding data."""
        # Define the category mapping (same as in original app)
        category_mapping = {
            'faithful-stewardship': {
                'name': 'Giving',
                'subcategories': {
                    'tithe': 'Tithe',
                    'offering': 'Offering',
                    'social-responsibility': 'Social Responsibility'
                }
            },
            'groceries': {
                'name': 'Groceries',
                'subcategories': {
                    'food-home-essentials': 'Food & Home Essentials',
                    'dining-out': 'Dining out'
                }
            },
            'housing': {
                'name': 'Housing',
                'subcategories': {
                    'mortgage-rent': 'Mortgage/Rent',
                    'hoa-fees-levies': 'HOA Fees/Levies',
                    'electricity-bill': 'Electricity Bill',
                    'water-bill': 'Water Bill',
                    'home-maintenance': 'Home maintenance',
                    'home-insurance': 'Home Insurance',
                    'internet': 'Internet'
                }
            },
            'transportation': {
                'name': 'Transportation',
                'subcategories': {
                    'loan-repayment': 'Loan repayment',
                    'insurance': 'Insurance',
                    'fuel': 'Fuel',
                    'car-tracker': 'Car Tracker',
                    'car-wash': 'Car wash'
                }
            },
            'monthly-commitments': {
                'name': 'Monthly Commitments',
                'subcategories': {
                    'life-cover': 'Life cover',
                    'funeral-plan': 'Funeral Plan',
                    'credit-card-repayment': 'Credit card repayment',
                    'monthly-banking-fees': 'Monthly Banking Fees'
                }
            },
            'leisure-entertainment': {
                'name': 'Leisure/Entertainment',
                'subcategories': {
                    'spotify': 'Spotify',
                    'weekend-adventures': 'Weekend adventures'
                }
            },
            'personal-care': {
                'name': 'Personal Care',
                'subcategories': {
                    'gym-membership': 'Gym membership',
                    'haircuts': 'Haircuts',
                    'clothing': 'Clothing'
                }
            },
            'savings-goals': {
                'name': 'Savings Goals',
                'subcategories': {
                    'emergency-fund': 'Emergency fund',
                    'general-savings': 'General Savings',
                    'short-term-goal': 'Short term goal'
                }
            },
            'once-off-expenses': {
                'name': 'Once-off expenses (populated as it happens)',
                'subcategories': {
                    'asset-purchase': 'Asset purchase',
                    'emergency': 'Emergency'
                }
            }
        }
        
        # Group custom subcategories by their parent category
        custom_category_subcategories = {}
        for subcategory_key in subcategories:
            if subcategory_key.startswith('custom-subcategory-'):
                parts = subcategory_key.split('-')
                if len(parts) >= 4:
                    if parts[2] == 'custom' and len(parts) >= 5:
                        parent_category_id = f"{parts[2]}-{parts[3]}-{parts[4]}"
                    else:
                        parent_category_id = parts[2]
                    
                    if parent_category_id not in custom_category_subcategories:
                        custom_category_subcategories[parent_category_id] = []
                    custom_category_subcategories[parent_category_id].append(subcategory_key)
        
        # Process each selected category
        for category_key in categories:
            if category_key in category_mapping:
                # Handle predefined categories
                category_data = category_mapping[category_key]
                category = Category(
                    name=category_data['name'],
                    user_id=user_id,
                    is_template=True
                )
                db.session.add(category)
                db.session.flush()
                
                # Add selected subcategories for this category (both predefined and custom)
                for subcategory_key in subcategories:
                    if subcategory_key in category_data['subcategories']:
                        # Predefined subcategory
                        subcategory = Subcategory(
                            name=category_data['subcategories'][subcategory_key],
                            category_id=category.id
                        )
                        db.session.add(subcategory)
                    elif subcategory_key.startswith(f'custom-subcategory-{category_key}-'):
                        # Custom subcategory under a predefined category
                        subcategory_name = custom_subcategory_names.get(subcategory_key, f"Custom Subcategory {subcategory_key.split('-')[-1]}")
                        # Only add if not already added (avoid duplicates from custom_category_subcategories)
                        subcategory = Subcategory(
                            name=subcategory_name,
                            category_id=category.id
                        )
                        db.session.add(subcategory)
                        
            elif category_key.startswith('custom-category-'):
                # Handle custom categories
                custom_category_name = custom_category_names.get(category_key, f'Custom Category {category_key.split("-")[-1]}')
                
                category = Category(
                    name=custom_category_name,
                    user_id=user_id,
                    is_template=False
                )
                db.session.add(category)
                db.session.flush()
                
                # Add subcategories for this custom category
                # First get the numeric part after 'custom-category-'
                category_number = category_key.split('-')[-1]
                matching_custom_subcategory_keys = []
                
                # Find all custom subcategories that belong to this custom category
                # Pattern: custom-subcategory-custom-category-{number}-{counter}
                # Example: custom-subcategory-custom-category-1-2
                for subcategory_key in subcategories:
                    # Check if this subcategory belongs to our custom category
                    if subcategory_key.startswith(f'custom-subcategory-custom-category-{category_number}-'):
                        matching_custom_subcategory_keys.append(subcategory_key)
                
                # Also check the grouped custom_category_subcategories (if it exists)
                if category_key in custom_category_subcategories:
                    # Only add if not already in matching keys to avoid duplicates
                    for sub_key in custom_category_subcategories[category_key]:
                        if sub_key not in matching_custom_subcategory_keys:
                            matching_custom_subcategory_keys.append(sub_key)
                
                # Add the found subcategories (avoid duplicates by using set or checking)
                added_names = set()
                for subcategory_key in matching_custom_subcategory_keys:
                    subcategory_name = custom_subcategory_names.get(subcategory_key, f"Custom Subcategory {subcategory_key.split('-')[-1]}")
                    # Avoid adding duplicate subcategories with the same name
                    if subcategory_name not in added_names:
                        subcategory = Subcategory(
                            name=subcategory_name,
                            category_id=category.id
                        )
                        db.session.add(subcategory)
                        added_names.add(subcategory_name)
        
        db.session.commit()
