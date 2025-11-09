"""
Budget utility functions.
"""

from ..extensions import db
from ..models import IncomeSource, BudgetAllocation, RecurringIncomeSource, RecurringBudgetAllocation


def populate_budget_from_recurring(user, budget, period_type):
    """Populate a new budget with recurring income sources and allocations matching the period type."""
    try:
        # Check if budget already has data to avoid duplicates
        existing_income_sources = IncomeSource.query.filter_by(budget_id=budget.id).count()
        existing_allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).count()
        
        if existing_income_sources > 0 or existing_allocations > 0:
            print(f"Budget {budget.id} already has data, skipping auto-population to avoid duplicates")
            return
        
        # Add recurring income sources matching the period type
        recurring_income_sources = RecurringIncomeSource.query.filter_by(
            user_id=user.id, 
            period_type=period_type,
            is_active=True
        ).all()
        
        for recurring_source in recurring_income_sources:
            income_source = IncomeSource(
                name=recurring_source.name,
                amount=recurring_source.amount,
                budget_id=budget.id,
                is_recurring_source=True,
                recurring_source_id=recurring_source.id
            )
            db.session.add(income_source)
        
        # Add recurring budget allocations matching the period type
        recurring_allocations = RecurringBudgetAllocation.query.filter_by(
            user_id=user.id,
            period_type=period_type,
            is_active=True
        ).all()
        
        for recurring_allocation in recurring_allocations:
            budget_allocation = BudgetAllocation(
                allocated_amount=recurring_allocation.allocated_amount,
                subcategory_id=recurring_allocation.subcategory_id,
                budget_id=budget.id,
                is_recurring_allocation=True,
                recurring_allocation_id=recurring_allocation.id
            )
            db.session.add(budget_allocation)
        
        # Update total income
        budget.total_income = sum(source.amount for source in budget.income_sources)
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error populating budget from recurring sources: {str(e)}")
        db.session.rollback()


def cleanup_duplicate_allocations(budget):
    """Remove duplicate allocations from a budget."""
    try:
        # Get all allocations for this budget
        allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).all()
        
        # Group by subcategory_id and keep only the first one
        seen_subcategories = set()
        duplicates_removed = 0
        
        for allocation in allocations:
            if allocation.subcategory_id in seen_subcategories:
                # This is a duplicate, remove it
                db.session.delete(allocation)
                duplicates_removed += 1
            else:
                seen_subcategories.add(allocation.subcategory_id)
        
        db.session.commit()
        return duplicates_removed
        
    except Exception as e:
        print(f"Error cleaning up duplicates: {str(e)}")
        db.session.rollback()
        return 0
