from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate_activos_add_activo():
    """Agregar columna activo a la tabla activo"""
    app = create_app()
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text("PRAGMA table_info(activo)"))
            columns = [row[1] for row in result.fetchall()]

            if "activo" not in columns:
                # Agregar columna activo con valor por defecto True
                db.session.execute(
                    text("ALTER TABLE activo ADD COLUMN activo BOOLEAN DEFAULT 1")
                )
                db.session.commit()
                print("✅ Columna activo agregada exitosamente a la tabla activo")
            else:
                print("ℹ️ La columna activo ya existe en la tabla activo")

        except Exception as e:
            print(f"❌ Error al agregar columna activo: {e}")
            db.session.rollback()


if __name__ == "__main__":
    migrate_activos_add_activo()


if __name__ == "__main__":
    migrate_activos_add_activo()
