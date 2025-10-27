"""
Recurring income and allocation API routes.
"""

from flask import Blueprint, request, jsonify
from ...auth import token_required
from ...extensions import db
from ...models import RecurringIncomeSource, RecurringBudgetAllocation

recurring_bp = Blueprint('recurring', __name__, url_prefix='/')


@recurring_bp.route('/recurring-income-sources', methods=['GET'])
@token_required
def get_recurring_income_sources(current_user):
    """Get all recurring income sources for the user."""
    sources = RecurringIncomeSource.query.filter_by(user_id=current_user.id).all()
    
    result = []
    for source in sources:
        result.append({
            'id': source.id,
            'name': source.name,
            'amount': source.amount,
            'is_active': source.is_active,
            'created_at': source.created_at.isoformat(),
            'updated_at': source.updated_at.isoformat()
        })
    
    return jsonify(result), 200


@recurring_bp.route('/recurring-income-sources', methods=['POST'])
@token_required
def create_recurring_income_source(current_user):
    """Create a new recurring income source."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    amount = data.get('amount')
    
    if not name or amount is None:
        return jsonify({'message': 'Name and amount are required'}), 400
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid amount'}), 400
    
    source = RecurringIncomeSource(
        name=name,
        amount=amount,
        user_id=current_user.id
    )
    
    db.session.add(source)
    db.session.commit()
    
    return jsonify({
        'id': source.id,
        'name': source.name,
        'amount': source.amount,
        'is_active': source.is_active,
        'created_at': source.created_at.isoformat()
    }), 201


@recurring_bp.route('/recurring-income-sources/<int:source_id>', methods=['PUT'])
@token_required
def update_recurring_income_source(current_user, source_id):
    """Update a recurring income source."""
    data = request.get_json()
    
    source = RecurringIncomeSource.query.filter_by(id=source_id, user_id=current_user.id).first()
    if not source:
        return jsonify({'message': 'Recurring income source not found'}), 404
    
    if 'name' in data:
        source.name = data['name'].strip()
    if 'amount' in data:
        try:
            source.amount = float(data['amount'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid amount'}), 400
    if 'is_active' in data:
        source.is_active = bool(data['is_active'])
    
    db.session.commit()
    
    return jsonify({'message': 'Recurring income source updated successfully'}), 200


@recurring_bp.route('/recurring-income-sources/<int:source_id>', methods=['DELETE'])
@token_required
def delete_recurring_income_source(current_user, source_id):
    """Delete a recurring income source."""
    source = RecurringIncomeSource.query.filter_by(id=source_id, user_id=current_user.id).first()
    if not source:
        return jsonify({'message': 'Recurring income source not found'}), 404
    
    db.session.delete(source)
    db.session.commit()
    
    return jsonify({'message': 'Recurring income source deleted successfully'}), 200


@recurring_bp.route('/recurring-allocations', methods=['GET'])
@token_required
def get_recurring_allocations(current_user):
    """Get all recurring budget allocations for the user."""
    allocations = RecurringBudgetAllocation.query.filter_by(user_id=current_user.id).all()
    
    result = []
    for allocation in allocations:
        # Check if subcategory relationship exists
        if allocation.subcategory:
            result.append({
                'id': allocation.id,
                'allocated_amount': allocation.allocated_amount,
                'is_active': allocation.is_active,
                'category_name': allocation.subcategory.category.name if allocation.subcategory.category else '',
                'subcategory_name': allocation.subcategory.name,
                'subcategory_id': allocation.subcategory.id,
                'created_at': allocation.created_at.isoformat(),
                'updated_at': allocation.updated_at.isoformat()
            })
    
    return jsonify(result), 200


@recurring_bp.route('/recurring-allocations', methods=['POST'])
@token_required
def create_recurring_allocation(current_user):
    """Create a new recurring budget allocation."""
    data = request.get_json()
    
    allocated_amount = data.get('allocated_amount')
    subcategory_id = data.get('subcategory_id')
    
    if allocated_amount is None or not subcategory_id:
        return jsonify({'message': 'Allocated amount and subcategory are required'}), 400
    
    try:
        allocated_amount = float(allocated_amount)
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid allocated amount'}), 400
    
    allocation = RecurringBudgetAllocation(
        allocated_amount=allocated_amount,
        subcategory_id=subcategory_id,
        user_id=current_user.id
    )
    
    db.session.add(allocation)
    db.session.commit()
    
    return jsonify({
        'id': allocation.id,
        'allocated_amount': allocation.allocated_amount,
        'subcategory_id': allocation.subcategory_id,
        'is_active': allocation.is_active,
        'created_at': allocation.created_at.isoformat()
    }), 201


@recurring_bp.route('/recurring-allocations/<int:allocation_id>', methods=['PUT'])
@token_required
def update_recurring_allocation(current_user, allocation_id):
    """Update a recurring budget allocation."""
    data = request.get_json()
    
    allocation = RecurringBudgetAllocation.query.filter_by(id=allocation_id, user_id=current_user.id).first()
    if not allocation:
        return jsonify({'message': 'Recurring allocation not found'}), 404
    
    if 'allocated_amount' in data:
        try:
            allocation.allocated_amount = float(data['allocated_amount'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid allocated amount'}), 400
    if 'subcategory_id' in data:
        allocation.subcategory_id = data['subcategory_id']
    if 'is_active' in data:
        allocation.is_active = bool(data['is_active'])
    
    db.session.commit()
    
    return jsonify({'message': 'Recurring allocation updated successfully'}), 200


@recurring_bp.route('/recurring-allocations/<int:allocation_id>', methods=['DELETE'])
@token_required
def delete_recurring_allocation(current_user, allocation_id):
    """Delete a recurring budget allocation."""
    allocation = RecurringBudgetAllocation.query.filter_by(id=allocation_id, user_id=current_user.id).first()
    if not allocation:
        return jsonify({'message': 'Recurring allocation not found'}), 404
    
    db.session.delete(allocation)
    db.session.commit()
    
    return jsonify({'message': 'Recurring allocation deleted successfully'}), 200


@recurring_bp.route('/populate-current-budget', methods=['POST'])
@token_required
def populate_current_budget_from_recurring(current_user):
    """Manually populate the current active budget with recurring sources."""
    from ..services import BudgetService
    
    success = BudgetService.populate_from_recurring(current_user.id)
    if not success:
        return jsonify({'message': 'No active budget found'}), 404
    
    return jsonify({'message': 'Budget populated from recurring sources successfully'}), 200
