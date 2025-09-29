"""
Script para crear la tabla de control de generación
"""

import os
import sys
from datetime import datetime

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from app import create_app
from app.extensions import db


def crear_tabla_control():
    """Crear la tabla de control de generación"""
    app = create_app()

    with app.app_context():
        print("🛠️ CREANDO TABLA DE CONTROL DE GENERACIÓN")
        print("=" * 50)

        # Crear tabla directamente con SQL
        try:
            db.engine.execute(
                """
                CREATE TABLE IF NOT EXISTS control_generacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_generacion DATE NOT NULL UNIQUE,
                    tipo_generacion VARCHAR(20) NOT NULL,
                    timestamp_generacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ordenes_generadas INTEGER DEFAULT 0,
                    usuario_manual VARCHAR(100),
                    detalles TEXT
                )
            """
            )

            # Crear índice
            db.engine.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_control_fecha 
                ON control_generacion(fecha_generacion)
            """
            )

            db.session.commit()
            print("✅ Tabla 'control_generacion' creada exitosamente")

            # Verificar que se creó
            result = db.engine.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='control_generacion'"
            )
            if result.fetchone():
                print("✅ Tabla verificada en la base de datos")
            else:
                print("❌ Error: Tabla no encontrada después de la creación")

        except Exception as e:
            print(f"❌ Error al crear tabla: {e}")
            db.session.rollback()


if __name__ == "__main__":
    crear_tabla_control()
