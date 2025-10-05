"""
Script de migración para aumentar el tamaño del campo dias_semana
De VARCHAR(50) a VARCHAR(200) para soportar múltiples días
"""

import os
import sys

# Configurar el path para imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db


def migrate_dias_semana_field():
    """Aumenta el límite del campo dias_semana de 50 a 200 caracteres"""

    app = create_app()

    with app.app_context():
        try:
            print("🔧 Iniciando migración del campo dias_semana...")

            # Ejecutar ALTER TABLE para PostgreSQL
            sql = """
            ALTER TABLE plan_mantenimiento 
            ALTER COLUMN dias_semana TYPE VARCHAR(200);
            """

            db.session.execute(db.text(sql))
            db.session.commit()

            print("✅ Campo dias_semana actualizado exitosamente a VARCHAR(200)")
            print("📊 Verificando cambio...")

            # Verificar el cambio
            verify_sql = """
            SELECT column_name, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'plan_mantenimiento' 
            AND column_name = 'dias_semana';
            """

            result = db.session.execute(db.text(verify_sql)).fetchone()
            if result:
                print(
                    f"✅ Verificación: {result[0]} - Longitud máxima: {result[1]} caracteres"
                )

            return True

        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    success = migrate_dias_semana_field()
    sys.exit(0 if success else 1)
