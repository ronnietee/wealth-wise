"""add period_type to recurring sources and allocations

Revision ID: add_period_type_recurring
Revises: 7b2f3a1c2c1e
Create Date: 2025-01-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a20ca1420b20'
down_revision = '7b2f3a1c2c1e'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns already exist (they may have been created by initial migration)
    # This migration is idempotent - safe to run even if columns already exist
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check recurring_income_source table
    recurring_income_columns = [col['name'] for col in inspector.get_columns('recurring_income_source')]
    if 'period_type' not in recurring_income_columns:
        with op.batch_alter_table('recurring_income_source') as batch_op:
            batch_op.add_column(sa.Column('period_type', sa.String(length=20), nullable=False, server_default='monthly'))
    
    # Check recurring_budget_allocation table
    recurring_allocation_columns = [col['name'] for col in inspector.get_columns('recurring_budget_allocation')]
    if 'period_type' not in recurring_allocation_columns:
        with op.batch_alter_table('recurring_budget_allocation') as batch_op:
            batch_op.add_column(sa.Column('period_type', sa.String(length=20), nullable=False, server_default='monthly'))


def downgrade():
    with op.batch_alter_table('recurring_budget_allocation') as batch_op:
        batch_op.drop_column('period_type')
    
    with op.batch_alter_table('recurring_income_source') as batch_op:
        batch_op.drop_column('period_type')

