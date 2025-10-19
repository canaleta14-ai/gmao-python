"""eliminar_campo_duplicado_fecha_movimiento_lote

Revision ID: 721658648421
Revises: 226ae0bc43a8
Create Date: 2025-10-18 23:13:33.811518

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "721658648421"
down_revision = "226ae0bc43a8"
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar columna duplicada fecha_movimiento
    # Mantenemos solo el campo "fecha" que tiene la misma funcionalidad
    op.execute(
        """
        ALTER TABLE movimiento_lote 
        DROP COLUMN IF EXISTS fecha_movimiento
    """
    )


def downgrade():
    # Restaurar columna en caso de rollback
    op.execute(
        """
        ALTER TABLE movimiento_lote 
        ADD COLUMN IF NOT EXISTS fecha_movimiento TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    """
    )
