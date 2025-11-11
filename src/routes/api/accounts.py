"""
Accounts API routes.
"""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ...auth import token_required, subscription_required
from ...services import AccountService
from ...schemas import AccountSchema, AccountUpdateSchema
from ...utils.validation import handle_validation_error
from ...extensions import limiter

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')


@accounts_bp.route('/', methods=['GET'])
@limiter.exempt  # Exempt GET requests from rate limiting
@token_required
@subscription_required
def get_accounts(current_user):
    """Get all accounts for the current user."""
    accounts = AccountService.get_user_accounts(current_user.id)
    return jsonify(accounts), 200


@accounts_bp.route('/', methods=['POST'])
@token_required
@subscription_required
def create_account(current_user):
    """Create a new account."""
    schema = AccountSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    account = AccountService.create_account(
        user_id=current_user.id,
        name=validated_data['name'],
        account_type=validated_data['account_type'],
        bank_name=validated_data.get('bank_name'),
        account_number=validated_data.get('account_number'),
        current_balance=validated_data.get('current_balance', 0.0)
    )
    
    return jsonify({
        'id': account.id,
        'name': account.name,
        'account_type': account.account_type,
        'bank_name': account.bank_name,
        'account_number': account.account_number,
        'current_balance': account.current_balance,
        'created_at': account.created_at.isoformat()
    }), 201


@accounts_bp.route('/<int:account_id>', methods=['PUT'])
@token_required
@subscription_required
def update_account(current_user, account_id):
    """Update an account."""
    schema = AccountUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return handle_validation_error(err)
    
    if not validated_data:
        return jsonify({'message': 'No valid fields to update'}), 400
    
    account = AccountService.update_account(account_id, current_user.id, **validated_data)
    if not account:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({'message': 'Account updated successfully'}), 200


@accounts_bp.route('/<int:account_id>', methods=['DELETE'])
@token_required
@subscription_required
def delete_account(current_user, account_id):
    """Delete an account."""
    success = AccountService.delete_account(account_id, current_user.id)
    if not success:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({'message': 'Account deleted successfully'}), 200


@accounts_bp.route('/balance-summary', methods=['GET'])
@token_required
@subscription_required
def get_balance_summary(current_user):
    """Get balance summary for all accounts."""
    summary = AccountService.get_balance_summary(current_user.id)
    return jsonify(summary), 200
