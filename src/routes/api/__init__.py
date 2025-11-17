"""
API route blueprints.
"""

from flask import Blueprint, request, jsonify, current_app
from .user import user_bp
from .categories import categories_bp
from .transactions import transactions_bp
from .budget import budget_bp
from .accounts import accounts_bp
from .recurring import recurring_bp
from .subscriptions import subscriptions_bp
from ...auth import token_required, get_current_user
from ...services import EmailService
from ...extensions import limiter, csrf
from ...utils.password import validate_password_strength

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register all API blueprints first
api_bp.register_blueprint(user_bp)
api_bp.register_blueprint(categories_bp)
api_bp.register_blueprint(transactions_bp)
api_bp.register_blueprint(budget_bp)
api_bp.register_blueprint(accounts_bp)
api_bp.register_blueprint(recurring_bp)
api_bp.register_blueprint(subscriptions_bp)

# Exempt all API routes from CSRF protection (they use JWT tokens)
# Must be done after registering nested blueprints
csrf.exempt(api_bp)


@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit contact form."""
    from marshmallow import ValidationError
    from ...schemas import ContactFormSchema
    from ...utils.validation import handle_validation_error
    
    schema = ContactFormSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    try:
        # Send email
        from flask import current_app
        
        # Check if email is configured
        if not current_app.config.get('MAIL_SERVER') or not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
            current_app.logger.error("Email configuration is missing. Please check your .env file.")
            return jsonify({'message': 'Email service is not configured. Please contact the administrator.'}), 500
        
        success = EmailService.send_contact_email(
            validated_data['name'],
            validated_data['email'],
            validated_data['subject'],
            validated_data['message'],
            current_app.config
        )
        
        if success:
            return jsonify({'message': 'Message sent successfully'}), 200
        else:
            current_app.logger.error("Failed to send contact email - check server logs for details")
            return jsonify({'message': 'Failed to send message. Please check your email configuration or try again later.'}), 500
            
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error sending contact email: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'message': f'An error occurred while sending the message: {str(e)}'}), 500


@api_bp.route('/validate-email', methods=['POST'])
def validate_email():
    """Validate if email already exists."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Always return the same response to prevent email enumeration
        # Don't reveal whether email exists or not
        return jsonify({'available': True, 'message': 'Email validation complete'}), 200
        
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
@limiter.limit("3 per hour")
def complete_onboarding():
    """Complete the onboarding process and create user account."""
    from marshmallow import ValidationError
    from ...schemas import OnboardingSchema
    from ...utils.validation import handle_validation_error
    
    schema = OnboardingSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    try:
        # Extract validated data
        username = validated_data.get('username')
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        country = validated_data.get('country')
        preferred_name = validated_data.get('preferred_name')
        referral_source = validated_data.get('referral_source')
        referral_details = validated_data.get('referral_details')
        currency = validated_data.get('currency', 'USD')
        
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
        from datetime import datetime
        
        user, error = UserService.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            country=country,
            preferred_name=preferred_name,
            referral_source=referral_source,
            referral_details=referral_details,
            currency=currency
        )
        
        # Store legal acceptance (MANDATORY - validated by schema to be True)
        # Schema validation ensures accept_terms and accept_privacy are True
        if user:
            # Use validated values from schema (already validated to be True)
            user.terms_accepted = validated_data.get('accept_terms', True)
            user.privacy_policy_accepted = validated_data.get('accept_privacy', True)
            user.terms_accepted_at = datetime.utcnow()
            user.privacy_policy_accepted_at = datetime.utcnow()
            # Store version identifiers (you can update these when documents change)
            user.terms_version = '1.0'  # Update when Terms change
            user.privacy_policy_version = '1.0'  # Update when Privacy Policy changes
            db.session.commit()
        
        if error:
            return jsonify({'message': error}), 400
        
        # Create categories and subcategories based on user selection
        categories = validated_data.get('categories', [])
        subcategories = validated_data.get('subcategories', [])
        custom_category_names = validated_data.get('custom_category_names', {})
        custom_subcategory_names = validated_data.get('custom_subcategory_names', {})
        
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
            from flask import current_app
            current_app.logger.error(f"Category creation failed: {str(category_error)}")
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Error creating categories. Please try again.'}), 500
        
        # Start trial subscription (optional, based on config)
        subscription = None
        payfast_payload = None
        subscriptions_enabled = False
        try:
            from flask import current_app
            # Check if subscriptions are enabled (config converts string to boolean)
            subscriptions_enabled = current_app.config.get('SUBSCRIPTIONS_ENABLED', True)
            if subscriptions_enabled:
                from ...services.subscription_service import SubscriptionService
                from ...services.payfast_service import PayFastService
                
                SubscriptionService.seed_default_plans(current_app.config.get('DEFAULT_CURRENCY', 'ZAR'))
                plan_code = validated_data.get('plan', 'monthly').lower()
                subscription = SubscriptionService.start_trial(user, plan_code, current_app.config.get('TRIAL_DAYS', 30))
                
                # Send trial started email
                # EmailService is already imported at the top of the file (line 14)
                trial_days = current_app.config.get('TRIAL_DAYS', 30)
                EmailService.send_subscription_email(
                    user=user,
                    email_type='trial_started',
                    app_config=current_app.config,
                    trial_days=trial_days,
                    trial_start=user.trial_start.isoformat() if user.trial_start else 'N/A',
                    trial_end=user.trial_end.isoformat() if user.trial_end else 'N/A',
                    plan=plan_code
                )
                
                # Build PayFast payload for redirect to hosted payment page
                # User will enter card details securely on PayFast's platform
                # Set amount to 0.00 and billing_date to trial_end so PayFast saves payment method
                # but doesn't charge until trial period ends
                from ...services.subscription_service import MONTHLY_PRICE_CENTS, YEARLY_PRICE_CENTS
                amount_cents = MONTHLY_PRICE_CENTS if plan_code == 'monthly' else YEARLY_PRICE_CENTS
                # Pass trial_end as billing_date and defer_payment=True to save payment method without charging
                billing_date = user.trial_end if user.trial_end else None
                payfast_payload = PayFastService.build_subscription_payload(
                    user, subscription.id, plan_code, amount_cents, 
                    billing_date=billing_date, 
                    defer_payment=True  # Save payment method but don't charge until trial ends
                )
                payfast_payload['test_mode'] = 'true' if current_app.config.get('PAYFAST_TEST_MODE', True) else 'false'
        except Exception as sub_err:
            from flask import current_app
            current_app.logger.error(f"Subscription trial setup failed: {str(sub_err)}")

        # Create email verification token
        verification_token = AuthService.create_email_verification_token(user)
        
        # Send verification email
        from flask import current_app
        EmailService.send_verification_email(user, verification_token, current_app.config)
        
        response_data = {
            'message': 'Account created successfully! Please check your email to verify your account.',
            'user_id': user.id,
            'success': True,
            'email_verification_required': True,
            'email': user.email
        }
        
        # Only include PayFast redirect if subscriptions are enabled AND payload was created
        # subscriptions_enabled is already checked above, so if we reach here with payload, it's valid
        if subscriptions_enabled and subscription and payfast_payload:
            response_data['redirect_to_payfast'] = True
            response_data['payfast'] = payfast_payload
            response_data['message'] = 'Account created! Redirecting to secure payment setup...'
        
        return jsonify(response_data), 201
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Onboarding error: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error creating account. Please try again.'}), 500


@api_bp.route('/resend-verification', methods=['POST'])
@limiter.limit("3 per hour")
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
@limiter.exempt  # Exempt GET requests from rate limiting
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
@limiter.exempt  # Exempt GET requests from rate limiting
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
