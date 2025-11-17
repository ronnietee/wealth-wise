"""merge multiple heads

Revision ID: merge_heads_001
Revises: add_legal_acceptance, a20ca1420b20
Create Date: 2025-11-16 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_001'
down_revision = ('add_legal_acceptance', 'a20ca1420b20')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration - no schema changes needed
    # Both branches are now merged into a single head
    # The migrations from both branches are already applied
    pass


def downgrade():
    # This is a merge migration - no schema changes needed
    pass

