"""
Transactions API routes.
"""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ...auth import token_required, subscription_required
from ...services import TransactionService
from ...extensions import csrf, limiter
from ...schemas import TransactionSchema, TransactionUpdateSchema
from ...utils.validation import handle_validation_error

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

# Exempt from CSRF (uses JWT tokens)
csrf.exempt(transactions_bp)


@transactions_bp.route('', methods=['GET'])
@limiter.exempt  # Exempt GET requests from rate limiting
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
    schema = TransactionSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    transaction = TransactionService.create_transaction(
        user_id=current_user.id,
        amount=validated_data['amount'],
        subcategory_id=validated_data['subcategory_id'],
        description=validated_data.get('description'),
        comment=validated_data.get('comment')
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
    schema = TransactionUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return handle_validation_error(err)
    
    if not validated_data:
        return jsonify({'message': 'No valid fields to update'}), 400
    
    transaction = TransactionService.update_transaction(transaction_id, current_user.id, **validated_data)
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
