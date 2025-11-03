"""
Transactions API routes.
"""

from flask import Blueprint, request, jsonify
from ...auth import token_required, subscription_required
from ...services import TransactionService

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@transactions_bp.route('', methods=['GET'])
@token_required
@subscription_required
def get_transactions(current_user):
    """Get all transactions for the current user."""
    transactions = TransactionService.get_user_transactions(current_user.id)
    return jsonify(transactions), 200


@transactions_bp.route('', methods=['POST'])
@token_required
@subscription_required
def create_transaction(current_user):
    """Create a new transaction."""
    data = request.get_json()
    
    amount = data.get('amount')
    subcategory_id = data.get('subcategory_id')
    description = data.get('description', '').strip()
    comment = data.get('comment', '').strip()
    
    if not amount or not subcategory_id:
        return jsonify({'message': 'Amount and subcategory are required'}), 400
    
    try:
        amount = float(amount)
        # Make expenses negative (expenses should be negative values)
        if amount > 0:
            amount = -amount
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid amount'}), 400
    
    transaction = TransactionService.create_transaction(
        user_id=current_user.id,
        amount=amount,
        subcategory_id=subcategory_id,
        description=description or None,
        comment=comment or None
    )
    
    return jsonify({
        'id': transaction.id,
        'amount': transaction.amount,
        'description': transaction.description,
        'comment': transaction.comment,
        'subcategory_id': transaction.subcategory_id,
        'transaction_date': transaction.transaction_date.isoformat()
    }), 201


@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@token_required
@subscription_required
def update_transaction(current_user, transaction_id):
    """Update a transaction."""
    data = request.get_json()
    
    update_data = {}
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            # Make expenses negative (expenses should be negative values)
            if amount > 0:
                amount = -amount
            update_data['amount'] = amount
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid amount'}), 400
    
    if 'description' in data:
        update_data['description'] = data['description'].strip() or None
    
    if 'comment' in data:
        update_data['comment'] = data['comment'].strip() or None
    
    if 'subcategory_id' in data:
        update_data['subcategory_id'] = data['subcategory_id']
    
    if not update_data:
        return jsonify({'message': 'No valid fields to update'}), 400
    
    transaction = TransactionService.update_transaction(transaction_id, current_user.id, **update_data)
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    return jsonify({'message': 'Transaction updated successfully'}), 200


@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@token_required
@subscription_required
def delete_transaction(current_user, transaction_id):
    """Delete a transaction."""
    success = TransactionService.delete_transaction(transaction_id, current_user.id)
    if not success:
        return jsonify({'message': 'Transaction not found'}), 404
    
    return jsonify({'message': 'Transaction deleted successfully'}), 200
