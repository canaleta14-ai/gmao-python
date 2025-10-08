"""Asegurar columnas del modelo Inventario en la tabla inventario

Revision ID: e3d9f2a7a8b1
Revises: 499968d1e362
Create Date: 2025-10-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "e3d9f2a7a8b1"
down_revision = "499968d1e362"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = inspect(bind)

    # Detectar esquema para Postgres
    schema = "public" if dialect in ("postgresql", "postgres") else None

    existing = set(
        [col["name"] for col in inspector.get_columns("inventario", schema=schema)]
    )

    def add_if_missing(colname, type_, nullable=True, server_default=None):
        if colname not in existing:
            op.add_column(
                "inventario",
                sa.Column(colname, type_, nullable=nullable, server_default=server_default),
                schema=schema,
            )

    # Campos básicos
    add_if_missing("codigo", sa.String(length=50), nullable=False)
    add_if_missing("descripcion", sa.String(length=200), nullable=True)

    # Campos simplificados esperados por tests
    add_if_missing("nombre", sa.String(length=100), nullable=True)
    add_if_missing("cantidad", sa.Integer(), nullable=True)
    add_if_missing("cantidad_minima", sa.Integer(), nullable=True)
    add_if_missing("unidad", sa.String(length=20), nullable=True)

    # Relación con categoría
    add_if_missing("categoria_id", sa.Integer(), nullable=True)

    # Compatibilidad hacia atrás
    add_if_missing("categoria", sa.String(length=100), nullable=True)
    add_if_missing("subcategoria", sa.String(length=100), nullable=True)
    add_if_missing("ubicacion", sa.String(length=100), nullable=True)

    # Stock
    add_if_missing("stock_actual", sa.Numeric(10, 2), nullable=True)
    add_if_missing("stock_minimo", sa.Numeric(10, 2), nullable=True)
    add_if_missing("stock_maximo", sa.Numeric(10, 2), nullable=True)
    add_if_missing("unidad_medida", sa.String(length=20), nullable=True)

    # Precios / costos
    add_if_missing("precio_unitario", sa.Numeric(10, 2), nullable=True)
    add_if_missing("precio_promedio", sa.Numeric(10, 2), nullable=True)
    add_if_missing("precio", sa.Numeric(10, 2), nullable=True)

    # Proveedor
    add_if_missing("proveedor_principal", sa.String(length=100), nullable=True)

    # Contable
    add_if_missing("cuenta_contable_compra", sa.String(length=20), nullable=True)
    add_if_missing("grupo_contable", sa.String(length=10), nullable=True)

    # Control
    add_if_missing("critico", sa.Boolean(), nullable=True)
    add_if_missing("activo", sa.Boolean(), nullable=True)

    # Otros
    add_if_missing("observaciones", sa.Text(), nullable=True)

    # Metadatos
    add_if_missing("fecha_creacion", sa.DateTime(), nullable=True)
    add_if_missing("fecha_actualizacion", sa.DateTime(), nullable=True)

    # FK categoria_id (si existe tabla categoria)
    try:
        categoria_cols = inspector.get_columns("categoria", schema=schema)
        if categoria_cols:
            # Crear FK si aún no existe
            existing_fks = inspector.get_foreign_keys("inventario", schema=schema)
            fk_names = {fk.get("name") for fk in existing_fks}
            if "fk_inventario_categoria" not in fk_names:
                op.create_foreign_key(
                    "fk_inventario_categoria",
                    "inventario",
                    "categoria",
                    ["categoria_id"],
                    ["id"],
                    source_schema=schema,
                    referent_schema=schema,
                )
    except Exception:
        # No fallar la migración por FKs
        pass


def downgrade():
    # No se eliminan columnas para evitar pérdida de datos
    pass