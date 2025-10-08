#!/usr/bin/env python3
"""
Script para insertar datos de prueba en el inventario
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.extensions import db
from sqlalchemy import text


def insertar_datos_prueba():
    app = create_app()

    with app.app_context():
        try:
            print("🔄 Insertando datos de prueba en inventario...")

            # Limpiar tabla si tiene datos
            db.session.execute(text("DELETE FROM inventario;"))

            # Datos de ejemplo
            articulos_prueba = [
                {
                    "codigo": "REP001",
                    "descripcion": "Motor eléctrico 5HP trifásico",
                    "categoria": "Eléctricos",
                    "ubicacion": "Almacén A-1",
                    "stock_actual": 5,
                    "stock_minimo": 2,
                    "precio_unitario": 850.00,
                    "precio_promedio": 820.00,
                    "critico": True,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Motores España SA",
                },
                {
                    "codigo": "REP002",
                    "descripcion": "Bomba hidráulica centrífuga",
                    "categoria": "Hidráulicos",
                    "ubicacion": "Almacén B-2",
                    "stock_actual": 3,
                    "stock_minimo": 1,
                    "precio_unitario": 1200.00,
                    "precio_promedio": 1150.00,
                    "critico": True,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Hidráulica Industrial",
                },
                {
                    "codigo": "REP003",
                    "descripcion": "Filtro de aceite hidráulico",
                    "categoria": "Hidráulicos",
                    "ubicacion": "Almacén C-1",
                    "stock_actual": 15,
                    "stock_minimo": 10,
                    "precio_unitario": 25.50,
                    "precio_promedio": 24.80,
                    "critico": False,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Filtros Técnicos",
                },
                {
                    "codigo": "REP004",
                    "descripcion": "Correa de transmisión tipo A",
                    "categoria": "Mecánicos",
                    "ubicacion": "Almacén A-3",
                    "stock_actual": 8,
                    "stock_minimo": 5,
                    "precio_unitario": 15.75,
                    "precio_promedio": 16.20,
                    "critico": False,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Transmisiones SA",
                },
                {
                    "codigo": "REP005",
                    "descripcion": "Rodamiento 6208-2RS",
                    "categoria": "Mecánicos",
                    "ubicacion": "Almacén A-2",
                    "stock_actual": 1,
                    "stock_minimo": 5,
                    "precio_unitario": 18.90,
                    "precio_promedio": 19.50,
                    "critico": False,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Rodamientos Industriales",
                },
                {
                    "codigo": "LUB001",
                    "descripcion": "Aceite hidráulico ISO VG 46",
                    "categoria": "Lubricantes",
                    "ubicacion": "Almacén D-1",
                    "stock_actual": 50,
                    "stock_minimo": 20,
                    "precio_unitario": 4.25,
                    "precio_promedio": 4.15,
                    "critico": False,
                    "cuenta_contable_compra": "600000000",
                    "grupo_contable": "60",
                    "proveedor_principal": "Lubricantes Profesionales",
                },
                {
                    "codigo": "ELE001",
                    "descripcion": "Contactor 3RT1025-1BB40",
                    "categoria": "Eléctricos",
                    "ubicacion": "Almacén E-1",
                    "stock_actual": 4,
                    "stock_minimo": 3,
                    "precio_unitario": 65.00,
                    "precio_promedio": 62.50,
                    "critico": False,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Eléctrica Industrial",
                },
                {
                    "codigo": "NEU001",
                    "descripcion": "Válvula neumática 5/2 vías",
                    "categoria": "Neumáticos",
                    "ubicacion": "Almacén F-1",
                    "stock_actual": 0,
                    "stock_minimo": 2,
                    "precio_unitario": 125.00,
                    "precio_promedio": 120.00,
                    "critico": True,
                    "cuenta_contable_compra": "622000000",
                    "proveedor_principal": "Neumática Avanzada",
                },
            ]

            # Insertar artículos
            for articulo in articulos_prueba:
                insert_sql = """
                INSERT INTO inventario (
                    codigo, descripcion, categoria, ubicacion, 
                    stock_actual, stock_minimo, precio_unitario, precio_promedio,
                    critico, activo, cuenta_contable_compra, grupo_contable, proveedor_principal,
                    fecha_creacion, fecha_actualizacion
                ) VALUES (
                    :codigo, :descripcion, :categoria, :ubicacion,
                    :stock_actual, :stock_minimo, :precio_unitario, :precio_promedio,
                    :critico, 1, :cuenta_contable_compra, :grupo_contable, :proveedor_principal,
                    datetime('now'), datetime('now')
                );
                """

                db.session.execute(
                    text(insert_sql),
                    {
                        "codigo": articulo["codigo"],
                        "descripcion": articulo["descripcion"],
                        "categoria": articulo["categoria"],
                        "ubicacion": articulo["ubicacion"],
                        "stock_actual": articulo["stock_actual"],
                        "stock_minimo": articulo["stock_minimo"],
                        "precio_unitario": articulo["precio_unitario"],
                        "precio_promedio": articulo["precio_promedio"],
                        "critico": articulo["critico"],
                        "cuenta_contable_compra": articulo["cuenta_contable_compra"],
                        "grupo_contable": articulo.get("grupo_contable", None),
                        "proveedor_principal": articulo["proveedor_principal"],
                    },
                )

            db.session.commit()
            print(f"✅ Insertados {len(articulos_prueba)} artículos de prueba")

            # Mostrar resumen en conexión independiente con AUTOCOMMIT tras ROLLBACK
            backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
            table_name = "inventario"
            if backend == "postgresql":
                table_name = "public.inventario"

            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    res = conn.execute(text(f"SELECT COUNT(*) AS total FROM {table_name}"))
                    total = int(res.fetchone()[0]) if res else 0
            print(f"üìä Total de artículos en inventario: {total}")

            print("\nüéØ Categorías insertadas:")
            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    result = conn.execute(
                        text(
                            f"SELECT categoria, COUNT(*) AS total FROM {table_name} GROUP BY categoria"
                        )
                    )
                    for row in result.fetchall():
                        print(f"   - {row[0]}: {row[1]} artículos")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la inserción: {e}")
            raise e


if __name__ == "__main__":
    insertar_datos_prueba()
