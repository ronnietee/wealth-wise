"""
Subscription-related API endpoints.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from ...auth import token_required, admin_required
from ...services.subscription_service import SubscriptionService, MONTHLY_PRICE_CENTS, YEARLY_PRICE_CENTS
from ...services.payfast_service import PayFastService
from ...extensions import db
from ...models.subscription import SubscriptionPlan, Subscription


subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')


@subscriptions_bp.route('/plans', methods=['GET'])
def list_plans():
    SubscriptionService.seed_default_plans(current_app.config.get('DEFAULT_CURRENCY', 'ZAR'))
    plans = SubscriptionPlan.query.filter_by(active=True).all()
    return jsonify([
        {
            'code': p.code,
            'name': p.name,
            'price_cents': p.price_cents,
            'currency': p.currency,
            'interval': p.interval
        } for p in plans
    ])


@subscriptions_bp.route('/start', methods=['POST'])
@token_required
def start_subscription(current_user):
    data = request.get_json() or {}
    plan_code = (data.get('plan') or 'monthly').lower()

    if plan_code not in ['monthly', 'yearly']:
        return jsonify({'message': 'Invalid plan'}), 400

    # Ensure plans exist
    SubscriptionService.seed_default_plans(current_app.config.get('DEFAULT_CURRENCY', 'ZAR'))

    # Start trial and set plan
    sub = SubscriptionService.start_trial(current_user, plan_code, current_app.config.get('TRIAL_DAYS', 30))

    # Send trial started email
    from ...services import EmailService
    EmailService.send_subscription_email(
        user=current_user,
        email_type='trial_started',
        app_config=current_app.config,
        trial_days=current_app.config.get('TRIAL_DAYS', 30),
        trial_start=current_user.trial_start.isoformat() if current_user.trial_start else 'N/A',
        trial_end=current_user.trial_end.isoformat() if current_user.trial_end else 'N/A',
        plan=plan_code
    )

    # Build PayFast payload for redirect-based subscription setup (optional step)
    amount_cents = MONTHLY_PRICE_CENTS if plan_code == 'monthly' else YEARLY_PRICE_CENTS
    payload = PayFastService.build_subscription_payload(current_user, sub.id, plan_code, amount_cents)

    return jsonify({
        'message': 'Trial started',
        'subscription': {
            'id': sub.id,
            'status': sub.status,
            'trial_end': current_user.trial_end.isoformat() if current_user.trial_end else None,
            'plan': plan_code
        },
        'payfast': payload  # Frontend can post this to PayFast if/when enabling subscriptions
    }), 201


@subscriptions_bp.route('/status', methods=['GET'])
@token_required
def subscription_status(current_user):
    enforce = current_app.config.get('ENFORCE_PAYMENT_AFTER_TRIAL', False)
    allowed, reason = SubscriptionService.check_access(current_user, enforce)
    return jsonify({
        'status': current_user.subscription_status,
        'plan': current_user.subscription_plan,
        'trial_end': current_user.trial_end.isoformat() if current_user.trial_end else None,
        'allowed': allowed,
        'reason': reason
    })


@subscriptions_bp.route('/webhook/payfast', methods=['POST'])
def payfast_webhook():
    """Handle PayFast ITN (Instant Transaction Notification) webhook."""
    payload = request.form.to_dict() or {}
    
    # Validate signature
    valid, reason = PayFastService.validate_itn(payload)
    if not valid:
        current_app.logger.warning(f'PayFast ITN validation failed: {reason}')
        return jsonify({'message': 'Invalid signature'}), 400

    # Verify merchant_id matches
    merchant_id = payload.get('merchant_id', '')
    expected_merchant_id = current_app.config.get('PAYFAST_MERCHANT_ID', '')
    if merchant_id != expected_merchant_id:
        current_app.logger.warning(f'PayFast ITN merchant_id mismatch: {merchant_id}')
        return jsonify({'message': 'Invalid merchant_id'}), 400
    
    # POST-back validation (additional security)
    postback_valid, postback_reason = PayFastService.postback_validation(payload)
    if not postback_valid:
        current_app.logger.warning(f'PayFast POST-back validation failed: {postback_reason}')
        # Log warning but continue - signature validation is primary

    # Map ITN to user/subscription
    success, user, subscription, message = SubscriptionService.process_payfast_itn(payload)
    if not success:
        current_app.logger.error(f'PayFast ITN processing failed: {message}')
        return jsonify({'message': message}), 400

    # Extract payment details
    pf_payment_id = payload.get('pf_payment_id')
    payment_status = payload.get('payment_status', '').upper()  # COMPLETE, FAILED, PENDING
    amount_gross = payload.get('amount_gross') or payload.get('amount', '0')
    token = payload.get('token', '')  # Subscription token from PayFast
    subscription_token = payload.get('subscription_token', token)  # Alternative field name
    
    try:
        amount_cents = int(float(amount_gross) * 100)
    except (ValueError, TypeError):
        amount_cents = 0
    
    currency = payload.get('currency', 'ZAR') or 'ZAR'

    # Import email service
    from ...services import EmailService
    
    # Process payment based on status
    if payment_status == 'COMPLETE':
        # Record successful payment
        payment = SubscriptionService.record_payment(
            user=user,
            subscription=subscription,
            amount_cents=amount_cents,
            currency=currency,
            status='paid',
            gateway_ref=pf_payment_id
        )
        
        # Activate subscription if it's not already active
        if subscription and subscription.status in ['trial', 'inactive']:
            # Calculate next billing date based on plan
            plan = subscription.plan_code if subscription else user.subscription_plan
            if plan == 'monthly':
                next_billing = datetime.utcnow() + timedelta(days=30)
            elif plan == 'yearly':
                next_billing = datetime.utcnow() + timedelta(days=365)
            else:
                next_billing = None
            
            SubscriptionService.activate_subscription(
                user=user,
                subscription=subscription,
                next_billing_at=next_billing,
                gateway_sub_id=subscription_token or pf_payment_id
            )
            
            # Send activation email
            EmailService.send_subscription_email(
                user=user,
                email_type='subscription_activated',
                app_config=current_app.config,
                plan=plan,
                next_billing=next_billing.strftime('%Y-%m-%d') if next_billing else 'N/A'
            )
            
            current_app.logger.info(f'Subscription activated for user {user.id}, subscription {subscription.id}')
        
        # Send payment success email
        EmailService.send_subscription_email(
            user=user,
            email_type='payment_success',
            app_config=current_app.config,
            amount=f"{currency} {amount_cents / 100:.2f}",
            reference=pf_payment_id
        )
        
        current_app.logger.info(f'Payment processed: {pf_payment_id} for user {user.id}, amount {amount_cents}')
        
    elif payment_status == 'FAILED':
        # Record failed payment
        SubscriptionService.record_payment(
            user=user,
            subscription=subscription,
            amount_cents=amount_cents,
            currency=currency,
            status='failed',
            gateway_ref=pf_payment_id
        )
        
        # Send payment failed email
        EmailService.send_subscription_email(
            user=user,
            email_type='payment_failed',
            app_config=current_app.config
        )
        
        current_app.logger.warning(f'Payment failed: {pf_payment_id} for user {user.id}')
        
    elif payment_status == 'PENDING':
        # Record pending payment
        SubscriptionService.record_payment(
            user=user,
            subscription=subscription,
            amount_cents=amount_cents,
            currency=currency,
            status='pending',
            gateway_ref=pf_payment_id
        )
        current_app.logger.info(f'Payment pending: {pf_payment_id} for user {user.id}')
    
    # Always acknowledge ITN (PayFast requirement)
    return jsonify({'message': 'OK'}), 200


@subscriptions_bp.route('/cancel', methods=['POST'])
@token_required
def cancel_subscription(current_user):
    """Cancel the user's subscription."""
    data = request.get_json() or {}
    cancel_immediately = bool(data.get('immediately', False))
    
    # Find user's active subscription
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).order_by(Subscription.created_at.desc()).first()
    
    if not subscription:
        return jsonify({'message': 'No active subscription found'}), 404
    
    if subscription.status == 'cancelled':
        return jsonify({'message': 'Subscription already cancelled'}), 400
    
    cancel_at = SubscriptionService.cancel_subscription(current_user, subscription, cancel_immediately)
    
    # Send cancellation email
    from ...services import EmailService
    EmailService.send_subscription_email(
        user=current_user,
        email_type='subscription_cancelled',
        app_config=current_app.config,
        cancel_at=cancel_at.isoformat() if cancel_at else None
    )
    
    return jsonify({
        'message': 'Subscription cancelled successfully',
        'cancel_immediately': cancel_immediately,
        'cancel_at': cancel_at.isoformat() if cancel_at else None
    }), 200


