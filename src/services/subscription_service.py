"""
Subscription orchestration: plans, trials, status checks, and PayFast interactions.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from ..extensions import db
from ..models import User
from ..models.subscription import SubscriptionPlan, Subscription, Payment


MONTHLY_PRICE_CENTS = 3500
YEARLY_PRICE_CENTS = 40000


class SubscriptionService:
    @staticmethod
    def seed_default_plans(currency: str = 'ZAR') -> None:
        existing = {p.code: p for p in SubscriptionPlan.query.all()}
        if 'monthly' not in existing:
            db.session.add(SubscriptionPlan(code='monthly', name='Monthly', price_cents=MONTHLY_PRICE_CENTS, currency=currency, interval='month'))
        if 'yearly' not in existing:
            db.session.add(SubscriptionPlan(code='yearly', name='Yearly', price_cents=YEARLY_PRICE_CENTS, currency=currency, interval='year'))
        db.session.commit()

    @staticmethod
    def start_trial(user: User, plan_code: str, trial_days: int) -> Subscription:
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=trial_days)
        user.trial_start = trial_start
        user.trial_end = trial_end
        user.subscription_status = 'trial'
        user.subscription_plan = plan_code
        db.session.flush()
        sub = Subscription(
            user_id=user.id,
            plan_code=plan_code,
            status='trial',
            started_at=trial_start,
            current_period_start=trial_start,
            current_period_end=trial_end,
        )
        db.session.add(sub)
        db.session.commit()
        return sub

    @staticmethod
    def activate_subscription(user: User, subscription: Subscription, next_billing_at: Optional[datetime] = None, gateway_sub_id: Optional[str] = None):
        subscription.status = 'active'
        user.subscription_status = 'active'
        user.next_billing_at = next_billing_at
        if gateway_sub_id:
            subscription.payfast_subscription_id = gateway_sub_id
            user.payfast_subscription_id = gateway_sub_id
        db.session.commit()

    @staticmethod
    def record_payment(user: User, subscription: Optional[Subscription], amount_cents: int, currency: str, status: str, gateway_ref: Optional[str] = None):
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id if subscription else None,
            amount_cents=amount_cents,
            currency=currency,
            status=status,
            gateway='payfast',
            gateway_reference=gateway_ref
        )
        if status == 'paid':
            payment.paid_at = datetime.utcnow()
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def check_access(user: User, enforce: bool) -> Tuple[bool, str]:
        now = datetime.utcnow()
        status = (user.subscription_status or 'trial').lower()
        if status == 'active':
            return True, 'active'
        if status == 'trial' and (user.trial_end is None or now <= user.trial_end or not enforce):
            return True, 'trial'
        if not enforce:
            return True, 'not_enforced'
        return False, 'blocked'


