"""
Eliminar el índice único de nif en la tabla proveedor (SQLite).
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'remove_unique_nif_proveedor'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Eliminar el índice único si existe (SQLite)
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX IF EXISTS ix_proveedor_nif;")
        op.execute("DROP INDEX IF EXISTS proveedor_nif_key;")

def downgrade():
    # No se vuelve a crear el índice único
    pass
