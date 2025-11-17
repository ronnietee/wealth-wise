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
    # Check if columns already exist (they may have been created by initial migration)
    # This migration is idempotent - safe to run even if columns/tables already exist
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Get existing columns in user table
    user_columns = [col['name'] for col in inspector.get_columns('user')]
    
    # Build list of columns to add (only if they don't exist)
    columns_to_add = []
    if 'trial_start' not in user_columns:
        columns_to_add.append(sa.Column('trial_start', sa.DateTime(), nullable=True))
    if 'trial_end' not in user_columns:
        columns_to_add.append(sa.Column('trial_end', sa.DateTime(), nullable=True))
    if 'subscription_status' not in user_columns:
        columns_to_add.append(sa.Column('subscription_status', sa.String(length=30), nullable=True))
    if 'subscription_plan' not in user_columns:
        columns_to_add.append(sa.Column('subscription_plan', sa.String(length=20), nullable=True))
    if 'next_billing_at' not in user_columns:
        columns_to_add.append(sa.Column('next_billing_at', sa.DateTime(), nullable=True))
    if 'auto_renew' not in user_columns:
        columns_to_add.append(sa.Column('auto_renew', sa.Boolean(), nullable=True))
    if 'payfast_token' not in user_columns:
        columns_to_add.append(sa.Column('payfast_token', sa.String(length=255), nullable=True))
    if 'payfast_subscription_id' not in user_columns:
        columns_to_add.append(sa.Column('payfast_subscription_id', sa.String(length=255), nullable=True))
    if 'billing_currency' not in user_columns:
        columns_to_add.append(sa.Column('billing_currency', sa.String(length=10), nullable=True))
    
    # Add columns only if there are any to add
    if columns_to_add:
        with op.batch_alter_table('user', schema=None) as batch_op:
            for col in columns_to_add:
                batch_op.add_column(col)

    # Check if tables exist before creating them
    existing_tables = inspector.get_table_names()
    
    # Subscription plan table
    if 'subscription_plan' not in existing_tables:
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
    if 'subscription' not in existing_tables:
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
    if 'payment' not in existing_tables:
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


