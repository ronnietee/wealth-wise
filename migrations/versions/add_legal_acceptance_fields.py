"""add legal acceptance fields to user

Revision ID: add_legal_acceptance
Revises: add_admin_role
Create Date: 2025-01-XX
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_legal_acceptance'
down_revision = 'add_admin_role'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('terms_accepted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        batch_op.add_column(sa.Column('privacy_policy_accepted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        batch_op.add_column(sa.Column('terms_accepted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('privacy_policy_accepted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('terms_version', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('privacy_policy_version', sa.String(50), nullable=True))


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('terms_version')
        batch_op.drop_column('privacy_policy_version')
        batch_op.drop_column('privacy_policy_accepted_at')
        batch_op.drop_column('terms_accepted_at')
        batch_op.drop_column('privacy_policy_accepted')
        batch_op.drop_column('terms_accepted')

