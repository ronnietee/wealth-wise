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
    # Add period_type to recurring_income_source
    with op.batch_alter_table('recurring_income_source') as batch_op:
        batch_op.add_column(sa.Column('period_type', sa.String(length=20), nullable=False, server_default='monthly'))
    
    # Add period_type to recurring_budget_allocation
    with op.batch_alter_table('recurring_budget_allocation') as batch_op:
        batch_op.add_column(sa.Column('period_type', sa.String(length=20), nullable=False, server_default='monthly'))


def downgrade():
    with op.batch_alter_table('recurring_budget_allocation') as batch_op:
        batch_op.drop_column('period_type')
    
    with op.batch_alter_table('recurring_income_source') as batch_op:
        batch_op.drop_column('period_type')

