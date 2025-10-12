#!/usr/bin/env python3
"""
Script para eliminar artículos sobrantes del inventario en producción
EJECUTAR DESDE GOOGLE CLOUD SHELL O APP ENGINE
"""

import os
import sys
from datetime import datetime


def limpiar_inventario_produccion():
    """Eliminar todos los artículos del inventario en producción"""

    # Configurar para producción si no están las variables
    if not os.environ.get("DB_TYPE"):
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

    from app import create_app
    from app.models import db
    from sqlalchemy import text

    app = create_app()

    with app.app_context():
        print("🗑️  LIMPIEZA COMPLETA DEL INVENTARIO EN PRODUCCIÓN")
        print("=" * 60)
        print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🌐 Base de datos: Google Cloud SQL PostgreSQL")
        print("🏢 Proyecto: mantenimiento-470311")
        print()

        try:
            # Verificar conexión y contar artículos
            result = db.session.execute(text("SELECT COUNT(*) FROM inventario"))
            total_articulos = result.scalar()

            print(f"📊 Total de artículos encontrados: {total_articulos}")

            if total_articulos == 0:
                print("✅ El inventario ya está vacío.")
                return

            # Mostrar todos los artículos antes de eliminar
            result = db.session.execute(
                text(
                    """
                SELECT id, codigo, nombre, stock_actual, fecha_creacion 
                FROM inventario 
                ORDER BY id
            """
                )
            )

            articulos = result.fetchall()

            print("\n📋 ARTÍCULOS A ELIMINAR:")
            print("-" * 80)
            print(
                f"{'ID':3s} | {'Código':15s} | {'Nombre':30s} | {'Stock':5s} | {'Fecha':10s}"
            )
            print("-" * 80)

            for row in articulos:
                id_art, codigo, nombre, stock, fecha = row
                codigo_str = (codigo or "N/A")[:15]
                nombre_str = (nombre or "N/A")[:30]
                fecha_str = fecha.strftime("%Y-%m-%d") if fecha else "N/A"
                print(
                    f"{id_art:3d} | {codigo_str:15s} | {nombre_str:30s} | {stock:5d} | {fecha_str:10s}"
                )

            print("-" * 80)
            print(f"Total a eliminar: {len(articulos)} artículos")

            # Doble confirmación de seguridad
            print(
                "\n⚠️  ADVERTENCIA: Esta acción eliminará TODOS los artículos del inventario en PRODUCCIÓN"
            )
            print("⚠️  Esta acción NO se puede deshacer")

            respuesta1 = input(
                "\n¿Está ABSOLUTAMENTE SEGURO? Escriba 'SI, ELIMINAR TODO': "
            )

            if respuesta1 != "SI, ELIMINAR TODO":
                print("❌ Operación cancelada por seguridad.")
                return

            respuesta2 = input(
                "\nÚltima confirmación. Escriba 'CONFIRMO ELIMINACION': "
            )

            if respuesta2 != "CONFIRMO ELIMINACION":
                print("❌ Operación cancelada por seguridad.")
                return

            # Proceder con la eliminación
            print("\n🗑️  INICIANDO ELIMINACIÓN MASIVA...")
            print("   ⏳ Por favor espere...")

            # Eliminar todos los artículos
            result = db.session.execute(text("DELETE FROM inventario"))
            articulos_eliminados = result.rowcount

            # Reiniciar secuencia de IDs
            db.session.execute(text("ALTER SEQUENCE inventario_id_seq RESTART WITH 1"))

            # Confirmar cambios
            db.session.commit()

            print(f"\n✅ ELIMINACIÓN COMPLETADA")
            print(f"   📊 Artículos eliminados: {articulos_eliminados}")
            print(f"   🔄 Secuencia de IDs reiniciada")
            print(f"   🕐 Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Verificar que está vacío
            result = db.session.execute(text("SELECT COUNT(*) FROM inventario"))
            verificacion = result.scalar()

            if verificacion == 0:
                print("   ✅ Verificación: Inventario completamente vacío")
            else:
                print(f"   ⚠️  Verificación: Quedan {verificacion} artículos")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            print("   La operación ha sido revertida.")
            import traceback

            traceback.print_exc()


def mostrar_inventario():
    """Solo mostrar el inventario actual"""

    # Configurar para producción si no están las variables
    if not os.environ.get("DB_TYPE"):
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

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from app import create_app
    from app.models import db
    from sqlalchemy import text

    app = create_app()

    with app.app_context():
        print("📦 INVENTARIO ACTUAL EN PRODUCCIÓN")
        print("=" * 50)

        try:
            result = db.session.execute(
                text(
                    """
                SELECT id, codigo, nombre, stock_actual, fecha_creacion 
                FROM inventario 
                ORDER BY id
            """
                )
            )

            articulos = result.fetchall()

            print(f"📊 Total de artículos: {len(articulos)}")

            if len(articulos) == 0:
                print("✅ El inventario está vacío.")
                return

            print("\n📋 LISTADO COMPLETO:")
            print("-" * 80)
            print(
                f"{'ID':3s} | {'Código':15s} | {'Nombre':30s} | {'Stock':5s} | {'Fecha':10s}"
            )
            print("-" * 80)

            for row in articulos:
                id_art, codigo, nombre, stock, fecha = row
                codigo_str = (codigo or "N/A")[:15]
                nombre_str = (nombre or "N/A")[:30]
                fecha_str = fecha.strftime("%Y-%m-%d") if fecha else "N/A"
                print(
                    f"{id_art:3d} | {codigo_str:15s} | {nombre_str:30s} | {stock:5d} | {fecha_str:10s}"
                )

            print("-" * 80)

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Limpiar inventario en producción")
    parser.add_argument("--ver", action="store_true", help="Solo ver el inventario")
    parser.add_argument(
        "--eliminar", action="store_true", help="Eliminar todos los artículos"
    )

    args = parser.parse_args()

    if args.eliminar:
        limpiar_inventario_produccion()
    elif args.ver:
        mostrar_inventario()
    else:
        print("Uso:")
        print("  python limpiar_inventario_produccion.py --ver        # Ver inventario")
        print(
            "  python limpiar_inventario_produccion.py --eliminar   # Eliminar todos los artículos"
        )
        print()
        print(
            "IMPORTANTE: Este script debe ejecutarse desde Google Cloud Shell o App Engine"
        )
