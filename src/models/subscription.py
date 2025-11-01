"""
Subscription and payment models.
"""

from datetime import datetime
from ..extensions import db


class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plan'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # monthly, yearly
    name = db.Column(db.String(100), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default='ZAR', nullable=False)
    interval = db.Column(db.String(20), nullable=False)  # month, year
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscription(db.Model):
    __tablename__ = 'subscription'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    plan_code = db.Column(db.String(50), db.ForeignKey('subscription_plan.code'), nullable=False)
    status = db.Column(db.String(30), default='trial')  # trial, active, past_due, cancelled
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    cancel_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    payfast_subscription_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to User is defined via backref in User model


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id', ondelete='SET NULL'), nullable=True)
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default='ZAR', nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, paid, failed, refunded
    gateway = db.Column(db.String(30), default='payfast')
    gateway_reference = db.Column(db.String(255), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships - User relationship is defined via backref in User model
    subscription = db.relationship('Subscription', backref='payments', lazy='select')


