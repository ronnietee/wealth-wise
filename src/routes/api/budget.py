"""
Budget API routes.
"""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ...auth import token_required, subscription_required
from ...services import BudgetService
from ...schemas import (
    BudgetPeriodSchema, BudgetPeriodUpdateSchema, BudgetUpdateSchema,
    BudgetAllocationsUpdateSchema, IncomeSourceSchema, IncomeSourceUpdateSchema
)
from ...utils.validation import handle_validation_error
from ...extensions import limiter

budget_bp = Blueprint('budget', __name__, url_prefix='/budget')


@budget_bp.route('/budget-periods', methods=['GET'])
@limiter.exempt  # Exempt GET requests from rate limiting
@token_required
@subscription_required
def get_budget_periods(current_user):
    """Get all budget periods for the current user."""
    periods = BudgetService.get_budget_periods(current_user.id)
    return jsonify(periods), 200


@budget_bp.route('/budget-periods', methods=['POST'])
@token_required
@subscription_required
def create_budget_period(current_user):
    """Create a new budget period."""
    schema = BudgetPeriodSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    try:
        period = BudgetService.create_budget_period(
            user_id=current_user.id,
            name=validated_data['name'],
            period_type=validated_data['period_type'],
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date']
        )
    except ValueError as e:
        # Handle overlap validation errors
        return jsonify({
            'message': str(e),
            'errors': {'period_overlap': [str(e)]}
        }), 400
    
    return jsonify({
        'id': period.id,
        'name': period.name,
        'period_type': period.period_type,
        'start_date': period.start_date.isoformat(),
        'end_date': period.end_date.isoformat(),
        'is_active': period.is_active
    }), 201


@budget_bp.route('/budget-periods/<int:period_id>/activate', methods=['POST'])
@token_required
@subscription_required
def activate_budget_period(current_user, period_id):
    """Activate a budget period."""
    period = BudgetService.activate_budget_period(period_id, current_user.id)
    if not period:
        return jsonify({'message': 'Budget period not found'}), 404
    
    return jsonify({'message': 'Budget period activated successfully'}), 200


@budget_bp.route('/budget-periods/<int:period_id>', methods=['PUT'])
@token_required
@subscription_required
def update_budget_period(current_user, period_id):
    """Update a budget period."""
    schema = BudgetPeriodUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return handle_validation_error(err)
    
    if not validated_data:
        return jsonify({'message': 'No valid fields to update'}), 400
    
    try:
        period = BudgetService.update_budget_period(
            period_id=period_id,
            user_id=current_user.id,
            **validated_data
        )
    except ValueError as e:
        # Handle overlap validation errors
        return jsonify({
            'message': str(e),
            'errors': {'period_overlap': [str(e)]}
        }), 400
    
    if not period:
        return jsonify({'message': 'Budget period not found'}), 404
    
    return jsonify({
        'id': period.id,
        'name': period.name,
        'period_type': period.period_type,
        'start_date': period.start_date.isoformat(),
        'end_date': period.end_date.isoformat(),
        'is_active': period.is_active,
        'message': 'Budget period updated successfully'
    }), 200


@budget_bp.route('/budget-periods/<int:period_id>', methods=['DELETE'])
@token_required
@subscription_required
def delete_budget_period(current_user, period_id):
    """Delete a budget period."""
    success = BudgetService.delete_budget_period(period_id, current_user.id)
    if not success:
        return jsonify({'message': 'Budget period not found'}), 404
    
    return jsonify({'message': 'Budget period deleted successfully'}), 200


@budget_bp.route('/budget', methods=['GET'])
@limiter.exempt  # Exempt GET requests from rate limiting
@token_required
@subscription_required
def get_budget(current_user):
    """Get the active budget for the current user."""
    try:
        budget = BudgetService.get_budget(current_user.id)
        if not budget:
            return jsonify({'message': 'No active budget found'}), 404
        
        return jsonify(budget), 200
    except Exception as e:
        print(f"Error in get_budget API: {str(e)}")
        return jsonify({'message': f'Error loading budget: {str(e)}'}), 500