@subscriptions_bp.route('/pause', methods=['POST'])
@token_required
def pause_subscription(current_user):
    """Pause the user's subscription."""
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).order_by(Subscription.created_at.desc()).first()
    
    if not subscription:
        return jsonify({'message': 'No active subscription found'}), 404
    
    if subscription.status == 'inactive':
        return jsonify({'message': 'Subscription already paused'}), 400
    
    SubscriptionService.pause_subscription(current_user, subscription)
    
    return jsonify({
        'message': 'Subscription paused successfully'
    }), 200


@subscriptions_bp.route('/resume', methods=['POST'])
@token_required
def resume_subscription(current_user):
    """Resume a paused subscription."""
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).order_by(Subscription.created_at.desc()).first()
    
    if not subscription:
        return jsonify({'message': 'No subscription found'}), 404
    
    if subscription.status != 'inactive':
        return jsonify({'message': 'Subscription is not paused'}), 400
    
    SubscriptionService.resume_subscription(current_user, subscription)
    
    return jsonify({
        'message': 'Subscription resumed successfully'
    }), 200


@subscriptions_bp.route('/payments', methods=['GET'])
@token_required
def get_payments(current_user):
    """Get payment history for the current user."""
    from ...models.subscription import Payment
    
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(
        Payment.created_at.desc()
    ).limit(50).all()
    
    return jsonify([
        {
            'id': p.id,
            'amount_cents': p.amount_cents,
            'currency': p.currency,
            'status': p.status,
            'gateway_reference': p.gateway_reference,
            'paid_at': p.paid_at.isoformat() if p.paid_at else None,
            'created_at': p.created_at.isoformat()
        } for p in payments
    ]), 200


