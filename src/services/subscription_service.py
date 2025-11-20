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
        # Use more efficient queries - only check for specific plans
        monthly_exists = SubscriptionPlan.query.filter_by(code='monthly').first()
        yearly_exists = SubscriptionPlan.query.filter_by(code='yearly').first()
        
        if not monthly_exists:
            db.session.add(SubscriptionPlan(code='monthly', name='Monthly', price_cents=MONTHLY_PRICE_CENTS, currency=currency, interval='month'))
        if not yearly_exists:
            db.session.add(SubscriptionPlan(code='yearly', name='Yearly', price_cents=YEARLY_PRICE_CENTS, currency=currency, interval='year'))
        
        # Only commit if we added plans
        if not monthly_exists or not yearly_exists:
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
    def upgrade_subscription(user: User, subscription: Subscription, new_plan_code: str):
        """Upgrade subscription to a higher tier."""
        if not subscription:
            return False
        
        old_plan = subscription.plan_code
        subscription.plan_code = new_plan_code
        user.subscription_plan = new_plan_code
        
        # Update billing cycle if needed
        if old_plan == 'monthly' and new_plan_code == 'yearly':
            # Upgrade: extend period
            if subscription.current_period_end:
                remaining_days = (subscription.current_period_end - datetime.utcnow()).days
                subscription.current_period_end = datetime.utcnow() + timedelta(days=365 + remaining_days)
        elif old_plan == 'yearly' and new_plan_code == 'monthly':
            # Downgrade: adjust period
            if subscription.current_period_end:
                # Keep current period end, next billing will be monthly
                user.next_billing_at = subscription.current_period_end
        
        db.session.commit()
        return True
    
    @staticmethod
    def downgrade_subscription(user: User, subscription: Subscription, new_plan_code: str):
        """Downgrade subscription to a lower tier (takes effect at period end)."""
        if not subscription:
            return False
        
        # Mark for downgrade at period end
        subscription.plan_code = new_plan_code
        user.subscription_plan = new_plan_code
        # Status remains active until period end
        
        db.session.commit()
        return True
    
    @staticmethod
    def process_renewal(subscription: Subscription):
        """Process subscription renewal for recurring billing."""
        if not subscription or subscription.status != 'active':
            return False
        
        now = datetime.utcnow()
        
        # Check if renewal is due
        if subscription.current_period_end and now >= subscription.current_period_end:
            # Renew subscription
            if subscription.plan_code == 'monthly':
                next_period_start = subscription.current_period_end
                next_period_end = next_period_start + timedelta(days=30)
            elif subscription.plan_code == 'yearly':
                next_period_start = subscription.current_period_end
                next_period_end = next_period_start + timedelta(days=365)
            else:
                return False
            
            subscription.current_period_start = next_period_start
            subscription.current_period_end = next_period_end
            
            # Update user next billing
            from ..models import User
            user = subscription.user
            if user:
                user.next_billing_at = next_period_end
            
            db.session.commit()
            return True
        
        return False

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

    @staticmethod
    def cancel_subscription(user: User, subscription: Subscription, cancel_immediately: bool = False):
        """Cancel a subscription.
        
        Args:
            user: User model instance
            subscription: Subscription model instance
            cancel_immediately: If True, cancel now; if False, cancel at period end
        """
        if cancel_immediately:
            subscription.status = 'cancelled'
            subscription.cancelled_at = datetime.utcnow()
            user.subscription_status = 'cancelled'
        else:
            subscription.cancel_at = subscription.current_period_end
            subscription.status = 'active'  # Keep active until period end
            # User status remains active until period end
        db.session.commit()
        return subscription.cancel_at if not cancel_immediately else None

    @staticmethod
    def pause_subscription(user: User, subscription: Subscription):
        """Pause a subscription (set status to inactive)."""
        subscription.status = 'inactive'
        user.subscription_status = 'inactive'
        db.session.commit()

    @staticmethod
    def resume_subscription(user: User, subscription: Subscription):
        """Resume a paused subscription."""
        subscription.status = 'active'
        user.subscription_status = 'active'
        db.session.commit()

    @staticmethod
    def process_payfast_itn(payload: dict) -> Tuple[bool, Optional[User], Optional[Subscription], str]:
        """Process PayFast ITN payload and map to user/subscription.
        
        Returns:
            (success, user, subscription, message)
        """
        try:
            # Extract custom fields for mapping
            user_id_str = payload.get('custom_str1', '')
            subscription_id_str = payload.get('custom_int1', '')
            
            if not user_id_str:
                return False, None, None, 'Missing custom_str1 (user_id)'
            
            try:
                user_id = int(user_id_str)
                subscription_id = int(subscription_id_str) if subscription_id_str else None
            except ValueError:
                return False, None, None, 'Invalid user_id or subscription_id format'
            
            # Find user
            user = User.query.get(user_id)
            if not user:
                return False, None, None, f'User {user_id} not found'
            
            # Find subscription (if provided)
            subscription = None
            if subscription_id:
                subscription = Subscription.query.filter_by(
                    id=subscription_id,
                    user_id=user_id
                ).first()
                if not subscription:
                    # Fallback: find active subscription for user
                    subscription = Subscription.query.filter_by(
                        user_id=user_id,
                        status='trial'
                    ).order_by(Subscription.created_at.desc()).first()
            else:
                # Find latest active/trial subscription for user
                subscription = Subscription.query.filter_by(
                    user_id=user_id
                ).order_by(Subscription.created_at.desc()).first()
            
            return True, user, subscription, 'OK'
            
        except Exception as e:
            return False, None, None, f'Error processing ITN: {str(e)}'


