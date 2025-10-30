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
from .subscriptions import subscriptions_bp
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
api_bp.register_blueprint(subscriptions_bp)


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
        
        # Debug: Log received data
        print("=== ONBOARDING DATA RECEIVED ===")
        print("Categories:", data.get('categories', []))
        print("Subcategories:", data.get('subcategories', []))
        print("Currency:", data.get('currency'))
        print("First name:", data.get('firstName'), "or", data.get('first_name'))
        print("Last name:", data.get('lastName'), "or", data.get('last_name'))
        print("Username:", data.get('username'))
        print("Email:", data.get('email'))
        print("Password present:", bool(data.get('password')))
        print("Full data keys:", list(data.keys()))
        print("================================")
        
        # Extract form data
        username = (data.get('username', '') or '').strip()
        email = (data.get('email', '') or '').strip().lower()
        password = data.get('password', '') or ''
        # Handle both frontend (camelCase) and backend (snake_case) field names
        first_name = (data.get('firstName') or data.get('first_name') or '').strip()
        last_name = (data.get('lastName') or data.get('last_name') or '').strip()
        country = (data.get('country', '') or '').strip()
        preferred_name = (data.get('preferredName') or data.get('preferred_name') or '').strip()
        referral_source = (data.get('referralSource') or data.get('referral_source') or '').strip()
        referral_details = (data.get('referralDetailsText') or data.get('referral_details') or '').strip()
        currency = data.get('currency', 'USD')  # Extract currency from data
        
        # Validation (username is optional, will be auto-generated)
        if not all([email, password, first_name, last_name]):
            return jsonify({'message': 'Email, password, first name, and last name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Auto-generate username if not provided
        if not username:
            # Use email prefix or generate from name
            username = email.split('@')[0] if email else f"{first_name.lower()}_{last_name.lower()}"
        
        # Ensure username is unique
        from ...models import User
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Create user
        from ...services import UserService, AuthService
        from ...extensions import db
        
        user, error = UserService.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            country=country or None,
            preferred_name=preferred_name or None,
            referral_source=referral_source or None,
            referral_details=referral_details or None,
            currency=currency  # Pass currency to user creation
        )
        
        if error:
            return jsonify({'message': error}), 400
        
        # Create categories and subcategories based on user selection
        categories = data.get('categories', [])
        subcategories = data.get('subcategories', [])
        custom_category_names = data.get('custom_category_names', {})
        custom_subcategory_names = data.get('custom_subcategory_names', {})
        
        try:
            if categories or subcategories:
                from ...services import CategoryService
                CategoryService.create_onboarding_categories(
                    user_id=user.id,
                    categories=categories,
                    subcategories=subcategories,
                    custom_category_names=custom_category_names,
                    custom_subcategory_names=custom_subcategory_names
                )
        except Exception as category_error:
            # If category creation fails, rollback user creation
            print(f"Category creation failed: {str(category_error)}")
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': f'Error creating categories: {str(category_error)}'}), 500
        
        # Start trial subscription (optional, based on config)
        try:
            from flask import current_app
            if current_app.config.get('SUBSCRIPTIONS_ENABLED', True):
                from ...services.subscription_service import SubscriptionService
                SubscriptionService.seed_default_plans(current_app.config.get('DEFAULT_CURRENCY', 'ZAR'))
                SubscriptionService.start_trial(user, (data.get('plan') or 'monthly').lower(), current_app.config.get('TRIAL_DAYS', 30))
        except Exception as sub_err:
            print(f"Subscription trial setup failed: {str(sub_err)}")

        # Create email verification token
        verification_token = AuthService.create_email_verification_token(user)
        
        # Send verification email
        from flask import current_app
        EmailService.send_verification_email(user, verification_token, current_app.config)
        
        return jsonify({
            'message': 'Account created successfully! Please check your email to verify your account.',
            'user_id': user.id,
            'success': True,
            'email_verification_required': True,
            'email': user.email
        }), 201
        
    except Exception as e:
        print(f"Onboarding error: {str(e)}")
        import traceback
        traceback.print_exc()
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
        from ...services import AuthService
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
        from ...models import Budget, BudgetPeriod, BudgetAllocation
        
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not active_period:
            return jsonify({'message': 'No active budget period found'}), 404
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        if not budget:
            return jsonify({'message': 'No budget found for active period'}), 404
        
        # Calculate total available income (income sources + balance brought forward)
        total_income = (budget.total_income or 0) + (budget.balance_brought_forward or 0)
        
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
            'deficit': abs(balance) if balance < 0 else 0,  # Add deficit for dashboard compatibility
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
        from ...models import Budget, BudgetPeriod, BudgetAllocation, Transaction
        from ...extensions import db
        
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not active_period:
            return jsonify({'message': 'No active budget period found'}), 404
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        if not budget:
            return jsonify({'message': 'No budget found for active period'}), 404
        
        # Get all allocations for this budget
        allocations = BudgetAllocation.query.filter_by(budget_id=budget.id).all()
        
        # Get all transactions in the active period
        from ...models import Category, Subcategory
        user_subcategory_ids = db.session.query(Subcategory.id).join(Category).filter(
            Category.user_id == current_user.id
        ).subquery()
        
        transactions = Transaction.query.filter(
            Transaction.subcategory_id.in_(user_subcategory_ids),
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= active_period.start_date,
            Transaction.transaction_date <= active_period.end_date
        ).all()
        
        # Group transactions by subcategory
        subcategory_spending = {}
        for transaction in transactions:
            if transaction.amount < 0:  # Only count expenses
                subcategory_id = transaction.subcategory_id
                if subcategory_id not in subcategory_spending:
                    subcategory_spending[subcategory_id] = 0
                subcategory_spending[subcategory_id] += abs(transaction.amount)
        
        # Check for overspending
        overspending = []
        checked_subcategories = set()
        
        # Check subcategories that have allocations
        for allocation in allocations:
            subcategory_id = allocation.subcategory_id
            checked_subcategories.add(subcategory_id)
            
            total_spent = subcategory_spending.get(subcategory_id, 0)
            allocated = allocation.allocated_amount or 0
            
            # Check if spending exceeds allocation
            if total_spent > allocated:
                overspent_amount = total_spent - allocated
                overspent_percentage = (overspent_amount / allocated * 100) if allocated > 0 else 0
                
                overspending.append({
                    'subcategory_id': subcategory_id,
                    'subcategory_name': allocation.subcategory.name,
                    'category_name': allocation.subcategory.category.name,
                    'allocated': allocated,
                    'spent': total_spent,
                    'overspent_amount': overspent_amount,
                    'overspent_percentage': overspent_percentage
                })
        
        # Check subcategories with spending but no allocations (spending > 0 with allocated = 0 is overspending)
        for subcategory_id, total_spent in subcategory_spending.items():
            if subcategory_id not in checked_subcategories and total_spent > 0:
                # Get subcategory info
                subcategory = Subcategory.query.get(subcategory_id)
                if subcategory and subcategory.category.user_id == current_user.id:
                    overspending.append({
                        'subcategory_id': subcategory_id,
                        'subcategory_name': subcategory.name,
                        'category_name': subcategory.category.name,
                        'allocated': 0,
                        'spent': total_spent,
                        'overspent_amount': total_spent,
                        'overspent_percentage': 0  # Can't calculate percentage when allocated is 0
                    })
        
        return jsonify({
            'overspent_categories': overspending,
            'total_overspent_categories': len(overspending),
            'has_overspending': len(overspending) > 0
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error checking overspending: {str(e)}'}), 500


__all__ = ['user_bp', 'categories_bp', 'transactions_bp', 'budget_bp', 'accounts_bp', 'recurring_bp', 'subscriptions_bp', 'api_bp']