@budget_bp.route('/budget', methods=['PUT'])
@token_required
@subscription_required
def update_budget(current_user):
    """Update budget details."""
    data = request.get_json()
    
    total_income = data.get('total_income')
    balance_brought_forward = data.get('balance_brought_forward')
    
    if total_income is not None:
        try:
            total_income = float(total_income)
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid total income'}), 400
    
    if balance_brought_forward is not None:
        try:
            balance_brought_forward = float(balance_brought_forward)
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid balance brought forward'}), 400
    
    budget = BudgetService.update_budget(
        user_id=current_user.id,
        total_income=total_income,
        balance_brought_forward=balance_brought_forward
    )
    
    if not budget:
        return jsonify({'message': 'No active budget found'}), 404
    
    return jsonify({'message': 'Budget updated successfully'}), 200


@budget_bp.route('/allocations', methods=['POST'])
@token_required
@subscription_required
def update_allocations(current_user):
    """Update budget allocations."""
    schema = BudgetAllocationsUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    # Extract allocations list from validated data
    allocations = validated_data['allocations']
    # Convert to format expected by service (list of dicts with subcategory_id and allocated_amount)
    allocations_list = [
        {'subcategory_id': alloc['subcategory_id'], 'allocated_amount': alloc['allocated']}
        for alloc in allocations
    ]
    
    success = BudgetService.update_allocations(current_user.id, allocations_list)
    if not success:
        return jsonify({'message': 'No active budget found'}), 404
    
    return jsonify({'message': 'Allocations updated successfully'}), 200


@budget_bp.route('/income-sources', methods=['POST'])
@token_required
@subscription_required
def create_income_source(current_user):
    """Create an income source for the active budget."""
    schema = IncomeSourceSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    income_source = BudgetService.create_income_source(
        current_user.id,
        validated_data['name'],
        validated_data['amount']
    )
    if not income_source:
        return jsonify({'message': 'No active budget found'}), 404
    
    return jsonify({
        'id': income_source.id,
        'name': income_source.name,
        'amount': income_source.amount
    }), 201


@budget_bp.route('/income-sources/<int:source_id>', methods=['PUT'])
@token_required
@subscription_required
def update_income_source(current_user, source_id):
    """Update an income source."""
    schema = IncomeSourceUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return handle_validation_error(err)
    
    if not validated_data:
        return jsonify({'message': 'Name or amount is required'}), 400
    
    # Get the income source
    from ...models import IncomeSource, Budget, BudgetPeriod
    active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_period:
        return jsonify({'message': 'No active budget period found'}), 404
    
    budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
    if not budget:
        return jsonify({'message': 'No budget found'}), 404
    
    income_source = IncomeSource.query.filter_by(id=source_id, budget_id=budget.id).first()
    if not income_source:
        return jsonify({'message': 'Income source not found'}), 404
    
    if 'name' in validated_data:
        income_source.name = validated_data['name']
    if 'amount' in validated_data:
        income_source.amount = validated_data['amount']
    
    from ...extensions import db
    db.session.commit()
    
    # Recalculate total income from all sources
    BudgetService.recalculate_total_income(current_user.id)
    
    return jsonify({'message': 'Income source updated successfully'}), 200


@budget_bp.route('/income-sources/<int:source_id>', methods=['DELETE'])
@token_required
@subscription_required
def delete_income_source(current_user, source_id):
    """Delete an income source."""
    try:
        from ...models import IncomeSource, Budget, BudgetPeriod
        from ...extensions import db
        
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not active_period:
            return jsonify({'message': 'No active budget period found'}), 404
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        if not budget:
            return jsonify({'message': 'No budget found'}), 404
        
        income_source = IncomeSource.query.filter_by(id=source_id, budget_id=budget.id).first()
        if not income_source:
            return jsonify({'message': 'Income source not found'}), 404
        
        # Delete the income source
        db.session.delete(income_source)
        db.session.commit()
        
        # Recalculate total income from remaining sources
        BudgetService.recalculate_total_income(current_user.id)
        
        return jsonify({'message': 'Income source deleted successfully'}), 200
        
    except Exception as e:
        from ...extensions import db
        db.session.rollback()
        return jsonify({'message': f'Error deleting income source: {str(e)}'}), 500


@budget_bp.route('/recalculate-income', methods=['POST'])
@token_required
@subscription_required
def recalculate_income(current_user):
    """Recalculate total income from all income sources."""
    try:
        success = BudgetService.recalculate_total_income(current_user.id)
        if not success:
            return jsonify({'message': 'No active budget found'}), 404
        
        return jsonify({'message': 'Total income recalculated successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error recalculating income: {str(e)}'}), 500
