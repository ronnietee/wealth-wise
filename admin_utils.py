#!/usr/bin/env python3
"""
Admin utilities for Wealth Wise application
These functions can be used for maintenance and support tasks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Budget, BudgetPeriod, BudgetAllocation, IncomeSource
from datetime import datetime

def cleanup_duplicate_allocations(user_id=None):
    """Remove duplicate allocations from budgets"""
    with app.app_context():
        try:
            if user_id:
                # Clean up specific user
                budgets = Budget.query.filter_by(user_id=user_id).all()
                print(f"Cleaning up duplicates for user {user_id}...")
            else:
                # Clean up all users
                budgets = Budget.query.all()
                print("Cleaning up duplicates for all users...")
            
            total_duplicates_removed = 0
            
            for budget in budgets:
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
                
                if duplicates_removed > 0:
                    print(f"  Budget {budget.id}: Removed {duplicates_removed} duplicates")
                    total_duplicates_removed += duplicates_removed
            
            db.session.commit()
            print(f"Cleanup completed. Removed {total_duplicates_removed} duplicate allocations total.")
            return total_duplicates_removed
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            db.session.rollback()
            return 0

def debug_budget_calculation(user_id):
    """Debug budget calculation for a specific user"""
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"User {user_id} not found")
                return
            
            print(f"Debug Budget Calculation for User: {user.username}")
            print("=" * 50)
            
            # Get active budget period
            active_period = BudgetPeriod.query.filter_by(user_id=user.id, is_active=True).first()
            if not active_period:
                print("No active budget period found")
                return
            
            budget = Budget.query.filter_by(period_id=active_period.id, user_id=user.id).first()
            if not budget:
                print("No budget found for active period")
                return
            
            # Get all budgets for this user
            all_budgets = Budget.query.filter_by(user_id=user.id).all()
            
            # Calculate totals for current budget
            current_income = sum(source.amount for source in budget.income_sources)
            current_balance_forward = budget.balance_brought_forward or 0
            current_allocated = sum(allocation.allocated_amount for allocation in budget.allocations)
            
            print(f"Current Budget ({active_period.name}):")
            print(f"  Budget ID: {budget.id}")
            print(f"  Income Sources: {len(budget.income_sources)}")
            print(f"  Allocations: {len(budget.allocations)}")
            print(f"  Total Income: R{current_income:,.2f}")
            print(f"  Balance Forward: R{current_balance_forward:,.2f}")
            print(f"  Total Available: R{current_income + current_balance_forward:,.2f}")
            print(f"  Total Allocated: R{current_allocated:,.2f}")
            print(f"  Balance: R{(current_income + current_balance_forward) - current_allocated:,.2f}")
            print()
            
            # Calculate totals across all budgets
            total_income_all = sum(
                sum(source.amount for source in b.income_sources) + (b.balance_brought_forward or 0)
                for b in all_budgets
            )
            total_allocated_all = sum(
                sum(allocation.allocated_amount for allocation in b.allocations)
                for b in all_budgets
            )
            
            print(f"All Budgets Summary:")
            print(f"  Total Budgets: {len(all_budgets)}")
            print(f"  Total Income (All): R{total_income_all:,.2f}")
            print(f"  Total Allocated (All): R{total_allocated_all:,.2f}")
            print(f"  Balance (All): R{total_income_all - total_allocated_all:,.2f}")
            print()
            
            # Show allocation details
            all_allocations = BudgetAllocation.query.join(Budget).filter(Budget.user_id == user.id).all()
            print(f"Allocations Detail ({len(all_allocations)} total):")
            for i, allocation in enumerate(all_allocations[:20]):  # Show first 20
                period_name = allocation.budget.period.name if allocation.budget.period else 'Unknown'
                print(f"  {i+1:2d}. Budget {allocation.budget_id} ({period_name}): R{allocation.allocated_amount:,.2f}")
            
            if len(all_allocations) > 20:
                print(f"  ... and {len(all_allocations) - 20} more allocations")
            
        except Exception as e:
            print(f"Error during debug: {str(e)}")

def list_users():
    """List all users in the system"""
    with app.app_context():
        try:
            users = User.query.all()
            print(f"Users in system ({len(users)} total):")
            print("=" * 50)
            for user in users:
                print(f"ID: {user.id:3d} | Username: {user.username:20s} | Email: {user.email:30s} | Created: {user.created_at.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Error listing users: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python admin_utils.py list-users")
        print("  python admin_utils.py debug-user <user_id>")
        print("  python admin_utils.py cleanup-duplicates [user_id]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list-users':
        list_users()
    elif command == 'debug-user':
        if len(sys.argv) < 3:
            print("Usage: python admin_utils.py debug-user <user_id>")
            sys.exit(1)
        user_id = int(sys.argv[2])
        debug_budget_calculation(user_id)
    elif command == 'cleanup-duplicates':
        user_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        cleanup_duplicate_allocations(user_id)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