@subscriptions_bp.route('/upgrade', methods=['POST'])
@token_required
def upgrade_subscription(current_user):
    """Upgrade subscription plan."""
    data = request.get_json() or {}
    new_plan = data.get('plan', '').lower()
    
    if new_plan not in ['monthly', 'yearly']:
        return jsonify({'message': 'Invalid plan'}), 400
    
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).order_by(Subscription.created_at.desc()).first()
    
    if not subscription:
        return jsonify({'message': 'No subscription found'}), 404
    
    old_plan = subscription.plan_code
    
    # Check if it's actually an upgrade
    if old_plan == 'yearly' and new_plan == 'monthly':
        return jsonify({'message': 'Use downgrade endpoint for plan reductions'}), 400
    if old_plan == new_plan:
        return jsonify({'message': 'Already on this plan'}), 400
    
    SubscriptionService.upgrade_subscription(current_user, subscription, new_plan)
    
    # Send upgrade email
    from ...services import EmailService
    EmailService.send_subscription_email(
        user=current_user,
        email_type='upgrade',
        app_config=current_app.config,
        new_plan=new_plan
    )
    
    return jsonify({
        'message': 'Subscription upgraded successfully',
        'old_plan': old_plan,
        'new_plan': new_plan
    }), 200


@subscriptions_bp.route('/downgrade', methods=['POST'])
@token_required
def downgrade_subscription(current_user):
    """Downgrade subscription plan (takes effect at period end)."""
    data = request.get_json() or {}
    new_plan = data.get('plan', '').lower()
    
    if new_plan not in ['monthly', 'yearly']:
        return jsonify({'message': 'Invalid plan'}), 400
    
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).order_by(Subscription.created_at.desc()).first()
    
    if not subscription:
        return jsonify({'message': 'No subscription found'}), 404
    
    old_plan = subscription.plan_code
    
    # Check if it's actually a downgrade
    if old_plan == 'monthly' and new_plan == 'yearly':
        return jsonify({'message': 'Use upgrade endpoint for plan increases'}), 400
    if old_plan == new_plan:
        return jsonify({'message': 'Already on this plan'}), 400
    
    SubscriptionService.downgrade_subscription(current_user, subscription, new_plan)
    
    # Send downgrade email
    from ...services import EmailService
    EmailService.send_subscription_email(
        user=current_user,
        email_type='downgrade',
        app_config=current_app.config,
        new_plan=new_plan
    )
    
    return jsonify({
        'message': 'Subscription downgrade scheduled',
        'old_plan': old_plan,
        'new_plan': new_plan,
        'effective_date': subscription.current_period_end.isoformat() if subscription.current_period_end else None
    }), 200


