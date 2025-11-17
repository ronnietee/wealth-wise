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
    # Check if columns already exist (they may have been created by initial migration)
    # This migration is idempotent - safe to run even if columns already exist
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    user_columns = [col['name'] for col in inspector.get_columns('user')]
    
    # Build list of columns to add (only if they don't exist)
    columns_to_add = []
    if 'terms_accepted' not in user_columns:
        columns_to_add.append(sa.Column('terms_accepted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    if 'privacy_policy_accepted' not in user_columns:
        columns_to_add.append(sa.Column('privacy_policy_accepted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    if 'terms_accepted_at' not in user_columns:
        columns_to_add.append(sa.Column('terms_accepted_at', sa.DateTime(), nullable=True))
    if 'privacy_policy_accepted_at' not in user_columns:
        columns_to_add.append(sa.Column('privacy_policy_accepted_at', sa.DateTime(), nullable=True))
    if 'terms_version' not in user_columns:
        columns_to_add.append(sa.Column('terms_version', sa.String(50), nullable=True))
    if 'privacy_policy_version' not in user_columns:
        columns_to_add.append(sa.Column('privacy_policy_version', sa.String(50), nullable=True))
    
    # Add columns only if there are any to add
    if columns_to_add:
        with op.batch_alter_table('user') as batch_op:
            for col in columns_to_add:
                batch_op.add_column(col)


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('terms_version')
        batch_op.drop_column('privacy_policy_version')
        batch_op.drop_column('privacy_policy_accepted_at')
        batch_op.drop_column('terms_accepted_at')
        batch_op.drop_column('privacy_policy_accepted')
        batch_op.drop_column('terms_accepted')

