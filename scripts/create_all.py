"""
Inicializa la base de datos creando todas las tablas definidas en los modelos.

Uso previsto: entornos locales con SQLite, para bootstrap inicial cuando
las migraciones existentes no incluyen un "base" que cree tablas.

Luego de ejecutarlo, se recomienda ejecutar:
  flask db stamp head
para que Alembic considere la base de datos en la última revisión.
"""

import os
import sys

# Añadir el directorio raíz del proyecto al sys.path para poder importar 'app'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.factory import create_app
from app.extensions import db


def ensure_instance_dir(app):
    # Asegura que exista el directorio 'instance' para SQLite
    try:
        instance_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "instance"
        )
        instance_path = os.path.abspath(instance_path)
        os.makedirs(instance_path, exist_ok=True)
        print(f"[OK] Directorio instance verificado: {instance_path}")
    except Exception as e:
        print(f"[WARN] No se pudo verificar/crear 'instance': {e}")


def main():
    app = create_app("development")
    ensure_instance_dir(app)
    with app.app_context():
        db.create_all()
        print("[OK] Todas las tablas creadas (db.create_all)")


if __name__ == "__main__":
    main()
