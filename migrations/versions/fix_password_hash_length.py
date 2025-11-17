"""Fix password_hash column length and email_verification table

Revision ID: fix_password_hash_len
Revises: merge_heads_001
Create Date: 2025-11-17 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_password_hash_len'
down_revision = 'merge_heads_001'
branch_labels = None
depends_on = None


def upgrade():
    # Alter password_hash column to allow longer hashes (scrypt can be 144+ chars)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if password_hash needs to be updated
    user_columns = {col['name']: col for col in inspector.get_columns('user')}
    if 'password_hash' in user_columns and user_columns['password_hash']['type'].length == 120:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.alter_column('password_hash',
                                  existing_type=sa.String(length=120),
                                  type_=sa.String(length=255),
                                  existing_nullable=False)
    
    # Check if email_verification.verified column exists
    email_verification_columns = [col['name'] for col in inspector.get_columns('email_verification')]
    if 'verified' not in email_verification_columns:
        with op.batch_alter_table('email_verification', schema=None) as batch_op:
            batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True, server_default='0'))
    
    # Check if token needs unique constraint
    email_verification_indexes = [idx['name'] for idx in inspector.get_indexes('email_verification')]
    if 'uq_email_verification_token' not in email_verification_indexes:
        # Check if unique constraint exists
        try:
            op.create_unique_constraint('uq_email_verification_token', 'email_verification', ['token'])
        except Exception:
            # Constraint might already exist, skip
            pass


def downgrade():
    # Revert password_hash (not recommended if you have existing users)
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                              existing_type=sa.String(length=255),
                              type_=sa.String(length=120),
                              existing_nullable=False)
    
    # Remove verified column
    with op.batch_alter_table('email_verification', schema=None) as batch_op:
        batch_op.drop_column('verified')

