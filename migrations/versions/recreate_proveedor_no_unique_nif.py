"""
Recrear la tabla proveedor sin restricción única en nif (SQLite).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'recreate_proveedor_no_unique_nif'
down_revision = 'a38c420809de'
branch_labels = None
depends_on = None

def upgrade():
    # Renombrar la tabla actual
    op.execute('ALTER TABLE proveedor RENAME TO proveedor_old;')
    # Crear la nueva tabla sin restricción única
    op.create_table(
        'proveedor',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('nif', sa.String(20), nullable=True),
        sa.Column('direccion', sa.String(200), nullable=True),
        sa.Column('contacto', sa.String(100), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('cuenta_contable', sa.String(50), nullable=True),
        sa.Column('estado', sa.String(20), nullable=True)
    )
    # Copiar los datos
    op.execute('INSERT INTO proveedor (id, nombre, nif, direccion, contacto, email, cuenta_contable, estado) SELECT id, nombre, nif, direccion, contacto, email, cuenta_contable, estado FROM proveedor_old;')
    # Eliminar la tabla antigua
    op.execute('DROP TABLE proveedor_old;')

def downgrade():
    pass
