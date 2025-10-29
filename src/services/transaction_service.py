"""
Transaction service for managing financial transactions.
"""

from datetime import datetime
from ..extensions import db
from ..models import Transaction, BudgetPeriod


class TransactionService:
    """Service for handling transaction operations."""
    
    @staticmethod
    def get_user_transactions(user_id, active_period_only=True):
        """Get transactions for a user."""
        query = Transaction.query.filter_by(user_id=user_id)
        
        if active_period_only:
            # Get active budget period
            active_period = BudgetPeriod.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).first()
            
            if active_period:
                # Filter transactions within the active period
                query = query.filter(
                    Transaction.transaction_date >= active_period.start_date,
                    Transaction.transaction_date <= active_period.end_date
                )
        
        transactions = query.order_by(Transaction.transaction_date.desc()).all()
        
        result = []
        for transaction in transactions:
            result.append({
                'id': transaction.id,
                'amount': transaction.amount,
                'description': transaction.description,
                'comment': transaction.comment,
                'transaction_date': transaction.transaction_date.isoformat(),
                'subcategory': {
                    'id': transaction.subcategory.id,
                    'name': transaction.subcategory.name,
                    'category': {
                        'id': transaction.subcategory.category.id,
                        'name': transaction.subcategory.category.name
                    }
                }
            })
        
        return result
    
    @staticmethod
    def create_transaction(user_id, amount, subcategory_id, description=None, comment=None, transaction_date=None):
        """Create a new transaction."""
        if transaction_date is None:
            transaction_date = datetime.utcnow()
        
        transaction = Transaction(
            amount=amount,
            description=description,
            comment=comment,
            subcategory_id=subcategory_id,
            user_id=user_id,
            transaction_date=transaction_date
        )
        
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def update_transaction(transaction_id, user_id, **kwargs):
        """Update a transaction."""
        transaction = Transaction.query.filter_by(
            id=transaction_id, 
            user_id=user_id
        ).first()
        
        if not transaction:
            return None
        
        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        db.session.commit()
        return transaction
    
    @staticmethod
    def delete_transaction(transaction_id, user_id):
        """Delete a transaction."""
        transaction = Transaction.query.filter_by(
            id=transaction_id, 
            user_id=user_id
        ).first()
        
        if not transaction:
            return False
        
        db.session.delete(transaction)
        db.session.commit()
        return True
