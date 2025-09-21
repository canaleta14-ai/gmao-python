"""
Script para actualizar la base de datos con las nuevas tablas de manuales
"""

from app.factory import create_app
from app.extensions import db


def update_db():
    """Actualizar base de datos con nuevas tablas"""
    app = create_app()
    with app.app_context():
        # Crear todas las tablas (incluyendo las nuevas)
        db.create_all()
        print("Base de datos actualizada con las tablas de manuales")


if __name__ == "__main__":
    update_db()
