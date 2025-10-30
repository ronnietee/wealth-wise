"""
Subscription-related API endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
from ...auth import token_required
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

    # Build PayFast payload for redirect-based subscription setup (optional step)
    amount_cents = MONTHLY_PRICE_CENTS if plan_code == 'monthly' else YEARLY_PRICE_CENTS
    payload = PayFastService.build_subscription_payload(current_user, plan_code, amount_cents)

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
    payload = request.form.to_dict() or {}
    valid, reason = PayFastService.validate_itn(payload)
    if not valid:
        return jsonify({'message': 'Invalid'}), 400

    # Extract important fields
    custom_str1 = payload.get('custom_str1')  # we could send user_id here in future
    pf_payment_id = payload.get('pf_payment_id')
    payment_status = payload.get('payment_status', '').lower()  # COMPLETE, FAILED, PENDING
    amount_gross = payload.get('amount_gross') or payload.get('amount')

    # TODO: map back to user/subscription via reference fields
    # For now, acknowledge
    return jsonify({'message': 'OK'}), 200


@subscriptions_bp.route('/toggle-enforcement', methods=['POST'])
def toggle_enforcement():
    data = request.get_json() or {}
    enabled = bool(data.get('enabled'))
    current_app.config['ENFORCE_PAYMENT_AFTER_TRIAL'] = enabled
    return jsonify({'enforce_payment_after_trial': enabled})


