"""add admin role to user

Revision ID: add_admin_role
Revises: 7b2f3a1c2c1e
Create Date: 2025-01-01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_admin_role'
down_revision = '7b2f3a1c2c1e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('is_admin')

