"""Actualizar estructura tabla proveedores - aplicado manualmente

Revision ID: 94b8fbf32a3b
Revises: recreate_proveedor_no_unique_nif
Create Date: 2025-10-18 18:54:39.255329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94b8fbf32a3b'
down_revision = 'recreate_proveedor_no_unique_nif'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
