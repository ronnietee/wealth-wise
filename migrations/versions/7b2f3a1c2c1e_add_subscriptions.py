"""add subscriptions

Revision ID: 7b2f3a1c2c1e
Revises: 94aadecb5493
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b2f3a1c2c1e'
down_revision = '94aadecb5493'
branch_labels = None
depends_on = None


def upgrade():
    # User subscription columns
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('trial_start', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('trial_end', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('subscription_status', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('subscription_plan', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('next_billing_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('auto_renew', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('payfast_token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('payfast_subscription_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('billing_currency', sa.String(length=10), nullable=True))

    # Subscription plan table
    op.create_table(
        'subscription_plan',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='ZAR'),
        sa.Column('interval', sa.String(length=20), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Subscription table
    op.create_table(
        'subscription',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plan_code', sa.String(length=50), sa.ForeignKey('subscription_plan.code'), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('cancel_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('payfast_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Payment table
    op.create_table(
        'payment',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subscription_id', sa.Integer(), sa.ForeignKey('subscription.id', ondelete='SET NULL'), nullable=True),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='ZAR'),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('gateway', sa.String(length=30), nullable=True),
        sa.Column('gateway_reference', sa.String(length=255), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('payment')
    op.drop_table('subscription')
    op.drop_table('subscription_plan')
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('billing_currency')
        batch_op.drop_column('payfast_subscription_id')
        batch_op.drop_column('payfast_token')
        batch_op.drop_column('auto_renew')
        batch_op.drop_column('next_billing_at')
        batch_op.drop_column('subscription_plan')
        batch_op.drop_column('subscription_status')
        batch_op.drop_column('trial_end')
        batch_op.drop_column('trial_start')


