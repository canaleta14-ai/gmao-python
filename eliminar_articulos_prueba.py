#!/usr/bin/env python3
"""
Script para eliminar artículos de prueba del almacén/inventario
"""

import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Inventario
from sqlalchemy import or_


def eliminar_articulos_prueba():
    """Elimina artículos de prueba del inventario"""

    app = create_app()

    with app.app_context():
        print("🧹 ELIMINACIÓN DE ARTÍCULOS DE PRUEBA DEL ALMACÉN")
        print("=" * 55)
        print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            # Buscar artículos que parezcan de prueba
            criterios_prueba = [
                Inventario.nombre.ilike("%prueba%"),
                Inventario.nombre.ilike("%test%"),
                Inventario.nombre.ilike("%demo%"),
                Inventario.nombre.ilike("%ejemplo%"),
                Inventario.codigo.ilike("%TEST%"),
                Inventario.codigo.ilike("%PRUEBA%"),
                Inventario.codigo.ilike("%DEMO%"),
                Inventario.descripcion.ilike("%prueba%"),
                Inventario.descripcion.ilike("%test%"),
                Inventario.descripcion.ilike("%demo%"),
                # Códigos específicos de prueba
                Inventario.codigo.ilike("P-%"),
                Inventario.codigo.ilike("T-%"),
                Inventario.codigo.ilike("TEST-%"),
                Inventario.codigo.ilike("DEMO-%"),
            ]

            articulos_prueba = Inventario.query.filter(or_(*criterios_prueba)).all()

            print(f"🔍 Artículos de prueba encontrados: {len(articulos_prueba)}")

            if not articulos_prueba:
                print("✅ No se encontraron artículos de prueba para eliminar.")
                return

            print("\n📋 LISTA DE ARTÍCULOS A ELIMINAR:")
            print("-" * 80)

            for i, articulo in enumerate(articulos_prueba, 1):
                print(
                    f"{i:2d}. ID: {articulo.id:3d} | Código: {articulo.codigo:15s} | "
                    f"Nombre: {articulo.nombre[:30]:30s} | Stock: {articulo.stock_actual:3d}"
                )

            print("-" * 80)
            print(f"Total a eliminar: {len(articulos_prueba)} artículos")

            # Confirmación
            respuesta = input(
                "\n⚠️  ¿Está seguro de que desea eliminar estos artículos? (s/N): "
            )

            if respuesta.lower() not in ["s", "si", "sí", "yes", "y"]:
                print("❌ Operación cancelada por el usuario.")
                return

            # Proceso de eliminación
            print("\n🗑️  INICIANDO ELIMINACIÓN...")
            eliminados = 0
            errores = 0

            for articulo in articulos_prueba:
                try:
                    print(f"   Eliminando: {articulo.codigo} - {articulo.nombre}")
                    db.session.delete(articulo)
                    eliminados += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando {articulo.codigo}: {str(e)}")
                    errores += 1

            # Confirmar cambios
            if eliminados > 0:
                try:
                    db.session.commit()
                    print(f"\n✅ ELIMINACIÓN COMPLETADA")
                    print(f"   Artículos eliminados: {eliminados}")
                    print(f"   Errores: {errores}")
                    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                except Exception as e:
                    db.session.rollback()
                    print(f"\n❌ ERROR AL CONFIRMAR CAMBIOS: {str(e)}")
                    print("   Se ha revertido la operación.")

            else:
                print("\n⚠️  No se eliminó ningún artículo.")

        except Exception as e:
            print(f"\n❌ ERROR GENERAL: {str(e)}")
            db.session.rollback()


def listar_inventario():
    """Lista todos los artículos del inventario para verificación"""

    app = create_app()

    with app.app_context():
        print("📦 INVENTARIO ACTUAL")
        print("=" * 50)

        try:
            articulos = Inventario.query.order_by(Inventario.codigo).all()

            print(f"Total de artículos: {len(articulos)}")
            print("-" * 80)
            print(
                f"{'ID':3s} | {'Código':15s} | {'Nombre':30s} | {'Stock':5s} | {'Estado':8s}"
            )
            print("-" * 80)

            for articulo in articulos:
                estado = "Activo" if getattr(articulo, "activo", True) else "Inactivo"
                print(
                    f"{articulo.id:3d} | {articulo.codigo:15s} | "
                    f"{articulo.nombre[:30]:30s} | {articulo.stock_actual:5d} | {estado:8s}"
                )

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Gestión de artículos de prueba en el almacén"
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Listar todos los artículos del inventario",
    )
    parser.add_argument(
        "--eliminar", action="store_true", help="Eliminar artículos de prueba"
    )

    args = parser.parse_args()

    if args.listar:
        listar_inventario()
    elif args.eliminar:
        eliminar_articulos_prueba()
    else:
        print("Uso:")
        print("  python eliminar_articulos_prueba.py --listar     # Listar inventario")
        print(
            "  python eliminar_articulos_prueba.py --eliminar   # Eliminar artículos de prueba"
        )