@subscriptions_bp.route('/renewal/process', methods=['POST'])
@admin_required
def process_renewals(current_user):
    """Admin endpoint to process subscription renewals (typically called by cron job)."""
    from ...models.subscription import Subscription
    
    subscriptions = Subscription.query.filter_by(status='active').all()
    renewed = 0
    failed = []
    
    for subscription in subscriptions:
        try:
            if SubscriptionService.process_renewal(subscription):
                renewed += 1
        except Exception as e:
            failed.append({'subscription_id': subscription.id, 'error': str(e)})
            current_app.logger.error(f'Renewal failed for subscription {subscription.id}: {str(e)}')
    
    return jsonify({
        'message': f'Processed renewals: {renewed} successful, {len(failed)} failed',
        'renewed': renewed,
        'failed': failed
    }), 200


@subscriptions_bp.route('/enforcement/status', methods=['GET'])
@admin_required
def get_enforcement_status(current_user):
    """Get current payment enforcement status."""
    enabled = current_app.config.get('ENFORCE_PAYMENT_AFTER_TRIAL', False)
    return jsonify({
        'enforce_payment_after_trial': enabled,
        'status': 'enabled' if enabled else 'disabled'
    }), 200


@subscriptions_bp.route('/toggle-enforcement', methods=['POST'])
@admin_required
def toggle_enforcement(current_user):
    """Toggle payment enforcement - controls whether users are blocked after trial expires.
    
    When ENABLED:
    - Users with expired trials will be BLOCKED from accessing subscription-gated features
    - Users must have an active paid subscription to continue using the app
    
    When DISABLED (development/testing mode):
    - Users can continue using the app even after their trial expires
    - Useful for testing and development before going live
    """
    # Get current state and toggle it
    current_state = current_app.config.get('ENFORCE_PAYMENT_AFTER_TRIAL', False)
    new_state = not current_state
    current_app.config['ENFORCE_PAYMENT_AFTER_TRIAL'] = new_state
    
    status_msg = "ENABLED" if new_state else "DISABLED"
    user_msg = "will be BLOCKED" if new_state else "can continue accessing"
    
    return jsonify({
        'enforce_payment_after_trial': new_state,
        'previous_state': current_state,
        'message': f'Payment enforcement {status_msg}. Users with expired trials {user_msg} the app.'
    })


