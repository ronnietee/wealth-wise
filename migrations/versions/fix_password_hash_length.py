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
    try:
        user_columns = {col['name']: col for col in inspector.get_columns('user')}
        if 'password_hash' in user_columns:
            # Try to get the length - PostgreSQL returns it differently
            col_type = str(user_columns['password_hash']['type'])
            if 'VARCHAR(120)' in col_type or 'character varying(120)' in col_type.lower():
                with op.batch_alter_table('user', schema=None) as batch_op:
                    batch_op.alter_column('password_hash',
                                          existing_type=sa.String(length=120),
                                          type_=sa.String(length=255),
                                          existing_nullable=False)
    except Exception as e:
        # If check fails, try to alter anyway (idempotent)
        try:
            with op.batch_alter_table('user', schema=None) as batch_op:
                batch_op.alter_column('password_hash',
                                      existing_type=sa.String(length=120),
                                      type_=sa.String(length=255),
                                      existing_nullable=False)
        except Exception:
            # Column might already be correct, skip
            pass
    
    # Check if email_verification.verified column exists
    try:
        email_verification_columns = [col['name'] for col in inspector.get_columns('email_verification')]
        if 'verified' not in email_verification_columns:
            with op.batch_alter_table('email_verification', schema=None) as batch_op:
                batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True, server_default='0'))
    except Exception as e:
        # If table doesn't exist or check fails, try to add column anyway
        try:
            with op.batch_alter_table('email_verification', schema=None) as batch_op:
                batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True, server_default='0'))
        except Exception:
            # Column might already exist, skip
            pass
    
    # Check if token needs unique constraint
    try:
        email_verification_indexes = [idx['name'] for idx in inspector.get_indexes('email_verification')]
        constraints = [con['name'] for con in inspector.get_unique_constraints('email_verification')]
        if 'uq_email_verification_token' not in email_verification_indexes and 'uq_email_verification_token' not in constraints:
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

