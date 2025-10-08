#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test completo para verificar el sistema de categorías dinámicas
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models.categoria import Categoria
from app.models.inventario import Inventario
from app.extensions import db
from sqlalchemy import text
import requests


def test_api_categorias():
    """Test de las APIs de categorías"""
    app = create_app()

    with app.app_context():
        # Limpiar la base de datos
        Inventario.query.delete()
        Categoria.query.delete()
        db.session.commit()

        print("=== Test del Sistema de Categorías Dinámicas ===\n")

        # 1. Crear categorías de ejemplo
        categorias_ejemplo = [
            {"nombre": "Herramientas", "descripcion": "Herramientas de trabajo"},
            {"nombre": "Mecánicos", "descripcion": "Repuestos mecánicos"},
            {"nombre": "Eléctricos", "descripcion": "Componentes eléctricos"},
            {"nombre": "Hidráulicos", "descripcion": "Sistemas hidráulicos"},
            {"nombre": "Lubricantes", "descripcion": "Aceites y lubricantes"},
        ]

        print("1. Creando categorías de ejemplo...")
        for cat_data in categorias_ejemplo:
            categoria = Categoria(
                nombre=cat_data["nombre"], descripcion=cat_data["descripcion"]
            )
            db.session.add(categoria)
            db.session.commit()
            print(f"   ✅ {categoria.nombre} - Prefijo: {categoria.prefijo}")

        print(f"\n2. Total de categorías creadas: {Categoria.query.count()}")

        # 2. Crear algunos artículos con categorías
        print("\n3. Creando artículos con categorías...")
        herramientas = Categoria.query.filter_by(nombre="Herramientas").first()
        mecanicos = Categoria.query.filter_by(nombre="Mecánicos").first()

        if herramientas:
            # Generar códigos automáticos
            codigo1 = herramientas.generar_proximo_codigo()
            articulo1 = Inventario(
                codigo=codigo1,
                descripcion="Martillo de bola 16oz",
                categoria_id=herramientas.id,
                stock_actual=5,
                stock_minimo=2,
                precio_unitario=25.50,
                ubicacion="A-1-01",
            )
            db.session.add(articulo1)
            print(f"   ✅ Artículo: {articulo1.codigo} - {articulo1.descripcion}")

            codigo2 = herramientas.generar_proximo_codigo()
            articulo2 = Inventario(
                codigo=codigo2,
                descripcion="Destornillador Phillips #2",
                categoria_id=herramientas.id,
                stock_actual=8,
                stock_minimo=3,
                precio_unitario=12.00,
                ubicacion="A-1-02",
            )
            db.session.add(articulo2)
            print(f"   ✅ Artículo: {articulo2.codigo} - {articulo2.descripcion}")

        if mecanicos:
            codigo3 = mecanicos.generar_proximo_codigo()
            articulo3 = Inventario(
                codigo=codigo3,
                descripcion="Rodamiento 6204-2RS",
                categoria_id=mecanicos.id,
                stock_actual=12,
                stock_minimo=5,
                precio_unitario=8.75,
                ubicacion="B-2-05",
            )
            db.session.add(articulo3)
            print(f"   ✅ Artículo: {articulo3.codigo} - {articulo3.descripcion}")

        db.session.commit()

        # Conteo de artículos con fallback seguro (ROLLBACK + AUTOCOMMIT)
        try:
            total_articulos = Inventario.query.count()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            try:
                db.session.remove()
            except Exception:
                pass
            backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
            table_name = "inventario"
            if backend in ("postgresql", "postgres"):
                table_name = "public.inventario"
            with db.engine.connect() as base_conn:
                try:
                    base_conn.exec_driver_sql("ROLLBACK")
                except Exception:
                    pass
                with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                    res = conn.execute(text(f"SELECT COUNT(*) AS total FROM {table_name}")).first()
                    total_articulos = int(res[0]) if res else 0
        print(f"\n4. Total de artículos creados: {total_articulos}")

        # 3. Verificar generación de códigos
        print("\n5. Verificando generación de códigos...")
        for categoria in Categoria.query.all():
            proximo_codigo = categoria.generar_proximo_codigo()
            print(f"   📝 {categoria.nombre}: próximo código sería {proximo_codigo}")

        # 4. Mostrar estadísticas
        print("\n6. Estadísticas del sistema:")
        for categoria in Categoria.query.all():
            try:
                count = Inventario.query.filter_by(categoria_id=categoria.id).count()
            except Exception:
                try:
                    db.session.rollback()
                except Exception:
                    pass
                try:
                    db.session.remove()
                except Exception:
                    pass
                backend = db.engine.url.get_backend_name() if getattr(db, "engine", None) else None
                table_name = "inventario"
                if backend in ("postgresql", "postgres"):
                    table_name = "public.inventario"
                with db.engine.connect() as base_conn:
                    try:
                        base_conn.exec_driver_sql("ROLLBACK")
                    except Exception:
                        pass
                    with base_conn.execution_options(isolation_level="AUTOCOMMIT") as conn:
                        res = conn.execute(
                            text(
                                f"SELECT COUNT(*) AS total FROM {table_name} WHERE categoria_id = :cid"
                            ),
                            {"cid": categoria.id},
                        ).first()
                        count = int(res[0]) if res else 0
            print(f"   📊 {categoria.nombre}: {count} artículos")

        print("\n=== Test completado exitosamente ===")
        return True


if __name__ == "__main__":
    test_api_categorias()
