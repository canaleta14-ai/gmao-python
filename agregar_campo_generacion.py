"""
Script para agregar el campo de generación automática
"""

import os
import sys

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from app import create_app
from app.extensions import db
from sqlalchemy import text


def agregar_campo_generacion_automatica():
    """Agregar campo generacion_automatica a la tabla plan_mantenimiento"""
    app = create_app()

    with app.app_context():
        print("🛠️ AGREGANDO CAMPO GENERACIÓN AUTOMÁTICA")
        print("=" * 50)

        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text("PRAGMA table_info(plan_mantenimiento)"))
            columnas = [row[1] for row in result.fetchall()]

            if "generacion_automatica" in columnas:
                print("✅ La columna 'generacion_automatica' ya existe")
                return

            # Agregar la columna
            db.session.execute(
                text(
                    """
                ALTER TABLE plan_mantenimiento 
                ADD COLUMN generacion_automatica BOOLEAN DEFAULT 1
            """
                )
            )

            db.session.commit()
            print("✅ Campo 'generacion_automatica' agregado exitosamente")

            # Verificar que se agregó
            result = db.session.execute(text("PRAGMA table_info(plan_mantenimiento)"))
            columnas = [row[1] for row in result.fetchall()]

            if "generacion_automatica" in columnas:
                print("✅ Campo verificado en la base de datos")

                # Actualizar todos los planes existentes para que tengan generación automática activada
                db.session.execute(
                    text(
                        """
                    UPDATE plan_mantenimiento 
                    SET generacion_automatica = 1 
                    WHERE generacion_automatica IS NULL
                """
                    )
                )
                db.session.commit()
                print(
                    "✅ Planes existentes actualizados con generación automática activada"
                )

            else:
                print("❌ Error: Campo no encontrado después de la creación")

        except Exception as e:
            print(f"❌ Error al agregar campo: {e}")
            db.session.rollback()


if __name__ == "__main__":
    agregar_campo_generacion_automatica()
