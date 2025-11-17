"""Fix password_hash column length

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
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                              existing_type=sa.String(length=120),
                              type_=sa.String(length=255),
                              existing_nullable=False)


def downgrade():
    # Revert to shorter length (not recommended if you have existing users)
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                              existing_type=sa.String(length=255),
                              type_=sa.String(length=120),
                              existing_nullable=False)

