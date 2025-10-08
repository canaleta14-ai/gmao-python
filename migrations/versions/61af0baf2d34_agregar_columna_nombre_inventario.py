"""Agregar columna 'nombre' a la tabla inventario

Revision ID: 61af0baf2d34
Revises: e3d9f2a7a8b1
Create Date: 2025-10-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "61af0baf2d34"
down_revision = "e3d9f2a7a8b1"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = inspect(bind)

    # Detectar esquema para Postgres
    schema = "public" if dialect in ("postgresql", "postgres") else None

    # Obtener columnas existentes
    existing = set(
        [col["name"] for col in inspector.get_columns("inventario", schema=schema)]
    )

    # Agregar columna 'nombre' si no existe
    if "nombre" not in existing:
        op.add_column(
            "inventario",
            sa.Column("nombre", sa.String(length=100), nullable=True),
            schema=schema,
        )


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = inspect(bind)
    schema = "public" if dialect in ("postgresql", "postgres") else None

    # Solo eliminar si existe
    existing = set(
        [col["name"] for col in inspector.get_columns("inventario", schema=schema)]
    )
    if "nombre" in existing:
        op.drop_column("inventario", "nombre", schema=schema)