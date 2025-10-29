"""
Account service for managing financial accounts.
"""

from datetime import datetime
from ..extensions import db
from ..models import Account


class AccountService:
    """Service for handling account operations."""
    
    @staticmethod
    def get_user_accounts(user_id):
        """Get all active accounts for a user."""
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        
        result = []
        for account in accounts:
            result.append({
                'id': account.id,
                'name': account.name,
                'account_type': account.account_type,
                'bank_name': account.bank_name,
                'account_number': account.account_number,
                'current_balance': account.current_balance,
                'created_at': account.created_at.isoformat(),
                'updated_at': account.updated_at.isoformat()
            })
        
        return result
    
    @staticmethod
    def create_account(user_id, name, account_type, bank_name=None, account_number=None, current_balance=0):
        """Create a new account."""
        account = Account(
            name=name,
            account_type=account_type,
            bank_name=bank_name,
            account_number=account_number,
            current_balance=current_balance,
            user_id=user_id
        )
        
        db.session.add(account)
        db.session.commit()
        return account
    
    @staticmethod
    def update_account(account_id, user_id, **kwargs):
        """Update an account."""
        account = Account.query.filter_by(
            id=account_id, 
            user_id=user_id, 
            is_active=True
        ).first()
        
        if not account:
            return None
        
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        account.updated_at = datetime.utcnow()
        db.session.commit()
        return account
    
    @staticmethod
    def delete_account(account_id, user_id):
        """Soft delete an account."""
        account = Account.query.filter_by(
            id=account_id, 
            user_id=user_id, 
            is_active=True
        ).first()
        
        if not account:
            return False
        
        account.is_active = False
        account.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    
    @staticmethod
    def get_balance_summary(user_id):
        """Get balance summary for all accounts."""
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        
        total_accounts_balance = sum(account.current_balance for account in accounts)
        
        # Get app balance from active budget
        from ..models import Budget, BudgetPeriod
        app_balance = 0
        try:
            active_period = BudgetPeriod.query.filter_by(user_id=user_id, is_active=True).first()
            if active_period:
                budget = Budget.query.filter_by(period_id=active_period.id, user_id=user_id).first()
                if budget:
                    # Calculate app balance as total income minus total spent
                    total_income = (budget.total_income or 0) + (budget.balance_brought_forward or 0)
                    
                    # Calculate total spent from transactions
                    from ..models import Transaction, Category, Subcategory
                    from ..extensions import db
                    user_subcategory_ids = db.session.query(Subcategory.id).join(Category).filter(Category.user_id == user_id).subquery()
                    # Get all transactions in the period
                    transactions = Transaction.query.filter(
                        Transaction.subcategory_id.in_(user_subcategory_ids),
                        Transaction.transaction_date >= active_period.start_date,
                        Transaction.transaction_date <= active_period.end_date
                    ).all()
                    
                    # Calculate total spent as positive value (only count negative amounts as expenses)
                    # This matches how category_service calculates spent amounts
                    total_spent = sum(abs(t.amount) for t in transactions if t.amount < 0)
                    
                    app_balance = total_income - total_spent
        except Exception as e:
            print(f"Error calculating app balance: {str(e)}")
            app_balance = 0
        
        balance_difference = total_accounts_balance - app_balance
        alignment_percentage = 100 if app_balance == 0 else (total_accounts_balance / app_balance * 100) if app_balance > 0 else 0
        is_aligned = abs(balance_difference) < 0.01  # Consider aligned if difference is less than 1 cent
        
        account_summary = []
        for account in accounts:
            account_summary.append({
                'id': account.id,
                'name': account.name,
                'account_type': account.account_type,
                'balance': account.current_balance
            })
        
        return {
            'total_accounts_balance': total_accounts_balance,
            'app_balance': app_balance,
            'balance_difference': balance_difference,
            'alignment_percentage': alignment_percentage,
            'is_aligned': is_aligned,
            'account_count': len(accounts),
            'accounts': account_summary
        }
