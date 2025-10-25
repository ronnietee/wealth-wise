"""
Budget API routes.
"""

from flask import Blueprint, request, jsonify
from ...auth import token_required
from ...services import BudgetService

budget_bp = Blueprint('budget', __name__, url_prefix='/budget')


@budget_bp.route('/budget-periods', methods=['GET'])
@token_required
def get_budget_periods(current_user):
    """Get all budget periods for the current user."""
    periods = BudgetService.get_budget_periods(current_user.id)
    return jsonify(periods), 200


@budget_bp.route('/budget-periods', methods=['POST'])
@token_required
def create_budget_period(current_user):
    """Create a new budget period."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    period_type = data.get('period_type', '').strip()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not all([name, period_type, start_date, end_date]):
        return jsonify({'message': 'All fields are required'}), 400
    
    try:
        from datetime import datetime
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
    except (ValueError, AttributeError):
        return jsonify({'message': 'Invalid date format'}), 400
    
    period = BudgetService.create_budget_period(
        user_id=current_user.id,
        name=name,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date
    )
    
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
def activate_budget_period(current_user, period_id):
    """Activate a budget period."""
    period = BudgetService.activate_budget_period(period_id, current_user.id)
    if not period:
        return jsonify({'message': 'Budget period not found'}), 404
    
    return jsonify({'message': 'Budget period activated successfully'}), 200


@budget_bp.route('/budget-periods/<int:period_id>', methods=['DELETE'])
@token_required
def delete_budget_period(current_user, period_id):
    """Delete a budget period."""
    success = BudgetService.delete_budget_period(period_id, current_user.id)
    if not success:
        return jsonify({'message': 'Budget period not found'}), 404
    
    return jsonify({'message': 'Budget period deleted successfully'}), 200


@budget_bp.route('/budget', methods=['GET'])
@token_required
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
def update_allocations(current_user):
    """Update budget allocations."""
    data = request.get_json()
    allocations = data.get('allocations', [])
    
    if not isinstance(allocations, list):
        return jsonify({'message': 'Allocations must be a list'}), 400
    
    success = BudgetService.update_allocations(current_user.id, allocations)
    if not success:
        return jsonify({'message': 'No active budget found'}), 404
    
    return jsonify({'message': 'Allocations updated successfully'}), 200


@budget_bp.route('/income-sources', methods=['POST'])
@token_required
def create_income_source(current_user):
    """Create an income source for the active budget."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    amount = data.get('amount')
    
    if not name or amount is None:
        return jsonify({'message': 'Name and amount are required'}), 400
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid amount'}), 400
    
    income_source = BudgetService.create_income_source(current_user.id, name, amount)
    if not income_source:
        return jsonify({'message': 'No active budget found'}), 404
    
    return jsonify({
        'id': income_source.id,
        'name': income_source.name,
        'amount': income_source.amount
    }), 201


@budget_bp.route('/income-sources/<int:source_id>', methods=['PUT'])
@token_required
def update_income_source(current_user, source_id):
    """Update an income source."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    amount = data.get('amount')
    
    if not name and amount is None:
        return jsonify({'message': 'Name or amount is required'}), 400
    
    if amount is not None:
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid amount'}), 400
    
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
    
    old_amount = income_source.amount
    
    if name:
        income_source.name = name
    if amount is not None:
        income_source.amount = amount
    
    from ...extensions import db
    db.session.commit()
    
    # Recalculate total income from all sources
    BudgetService.recalculate_total_income(current_user.id)
    
    return jsonify({'message': 'Income source updated successfully'}), 200


@budget_bp.route('/income-sources/<int:source_id>', methods=['DELETE'])
@token_required
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
def recalculate_income(current_user):
    """Recalculate total income from all income sources."""
    try:
        success = BudgetService.recalculate_total_income(current_user.id)
        if not success:
            return jsonify({'message': 'No active budget found'}), 404
        
        return jsonify({'message': 'Total income recalculated successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error recalculating income: {str(e)}'}), 500
