#!/usr/bin/env python3
"""
Script para verificar artículos de prueba en Google Cloud SQL (Producción)
"""

import os
import sys
from datetime import datetime

# Configurar variables de entorno para producción
os.environ.update(
    {
        "DB_TYPE": "postgresql",
        "DB_HOST": "/cloudsql/mantenimiento-470311:europe-southwest1:gmao-madrid-final",
        "DB_NAME": "gmao_production",
        "DB_USER": "postgres",
        "DB_PASSWORD": "GmaoMadrid2025!",
        "GOOGLE_CLOUD_PROJECT": "mantenimiento-470311",
    }
)

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def verificar_inventario_produccion():
    """Verificar inventario en la base de datos de producción"""

    from app import create_app
    from app.models import Inventario, db
    from sqlalchemy import text

    app = create_app()

    with app.app_context():
        print("🌐 VERIFICACIÓN DEL INVENTARIO EN PRODUCCIÓN")
        print("=" * 55)
        print("🔗 Conexión: Google Cloud SQL PostgreSQL")
        print(f"🏢 Proyecto: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
        print(f"🗄️  Base de datos: {os.environ.get('DB_NAME')}")
        print()

        try:
            # Probar conexión con consulta simple
            result = db.session.execute(text("SELECT COUNT(*) FROM inventario"))
            total_articulos = result.scalar()

            print(f"📊 Total de artículos en inventario: {total_articulos}")

            if total_articulos == 0:
                print("✅ El inventario está completamente vacío")
                return

            # Buscar artículos de prueba usando SQL directo
            result = db.session.execute(
                text(
                    """
                SELECT id, codigo, nombre, stock_actual 
                FROM inventario 
                WHERE LOWER(codigo) LIKE '%prueba%' 
                   OR LOWER(codigo) LIKE '%test%' 
                   OR LOWER(codigo) LIKE '%demo%'
                   OR LOWER(nombre) LIKE '%prueba%' 
                   OR LOWER(nombre) LIKE '%test%' 
                   OR LOWER(nombre) LIKE '%demo%'
                   OR codigo LIKE 'P-%' 
                   OR codigo LIKE 'T-%' 
                   OR codigo LIKE 'TEST-%' 
                   OR codigo LIKE 'DEMO-%'
                ORDER BY codigo
            """
                )
            )

            articulos_prueba = result.fetchall()

            print(f"🧪 Artículos de prueba encontrados: {len(articulos_prueba)}")

            if len(articulos_prueba) > 0:
                print("\n📋 ARTÍCULOS DE PRUEBA EN PRODUCCIÓN:")
                print("-" * 70)
                print(f"{'ID':3s} | {'Código':15s} | {'Nombre':30s} | {'Stock':5s}")
                print("-" * 70)

                for row in articulos_prueba:
                    id_art, codigo, nombre, stock = row
                    codigo_str = codigo or "N/A"
                    nombre_str = (nombre or "N/A")[:30]
                    print(
                        f"{id_art:3d} | {codigo_str:15s} | {nombre_str:30s} | {stock:5d}"
                    )
                print("-" * 70)
            else:
                print("✅ No se encontraron artículos de prueba en producción")

            # Mostrar muestra de artículos normales
            result = db.session.execute(
                text(
                    """
                SELECT id, codigo, nombre, stock_actual 
                FROM inventario 
                WHERE id NOT IN (
                    SELECT id FROM inventario 
                    WHERE LOWER(codigo) LIKE '%prueba%' 
                       OR LOWER(codigo) LIKE '%test%' 
                       OR LOWER(codigo) LIKE '%demo%'
                       OR LOWER(nombre) LIKE '%prueba%' 
                       OR LOWER(nombre) LIKE '%test%' 
                       OR LOWER(nombre) LIKE '%demo%'
                       OR codigo LIKE 'P-%' 
                       OR codigo LIKE 'T-%' 
                       OR codigo LIKE 'TEST-%' 
                       OR codigo LIKE 'DEMO-%'
                )
                ORDER BY id
                LIMIT 5
            """
                )
            )

            articulos_normales = result.fetchall()

            if len(articulos_normales) > 0:
                print(f"\n📋 MUESTRA DE ARTÍCULOS NORMALES (primeros 5):")
                print("-" * 70)
                print(f"{'ID':3s} | {'Código':15s} | {'Nombre':30s} | {'Stock':5s}")
                print("-" * 70)

                for row in articulos_normales:
                    id_art, codigo, nombre, stock = row
                    codigo_str = codigo or "N/A"
                    nombre_str = (nombre or "N/A")[:30]
                    print(
                        f"{id_art:3d} | {codigo_str:15s} | {nombre_str:30s} | {stock:5d}"
                    )
                print("-" * 70)

        except Exception as e:
            print(f"❌ ERROR DE CONEXIÓN: {str(e)}")
            print("   Posibles causas:")
            print("   - No hay conexión a Google Cloud SQL")
            print("   - Credenciales incorrectas")
            print("   - Firewall bloqueando la conexión")
            print("   - El script debe ejecutarse desde Google Cloud")


def eliminar_articulos_prueba_produccion():
    """Eliminar artículos de prueba de la base de datos de producción"""

    print("\n" + "=" * 60)
    print("🗑️  ELIMINACIÓN DE ARTÍCULOS DE PRUEBA EN PRODUCCIÓN")
    print("=" * 60)

    respuesta = input(
        "⚠️  ¿Está SEGURO de que quiere eliminar artículos de PRODUCCIÓN? (escriba 'CONFIRMO'): "
    )

    if respuesta != "CONFIRMO":
        print("❌ Operación cancelada por seguridad.")
        return

    from app import create_app
    from app.models import db
    from sqlalchemy import text

    app = create_app()

    with app.app_context():
        try:
            # Buscar artículos de prueba
            result = db.session.execute(
                text(
                    """
                SELECT id, codigo, nombre 
                FROM inventario 
                WHERE LOWER(codigo) LIKE '%prueba%' 
                   OR LOWER(codigo) LIKE '%test%' 
                   OR LOWER(codigo) LIKE '%demo%'
                   OR LOWER(nombre) LIKE '%prueba%' 
                   OR LOWER(nombre) LIKE '%test%' 
                   OR LOWER(nombre) LIKE '%demo%'
                   OR codigo LIKE 'P-%' 
                   OR codigo LIKE 'T-%' 
                   OR codigo LIKE 'TEST-%' 
                   OR codigo LIKE 'DEMO-%'
            """
                )
            )

            articulos_prueba = result.fetchall()

            if len(articulos_prueba) == 0:
                print("✅ No hay artículos de prueba para eliminar.")
                return

            print(f"🗑️  Eliminando {len(articulos_prueba)} artículos de prueba...")

            eliminados = 0
            for row in articulos_prueba:
                id_art, codigo, nombre = row
                try:
                    db.session.execute(
                        text("DELETE FROM inventario WHERE id = :id"), {"id": id_art}
                    )
                    print(f"   ✅ Eliminado ID {id_art}: {codigo} - {nombre}")
                    eliminados += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando ID {id_art}: {str(e)}")

            # Confirmar cambios
            if eliminados > 0:
                db.session.commit()
                print(f"\n✅ ELIMINACIÓN COMPLETADA: {eliminados} artículos eliminados")
            else:
                print(f"\n⚠️  No se eliminó ningún artículo")

        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE ARTÍCULOS DE PRUEBA EN PRODUCCIÓN")
    print("=" * 60)
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "--eliminar":
        verificar_inventario_produccion()
        eliminar_articulos_prueba_produccion()
    else:
        verificar_inventario_produccion()
        print("\nPara eliminar artículos de prueba use:")
        print("  python verificar_cloud_inventario.py --eliminar")
