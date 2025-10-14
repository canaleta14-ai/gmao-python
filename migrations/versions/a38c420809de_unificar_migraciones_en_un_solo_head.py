"""Unificar migraciones en un solo head

Revision ID: a38c420809de
Revises: 6c136aef235c, remove_unique_nif_proveedor
Create Date: 2025-10-14 17:59:27.093515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a38c420809de'
down_revision = ('6c136aef235c', 'remove_unique_nif_proveedor')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
