#!/usr/bin/env python3
"""
Script para migrar la base de datos con los nuevos campos del modelo PlanMantenimiento
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.extensions import db
from sqlalchemy import text


def migrate_database():
    app = create_app()

    with app.app_context():
        try:
            # Agregar los nuevos campos a la tabla plan_mantenimiento
            alter_commands = [
                "ALTER TABLE plan_mantenimiento ADD COLUMN tipo_frecuencia VARCHAR(20);",
                "ALTER TABLE plan_mantenimiento ADD COLUMN intervalo_semanas INTEGER;",
                "ALTER TABLE plan_mantenimiento ADD COLUMN dias_semana VARCHAR(50);",
                "ALTER TABLE plan_mantenimiento ADD COLUMN tipo_mensual VARCHAR(20);",
                "ALTER TABLE plan_mantenimiento ADD COLUMN dia_mes INTEGER;",
                "ALTER TABLE plan_mantenimiento ADD COLUMN semana_mes INTEGER;",
                "ALTER TABLE plan_mantenimiento ADD COLUMN dia_semana_mes VARCHAR(20);",
                "ALTER TABLE plan_mantenimiento ADD COLUMN intervalo_meses INTEGER;",
                "ALTER TABLE plan_mantenimiento ADD COLUMN frecuencia_personalizada TEXT;",
            ]

            for command in alter_commands:
                try:
                    db.session.execute(text(command))
                    print(f"✓ Ejecutado: {command}")
                except Exception as e:
                    if (
                        "duplicate column name" in str(e).lower()
                        or "already exists" in str(e).lower()
                    ):
                        print(f"⚠ Columna ya existe: {command}")
                    else:
                        print(f"✗ Error: {command} - {e}")

            db.session.commit()
            print("\n✅ Migración completada exitosamente")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la migración: {e}")


if __name__ == "__main__":
    migrate_database()
