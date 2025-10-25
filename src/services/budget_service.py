"""
Budget service for managing budgets and budget periods.
"""

from datetime import datetime, date
from ..extensions import db
from ..models import Budget, BudgetPeriod, BudgetAllocation, IncomeSource
from ..utils.budget import populate_budget_from_recurring, cleanup_duplicate_allocations


class BudgetService:
    """Service for handling budget operations."""
    
    @staticmethod
    def get_budget_periods(user_id):
        """Get all budget periods for a user."""
        periods = BudgetPeriod.query.filter_by(user_id=user_id).order_by(
            BudgetPeriod.created_at.desc()
        ).all()
        
        result = []
        for period in periods:
            result.append({
                'id': period.id,
                'name': period.name,
                'period_type': period.period_type,
                'start_date': period.start_date.isoformat(),
                'end_date': period.end_date.isoformat(),
                'is_active': period.is_active,
                'created_at': period.created_at.isoformat()
            })
        
        return result
    
    @staticmethod
    def create_budget_period(user_id, name, period_type, start_date, end_date):
        """Create a new budget period."""
        # Deactivate any existing active periods
        BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        
        period = BudgetPeriod(
            name=name,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            is_active=True
        )
        
        db.session.add(period)
        db.session.flush()  # Get the period ID
        
        # Create budget for this period
        budget = Budget(
            period_id=period.id,
            user_id=user_id
        )
        db.session.add(budget)
        db.session.commit()
        
        return period
    
    @staticmethod
    def activate_budget_period(period_id, user_id):
        """Activate a budget period."""
        # Deactivate all other periods for this user
        BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        
        # Activate the specified period
        period = BudgetPeriod.query.filter_by(id=period_id, user_id=user_id).first()
        if not period:
            return None
        
        period.is_active = True
        db.session.commit()
        return period
    
    @staticmethod
    def delete_budget_period(period_id, user_id):
        """Delete a budget period."""
        period = BudgetPeriod.query.filter_by(id=period_id, user_id=user_id).first()
        if not period:
            return False
        
        db.session.delete(period)
        db.session.commit()
        return True
    
    @staticmethod
    def get_budget(user_id):
        """Get the active budget for a user."""
        try:
            active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
            if not active_period:
                return None
            
            budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
            if not budget:
                return None
            
            # Get income sources
            income_sources = IncomeSource.query.filter_by(budget_id=budget.id).all()
            income_data = [{'id': source.id, 'name': source.name, 'amount': source.amount} for source in income_sources]
            
            # Get allocations with error handling
            allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).all()
            allocation_data = []
            for allocation in allocations:
                try:
                    # Check if subcategory and category exist
                    if allocation.subcategory and allocation.subcategory.category:
                        allocation_data.append({
                            'id': allocation.id,
                            'allocated_amount': allocation.allocated_amount,
                            'subcategory': {
                                'id': allocation.subcategory.id,
                                'name': allocation.subcategory.name,
                                'category': {
                                    'id': allocation.subcategory.category.id,
                                    'name': allocation.subcategory.category.name
                                }
                            }
                        })
                    else:
                        # Skip allocations with missing subcategory or category
                        print(f"Warning: Skipping allocation {allocation.id} - missing subcategory or category")
                except Exception as e:
                    print(f"Error processing allocation {allocation.id}: {str(e)}")
                    continue
            
            return {
                'id': budget.id,
                'total_income': budget.total_income,
                'balance_brought_forward': budget.balance_brought_forward,
                'income_sources': income_data,
                'allocations': allocation_data,
                'period_name': active_period.name,  # Add period_name for dashboard compatibility
                'period': {
                    'id': active_period.id,
                    'name': active_period.name,
                    'start_date': active_period.start_date.isoformat(),
                    'end_date': active_period.end_date.isoformat()
                }
            }
        except Exception as e:
            print(f"Error in get_budget: {str(e)}")
            return None
    
    @staticmethod
    def update_budget(user_id, total_income=None, balance_brought_forward=None):
        """Update budget details."""
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        if not active_period:
            return None
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
        if not budget:
            return None
        
        if total_income is not None:
            budget.total_income = total_income
        if balance_brought_forward is not None:
            budget.balance_brought_forward = balance_brought_forward
        
        db.session.commit()
        return budget
    
    @staticmethod
    def update_allocations(user_id, allocations_data):
        """Update budget allocations."""
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        if not active_period:
            return False
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
        if not budget:
            return False
        
        # Clear existing allocations
        BudgetAllocation.query.filter_by(budget_id=budget.id).delete()
        
        # Add new allocations
        for allocation_data in allocations_data:
            allocation = BudgetAllocation(
                allocated_amount=allocation_data['allocated_amount'],
                subcategory_id=allocation_data['subcategory_id'],
                budget_id=budget.id
            )
            db.session.add(allocation)
        
        db.session.commit()
        return True
    
    @staticmethod
    def create_income_source(user_id, name, amount):
        """Create an income source for the active budget."""
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        if not active_period:
            return None
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
        if not budget:
            return None
        
        income_source = IncomeSource(
            name=name,
            amount=amount,
            budget_id=budget.id
        )
        
        db.session.add(income_source)
        db.session.flush()  # Get the income source ID
        
        # Update total income by adding the new amount to existing total
        budget.total_income = (budget.total_income or 0) + amount
        db.session.commit()
        
        return income_source
    
    @staticmethod
    def recalculate_total_income(user_id):
        """Recalculate total income from all income sources."""
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        if not active_period:
            return False
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
        if not budget:
            return False
        
        # Calculate total from all income sources
        total_income = sum(source.amount for source in budget.income_sources)
        budget.total_income = total_income
        
        db.session.commit()
        return True
    
    @staticmethod
    def populate_from_recurring(user_id):
        """Populate current budget from recurring sources."""
        active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
        if not active_period:
            return False
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
        if not budget:
            return False
        
        from ..models import User
        user = User.query.get(user_id)
        populate_budget_from_recurring(user, budget)
        return True