# Admin reporting endpoints
@subscriptions_bp.route('/admin/subscriptions', methods=['GET'])
@admin_required
def admin_subscriptions(current_user):
    """Admin endpoint to get all subscriptions with stats."""
    try:
        from ...models.subscription import Subscription
        
        subscriptions = Subscription.query.order_by(Subscription.created_at.desc()).all()
        
        # Calculate stats
        stats = {
            'total': len(subscriptions),
            'by_status': {},
            'by_plan': {},
        }
        
        for sub in subscriptions:
            # Count by status
            status = sub.status or 'unknown'
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by plan
            plan = sub.plan_code or 'unknown'
            stats['by_plan'][plan] = stats['by_plan'].get(plan, 0) + 1
        
        # Serialize subscriptions
        subscriptions_data = []
        for sub in subscriptions:
            try:
                # Safely serialize datetime fields
                def safe_isoformat(dt):
                    if dt is None:
                        return None
                    if hasattr(dt, 'isoformat'):
                        return dt.isoformat()
                    return str(dt)
                
                subscriptions_data.append({
                    'id': sub.id,
                    'user_id': sub.user_id,
                    'user_email': sub.user.email if sub.user else None,
                    'plan_code': sub.plan_code,
                    'status': sub.status,
                    'started_at': safe_isoformat(sub.started_at),
                    'current_period_start': safe_isoformat(sub.current_period_start),
                    'current_period_end': safe_isoformat(sub.current_period_end),
                    'payfast_subscription_id': sub.payfast_subscription_id,
                    'cancel_at': safe_isoformat(sub.cancel_at),
                    'cancelled_at': safe_isoformat(sub.cancelled_at),
                    'created_at': safe_isoformat(sub.created_at),
                })
            except Exception as e:
                current_app.logger.error(f"Error serializing subscription {sub.id}: {e}")
                import traceback
                current_app.logger.error(traceback.format_exc())
                # Skip this subscription if there's an error
                continue
        
        return jsonify({
            'subscriptions': subscriptions_data,
            'stats': stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in admin_subscriptions: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'message': f'Error loading subscriptions: {str(e)}'}), 500


@subscriptions_bp.route('/admin/payments', methods=['GET'])
@admin_required
def admin_payments(current_user):
    """Admin endpoint to get all payments with stats."""
    try:
        from ...models.subscription import Payment
        
        payments = Payment.query.order_by(Payment.created_at.desc()).limit(500).all()
        
        # Calculate stats
        stats = {
            'total': len(payments),
            'by_status': {},
            'total_revenue_cents': 0,
            'total_revenue_by_currency': {},
            'by_gateway': {},
        }
        
        for payment in payments:
            # Count by status
            status = payment.status or 'unknown'
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Sum revenue for paid payments
            if payment.status == 'paid':
                stats['total_revenue_cents'] += payment.amount_cents
                currency = payment.currency or 'ZAR'
                stats['total_revenue_by_currency'][currency] = stats['total_revenue_by_currency'].get(currency, 0) + payment.amount_cents
            
            # Count by gateway
            gateway = payment.gateway or 'unknown'
            stats['by_gateway'][gateway] = stats['by_gateway'].get(gateway, 0) + 1
        
        # Serialize payments
        payments_data = []
        for p in payments:
            try:
                # Safely serialize datetime fields
                def safe_isoformat(dt):
                    if dt is None:
                        return None
                    if hasattr(dt, 'isoformat'):
                        return dt.isoformat()
                    return str(dt)
                
                payments_data.append({
                    'id': p.id,
                    'user_id': p.user_id,
                    'user_email': p.user.email if p.user else None,
                    'subscription_id': p.subscription_id,
                    'amount_cents': p.amount_cents,
                    'currency': p.currency,
                    'status': p.status,
                    'gateway': p.gateway,
                    'gateway_reference': p.gateway_reference,
                    'paid_at': safe_isoformat(p.paid_at),
                    'created_at': safe_isoformat(p.created_at),
                })
            except Exception as e:
                current_app.logger.error(f"Error serializing payment {p.id}: {e}")
                import traceback
                current_app.logger.error(traceback.format_exc())
                # Skip this payment if there's an error
                continue
        
        return jsonify({
            'payments': payments_data,
            'stats': stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in admin_payments: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'message': f'Error loading payments: {str(e)}'}), 500


