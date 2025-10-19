"""agregar_indices_busqueda_inventario

Revision ID: 226ae0bc43a8
Revises: 94b8fbf32a3b
Create Date: 2025-10-18 23:06:54.392651

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "226ae0bc43a8"
down_revision = "94b8fbf32a3b"
branch_labels = None
depends_on = None


def upgrade():
    # Crear índices para optimizar búsquedas con ILIKE
    # Estos índices mejoran el rendimiento de las búsquedas por código, descripción y categoría

    # Índice para búsquedas por código (ILIKE)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventario_codigo_ilike 
        ON inventario (LOWER(codigo) text_pattern_ops)
    """
    )

    # Índice para búsquedas por descripción (ILIKE)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventario_descripcion_ilike 
        ON inventario (LOWER(descripcion) text_pattern_ops)
    """
    )

    # Índice para búsquedas por categoría (ILIKE)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventario_categoria_ilike 
        ON inventario (LOWER(categoria) text_pattern_ops)
    """
    )

    # Índice para filtro por estado activo (usado frecuentemente)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventario_activo 
        ON inventario (activo)
    """
    )

    # Índice compuesto para filtros comunes (activo + categoria)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventario_activo_categoria 
        ON inventario (activo, categoria_id)
    """
    )

    # Índice para ordenamiento por código
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inventario_codigo_sort 
        ON inventario (codigo)
    """
    )


def downgrade():
    # Eliminar índices en orden inverso
    op.execute("DROP INDEX IF EXISTS idx_inventario_codigo_sort")
    op.execute("DROP INDEX IF EXISTS idx_inventario_activo_categoria")
    op.execute("DROP INDEX IF EXISTS idx_inventario_activo")
    op.execute("DROP INDEX IF EXISTS idx_inventario_categoria_ilike")
    op.execute("DROP INDEX IF EXISTS idx_inventario_descripcion_ilike")
    op.execute("DROP INDEX IF EXISTS idx_inventario_codigo_ilike")
