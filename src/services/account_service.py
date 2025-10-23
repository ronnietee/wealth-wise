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
        
        total_balance = sum(account.current_balance for account in accounts)
        
        account_summary = []
        for account in accounts:
            account_summary.append({
                'id': account.id,
                'name': account.name,
                'account_type': account.account_type,
                'balance': account.current_balance
            })
        
        return {
            'total_balance': total_balance,
            'account_count': len(accounts),
            'accounts': account_summary
        }
