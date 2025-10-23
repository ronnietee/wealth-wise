"""
API route blueprints.
"""

from flask import Blueprint, request, jsonify
from .user import user_bp
from .categories import categories_bp
from .transactions import transactions_bp
from .budget import budget_bp
from .accounts import accounts_bp
from .recurring import recurring_bp
from ...auth import token_required, get_current_user
from ...services import EmailService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register all API blueprints
api_bp.register_blueprint(user_bp)
api_bp.register_blueprint(categories_bp)
api_bp.register_blueprint(transactions_bp)
api_bp.register_blueprint(budget_bp)
api_bp.register_blueprint(accounts_bp)
api_bp.register_blueprint(recurring_bp)


@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit contact form."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        if not all([name, email, subject, message]):
            return jsonify({'message': 'All fields are required'}), 400
        
        # Send email
        from flask import current_app
        success = EmailService.send_contact_email(name, email, subject, message, current_app.config)
        
        if success:
            return jsonify({'message': 'Message sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send message. Please try again later.'}), 500
            
    except Exception as e:
        return jsonify({'message': 'An error occurred while sending the message'}), 500


@api_bp.route('/validate-email', methods=['POST'])
def validate_email():
    """Validate if email already exists."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        from ...models import User
        user = User.query.filter_by(email=email).first()
        
        return jsonify({'available': user is None}), 200
        
    except Exception as e:
        return jsonify({'message': 'Error validating email'}), 500


@api_bp.route('/validate-username', methods=['POST'])
def validate_username():
    """Validate if username already exists."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'message': 'Username is required'}), 400
        
        from ...models import User
        user = User.query.filter_by(username=username).first()
        
        return jsonify({'available': user is None}), 200
        
    except Exception as e:
        return jsonify({'message': 'Error validating username'}), 500


@api_bp.route('/onboarding/complete', methods=['POST'])
def complete_onboarding():
    """Complete the onboarding process and create user account."""
    try:
        data = request.get_json()
        
        # Extract form data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        # Handle both frontend (camelCase) and backend (snake_case) field names
        first_name = data.get('first_name', data.get('firstName', '')).strip()
        last_name = data.get('last_name', data.get('lastName', '')).strip()
        country = data.get('country', '').strip()
        preferred_name = data.get('preferred_name', data.get('preferredName', '')).strip()
        referral_source = data.get('referral_source', data.get('referralSource', '')).strip()
        referral_details = data.get('referral_details', data.get('referralDetails', '')).strip()
        
        # Validation
        if not all([username, email, password, first_name, last_name]):
            return jsonify({'message': 'Username, email, password, first name, and last name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Create user
        from ...services import UserService, AuthService
        user, error = UserService.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            country=country or None,
            preferred_name=preferred_name or None,
            referral_source=referral_source or None,
            referral_details=referral_details or None
        )
        
        if error:
            return jsonify({'message': error}), 400
        
        # Create email verification token
        verification_token = AuthService.create_email_verification_token(user)
        
        # Send verification email
        from flask import current_app
        EmailService.send_verification_email(user, verification_token, current_app.config)
        
        return jsonify({
            'message': 'Account created successfully! Please check your email to verify your account.',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating account: {str(e)}'}), 500


@api_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        from ...models import User
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.email_verified:
            return jsonify({'message': 'Email is already verified'}), 400
        
        # Create new verification token
        from ..services import AuthService
        verification_token = AuthService.create_email_verification_token(user)
        
        # Send verification email
        from flask import current_app
        EmailService.send_verification_email(user, verification_token, current_app.config)
        
        return jsonify({'message': 'Verification email sent successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error sending verification email: {str(e)}'}), 500


@api_bp.route('/budget/balance-check', methods=['GET'])
@token_required
def check_budget_balance(current_user):
    """Check if total income is sufficient for total allocated budget."""
    try:
        from ..models import Budget, BudgetPeriod, BudgetAllocation
        
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not active_period:
            return jsonify({'message': 'No active budget period found'}), 404
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        if not budget:
            return jsonify({'message': 'No budget found for active period'}), 404
        
        # Calculate total income
        total_income = budget.total_income or 0
        
        # Calculate total allocated
        allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).all()
        total_allocated = sum(allocation.allocated_amount for allocation in allocations)
        
        # Check balance
        balance = total_income - total_allocated
        is_balanced = balance >= 0
        
        return jsonify({
            'total_income': total_income,
            'total_allocated': total_allocated,
            'balance': balance,
            'is_balanced': is_balanced,
            'message': 'Budget is balanced' if is_balanced else 'Budget allocation exceeds income'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error checking budget balance: {str(e)}'}), 500


@api_bp.route('/budget/overspending-check', methods=['GET'])
@token_required
def check_overspending(current_user):
    """Check for subcategories where spending exceeds allocation."""
    try:
        from ..models import Budget, BudgetPeriod, BudgetAllocation, Transaction
        
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not active_period:
            return jsonify({'message': 'No active budget period found'}), 404
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        if not budget:
            return jsonify({'message': 'No budget found for active period'}), 404
        
        # Get allocations
        allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).all()
        
        overspending = []
        for allocation in allocations:
            # Get transactions for this subcategory in the current period
            transactions = Transaction.query.filter(
                Transaction.subcategory_id == allocation.subcategory_id,
                Transaction.user_id == current_user.id,
                Transaction.transaction_date >= active_period.start_date,
                Transaction.transaction_date <= active_period.end_date
            ).all()
            
            total_spent = sum(transaction.amount for transaction in transactions)
            
            if total_spent > allocation.allocated_amount:
                overspending.append({
                    'subcategory_id': allocation.subcategory_id,
                    'subcategory_name': allocation.subcategory.name,
                    'category_name': allocation.subcategory.category.name,
                    'allocated_amount': allocation.allocated_amount,
                    'total_spent': total_spent,
                    'overspend_amount': total_spent - allocation.allocated_amount
                })
        
        return jsonify({
            'overspending': overspending,
            'count': len(overspending)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error checking overspending: {str(e)}'}), 500


__all__ = ['user_bp', 'categories_bp', 'transactions_bp', 'budget_bp', 'accounts_bp', 'recurring_bp', 'api_bp']
