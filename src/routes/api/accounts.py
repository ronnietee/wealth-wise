"""
Accounts API routes.
"""

from flask import Blueprint, request, jsonify
from ...auth import token_required
from ...services import AccountService

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')


@accounts_bp.route('/accounts', methods=['GET'])
@token_required
def get_accounts(current_user):
    """Get all accounts for the current user."""
    accounts = AccountService.get_user_accounts(current_user.id)
    return jsonify(accounts), 200


@accounts_bp.route('/accounts', methods=['POST'])
@token_required
def create_account(current_user):
    """Create a new account."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    account_type = data.get('account_type', '').strip()
    bank_name = data.get('bank_name', '').strip() or None
    account_number = data.get('account_number', '').strip() or None
    current_balance = data.get('current_balance', 0)
    
    if not name or not account_type:
        return jsonify({'message': 'Name and account type are required'}), 400
    
    try:
        current_balance = float(current_balance)
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid balance'}), 400
    
    account = AccountService.create_account(
        user_id=current_user.id,
        name=name,
        account_type=account_type,
        bank_name=bank_name,
        account_number=account_number,
        current_balance=current_balance
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


@accounts_bp.route('/accounts/<int:account_id>', methods=['PUT'])
@token_required
def update_account(current_user, account_id):
    """Update an account."""
    data = request.get_json()
    
    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name'].strip()
    if 'account_type' in data:
        update_data['account_type'] = data['account_type'].strip()
    if 'bank_name' in data:
        update_data['bank_name'] = data['bank_name'].strip() or None
    if 'account_number' in data:
        update_data['account_number'] = data['account_number'].strip() or None
    if 'current_balance' in data:
        try:
            update_data['current_balance'] = float(data['current_balance'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid balance'}), 400
    
    if not update_data:
        return jsonify({'message': 'No valid fields to update'}), 400
    
    account = AccountService.update_account(account_id, current_user.id, **update_data)
    if not account:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({'message': 'Account updated successfully'}), 200


@accounts_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@token_required
def delete_account(current_user, account_id):
    """Delete an account."""
    success = AccountService.delete_account(account_id, current_user.id)
    if not success:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({'message': 'Account deleted successfully'}), 200


@accounts_bp.route('/accounts/balance-summary', methods=['GET'])
@token_required
def get_balance_summary(current_user):
    """Get balance summary for all accounts."""
    summary = AccountService.get_balance_summary(current_user.id)
    return jsonify(summary), 200
