"""Merge multiple migration heads

Revision ID: a4fe67ffab43
Revises: 69fb2271b36e, b8c0e444f8af
Create Date: 2025-10-12 15:06:01.313255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4fe67ffab43'
down_revision = ('69fb2271b36e', 'b8c0e444f8af')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
