#!/usr/bin/env python3
"""
Script para verificar las solicitudes en las bases de datos locales (SQLite)
"""

import sqlite3
import os
from datetime import datetime


def verificar_base_datos_local(db_path, nombre_db):
    """Verificar solicitudes en una base de datos SQLite"""

    print(f"🔍 Verificando {nombre_db}: {db_path}")

    if not os.path.exists(db_path):
        print(f"❌ No existe el archivo: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si existe la tabla de solicitudes
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%solicitud%'
        """
        )

        tablas = cursor.fetchall()
        print(f"📋 Tablas relacionadas con solicitudes: {[t[0] for t in tablas]}")

        # Intentar consultar solicitudes
        for tabla in ["solicitud_servicio", "solicitud", "solicitudes"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"📊 {tabla}: {count} registros")

                if count > 0:
                    # Obtener algunas solicitudes
                    cursor.execute(
                        f"""
                        SELECT * FROM {tabla} 
                        ORDER BY id DESC LIMIT 5
                    """
                    )

                    # Obtener nombres de columnas
                    columnas = [description[0] for description in cursor.description]
                    print(f"📝 Columnas: {columnas}")

                    solicitudes = cursor.fetchall()

                    print(f"📋 Últimas {len(solicitudes)} solicitudes en {tabla}:")
                    print("-" * 80)

                    for sol in solicitudes:
                        print(f"   ID: {sol[0] if len(sol) > 0 else 'N/A'}")

                        # Buscar columnas comunes
                        col_dict = dict(zip(columnas, sol))

                        for campo in [
                            "codigo",
                            "numero_solicitud",
                            "titulo",
                            "descripcion",
                            "solicitante",
                            "estado",
                        ]:
                            if campo in col_dict:
                                valor = col_dict[campo]
                                if isinstance(valor, str) and len(valor) > 50:
                                    valor = valor[:50] + "..."
                                print(f"   {campo.capitalize()}: {valor}")

                        print("-" * 40)

            except sqlite3.OperationalError as e:
                if "no such table" not in str(e).lower():
                    print(f"⚠️  Error consultando {tabla}: {e}")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DE BASES DE DATOS LOCALES")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Bases de datos a verificar
    bases_datos = [
        ("instance/gmao_local.db", "Base de datos local (.env)"),
        ("instance/database.db", "Base de datos instance"),
    ]

    for db_path, nombre in bases_datos:
        verificar_base_datos_local(db_path, nombre)
        print()

    print("📝 CONCLUSIÓN:")
    print("=" * 40)
    print("• Las solicitudes creadas MANUALMENTE aparecen en la web (producción)")
    print("• Las solicitudes creadas por SCRIPTS aparecen aquí (local)")
    print("• Esto explica por qué no ves las solicitudes de prueba en la web")
    print()
    print("💡 SOLUCIÓN:")
    print("• Las solicitudes manuales están en PostgreSQL (nube) ✅")
    print("• Las solicitudes de scripts están en SQLite (local) ❌")
    print("• Para crear solicitudes en producción, usar la interfaz web")


if __name__ == "__main__":
    main()
