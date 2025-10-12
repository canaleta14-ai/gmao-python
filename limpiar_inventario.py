#!/usr/bin/env python3
"""
Script simplificado para limpiar artículos de prueba del inventario
"""

import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Inventario
from sqlalchemy import text


def listar_inventario_simple():
    """Lista artículos del inventario de forma simple"""

    app = create_app()

    with app.app_context():
        print("📦 VERIFICACIÓN DEL INVENTARIO")
        print("=" * 50)

        try:
            # Consulta SQL directa para ser más robusta
            result = db.session.execute(
                text(
                    """
                SELECT id, codigo, nombre, stock_actual, activo 
                FROM inventario 
                ORDER BY codigo
            """
                )
            )

            articulos = result.fetchall()

            print(f"Total de artículos encontrados: {len(articulos)}")

            if len(articulos) == 0:
                print("✅ El inventario está vacío.")
                return

            print("\n📋 LISTA DE ARTÍCULOS:")
            print("-" * 80)
            print(
                f"{'ID':3s} | {'Código':15s} | {'Nombre':30s} | {'Stock':5s} | {'Activo':6s}"
            )
            print("-" * 80)

            articulos_prueba = []

            for row in articulos:
                id_art, codigo, nombre, stock, activo = row

                # Identificar artículos de prueba
                es_prueba = False
                if codigo and nombre:
                    codigo_lower = codigo.lower()
                    nombre_lower = nombre.lower()

                    if (
                        (
                            "prueba" in codigo_lower
                            or "test" in codigo_lower
                            or "demo" in codigo_lower
                        )
                        or (
                            "prueba" in nombre_lower
                            or "test" in nombre_lower
                            or "demo" in nombre_lower
                        )
                        or codigo.startswith("P-")
                        or codigo.startswith("T-")
                        or codigo.startswith("TEST-")
                        or codigo.startswith("DEMO-")
                    ):
                        es_prueba = True
                        articulos_prueba.append((id_art, codigo, nombre))

                estado = "Sí" if activo else "No"
                marca = "🧪" if es_prueba else "  "

                print(
                    f"{marca}{id_art:3d} | {codigo:15s} | {nombre[:30]:30s} | {stock:5d} | {estado:6s}"
                )

            print("-" * 80)

            if articulos_prueba:
                print(f"\n🧪 ARTÍCULOS DE PRUEBA DETECTADOS: {len(articulos_prueba)}")
                print("   (Marcados con 🧪)")

                for id_art, codigo, nombre in articulos_prueba:
                    print(f"   - ID {id_art}: {codigo} - {nombre}")
            else:
                print("\n✅ No se detectaron artículos de prueba.")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback

            traceback.print_exc()


def eliminar_articulos_prueba_simple():
    """Elimina artículos de prueba identificados"""

    app = create_app()

    with app.app_context():
        print("🧹 ELIMINACIÓN DE ARTÍCULOS DE PRUEBA")
        print("=" * 50)

        try:
            # Buscar artículos de prueba
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

            print(f"🔍 Artículos de prueba encontrados: {len(articulos_prueba)}")

            if len(articulos_prueba) == 0:
                print("✅ No se encontraron artículos de prueba para eliminar.")
                return

            print("\n📋 ARTÍCULOS A ELIMINAR:")
            print("-" * 60)

            for row in articulos_prueba:
                id_art, codigo, nombre, stock = row
                print(
                    f"ID: {id_art:3d} | {codigo:15s} | {nombre[:30]:30s} | Stock: {stock}"
                )

            print("-" * 60)
            print(f"Total a eliminar: {len(articulos_prueba)} artículos")

            # Confirmación
            respuesta = input(
                "\n⚠️  ¿Confirma la eliminación de estos artículos? (s/N): "
            )

            if respuesta.lower() not in ["s", "si", "sí", "yes", "y"]:
                print("❌ Operación cancelada.")
                return

            # Eliminar artículos
            print("\n🗑️  Eliminando artículos...")
            eliminados = 0

            for row in articulos_prueba:
                id_art, codigo, nombre, stock = row
                try:
                    db.session.execute(
                        text("DELETE FROM inventario WHERE id = :id"), {"id": id_art}
                    )
                    print(f"   ✅ Eliminado: {codigo} - {nombre}")
                    eliminados += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando {codigo}: {str(e)}")

            # Confirmar cambios
            if eliminados > 0:
                try:
                    db.session.commit()
                    print(f"\n✅ ELIMINACIÓN COMPLETADA")
                    print(f"   Artículos eliminados: {eliminados}")
                    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                except Exception as e:
                    db.session.rollback()
                    print(f"\n❌ ERROR AL CONFIRMAR: {str(e)}")

        except Exception as e:
            print(f"❌ ERROR GENERAL: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Limpiar artículos de prueba del inventario"
    )
    parser.add_argument("--listar", action="store_true", help="Listar inventario")
    parser.add_argument(
        "--eliminar", action="store_true", help="Eliminar artículos de prueba"
    )

    args = parser.parse_args()

    if args.listar:
        listar_inventario_simple()
    elif args.eliminar:
        eliminar_articulos_prueba_simple()
    else:
        print("Uso:")
        print("  python limpiar_inventario.py --listar     # Ver inventario")
        print(
            "  python limpiar_inventario.py --eliminar   # Eliminar artículos de prueba"
        )
