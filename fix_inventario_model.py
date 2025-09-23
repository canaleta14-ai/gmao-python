#!/usr/bin/env python3
"""
Script para actualizar la referencia del modelo Inventario a la nueva tabla
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.extensions import db
from sqlalchemy import text


def fix_inventario_model():
    app = create_app()

    with app.app_context():
        try:
            print("🔄 Corrigiendo referencias del modelo Inventario...")

            # Renombrar tabla antigua a inventario_old
            try:
                db.session.execute(
                    text("ALTER TABLE inventario RENAME TO inventario_old;")
                )
                print("✅ Tabla inventario renombrada a inventario_old")
            except Exception as e:
                if "no such table" in str(e).lower():
                    print("ℹ️  Tabla inventario no existe o ya fue renombrada")
                else:
                    print(f"⚠️  Error al renombrar tabla: {e}")

            # Renombrar nueva tabla para que use el nombre correcto
            try:
                db.session.execute(
                    text("ALTER TABLE inventario_nuevo RENAME TO inventario;")
                )
                print("✅ Tabla inventario_nuevo renombrada a inventario")
            except Exception as e:
                if "no such table" in str(e).lower():
                    print("⚠️  Tabla inventario_nuevo no existe")
                else:
                    print(f"⚠️  Error al renombrar tabla nueva: {e}")

            # Confirmar cambios
            db.session.commit()
            print("✅ Referencias del modelo actualizadas correctamente")

            # Verificar estructura de la nueva tabla
            result = db.session.execute(text("PRAGMA table_info(inventario);"))
            columns = result.fetchall()
            print(f"\n📋 Estructura de la tabla inventario ({len(columns)} columnas):")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la corrección: {e}")
            raise e


if __name__ == "__main__":
    fix_inventario_model()
