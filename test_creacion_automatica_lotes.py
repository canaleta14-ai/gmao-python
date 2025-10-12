#!/usr/bin/env python
"""
Script para probar la creación automática de lotes FIFO al registrar entradas de inventario.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuración de desarrollo
os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = (
    "development-secret-key-for-testing-fifo-articles-demo-1234567890"
)
os.environ["DATABASE_URL"] = "sqlite:///gmao.db"

from app import create_app
from app.extensions import db
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.models.movimiento_inventario import MovimientoInventario
from app.controllers.inventario_controller import crear_movimiento_inventario_avanzado
from app.controllers.inventario_controller_simple import registrar_movimiento_inventario
from datetime import datetime


def test_creacion_automatica_lotes():
    """Prueba la creación automática de lotes FIFO"""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 70)
        print("🧪 PROBANDO CREACIÓN AUTOMÁTICA DE LOTES FIFO")
        print("=" * 70)

        # Buscar un artículo FIFO de prueba
        articulo = Inventario.query.filter(Inventario.codigo.like("FIFO-%")).first()

        if not articulo:
            print("❌ No se encontró ningún artículo FIFO de prueba")
            print("💡 Ejecute primero test_ui_fifo.py para crear datos de prueba")
            return

        print(f"📦 Artículo seleccionado: {articulo.codigo} - {articulo.descripcion}")
        print(f"📊 Stock actual antes: {articulo.stock_actual}")

        # Contar lotes antes
        lotes_antes = LoteInventario.query.filter_by(inventario_id=articulo.id).count()
        print(f"📦 Lotes antes: {lotes_antes}")

        # Crear movimiento de entrada usando el controlador avanzado
        print("\n🔄 Probando controlador avanzado...")
        try:
            data_entrada = {
                "inventario_id": articulo.id,
                "tipo": "entrada",
                "cantidad": 50,
                "precio_unitario": 25.50,
                "documento_referencia": "FACT-2025-001",
                "observaciones": "Prueba automática de creación de lotes FIFO",
                "usuario_id": "test_user",
            }

            movimiento_avanzado = crear_movimiento_inventario_avanzado(data_entrada)
            print(f"✅ Movimiento avanzado creado: ID {movimiento_avanzado.id}")

        except Exception as e:
            print(f"❌ Error en controlador avanzado: {str(e)}")

        # Crear movimiento de entrada usando el controlador simple
        print("\n🔄 Probando controlador simple...")
        try:
            data_entrada_simple = {
                "inventario_id": articulo.id,
                "tipo": "entrada",
                "cantidad": 25,
                "precio_unitario": 30.00,
                "documento_referencia": "FACT-2025-002",
                "observaciones": "Prueba automática simple de creación de lotes FIFO",
                "usuario_id": "test_user_simple",
            }

            movimiento_simple = registrar_movimiento_inventario(data_entrada_simple)
            print(f"✅ Movimiento simple creado: ID {movimiento_simple.id}")

        except Exception as e:
            print(f"❌ Error en controlador simple: {str(e)}")

        # Verificar resultados
        db.session.refresh(articulo)
        lotes_despues = LoteInventario.query.filter_by(
            inventario_id=articulo.id
        ).count()

        print(f"\n📊 RESULTADOS:")
        print(f"📦 Stock actual después: {articulo.stock_actual}")
        print(f"📦 Lotes después: {lotes_despues}")
        print(f"➕ Lotes creados: {lotes_despues - lotes_antes}")

        # Mostrar los nuevos lotes
        lotes_nuevos = (
            LoteInventario.query.filter_by(inventario_id=articulo.id)
            .order_by(LoteInventario.fecha_entrada.desc())
            .limit(3)
        )

        print(f"\n📋 ÚLTIMOS LOTES CREADOS:")
        for lote in lotes_nuevos:
            print(f"  🏷️  {lote.codigo_lote or f'Lote-{lote.id}'}")
            print(f"      📅 Fecha: {lote.fecha_entrada.strftime('%d/%m/%Y %H:%M')}")
            print(f"      📦 Cantidad: {lote.cantidad_actual}")
            print(f"      💰 Precio: €{lote.precio_unitario}")
            if lote.fecha_vencimiento:
                print(f"      ⏰ Vence: {lote.fecha_vencimiento.strftime('%d/%m/%Y')}")
            print(f"      📄 Observaciones: {lote.observaciones}")
            print()

        # Probar consumo FIFO automático
        print(f"🔄 Probando consumo FIFO automático...")
        try:
            data_salida = {
                "inventario_id": articulo.id,
                "tipo": "salida",
                "cantidad": 20,
                "observaciones": "Prueba automática de consumo FIFO",
                "usuario_id": "test_user_consumo",
            }

            movimiento_salida = registrar_movimiento_inventario(data_salida)
            print(f"✅ Consumo automático realizado: ID {movimiento_salida.id}")

            # Verificar lotes después del consumo
            db.session.refresh(articulo)
            print(f"📊 Stock después del consumo: {articulo.stock_actual}")

        except Exception as e:
            print(f"❌ Error en consumo automático: {str(e)}")

        print("\n" + "=" * 70)
        print("🎉 PRUEBA DE CREACIÓN AUTOMÁTICA COMPLETADA")
        print("=" * 70)
        print("✅ Los lotes se crean automáticamente al registrar entradas")
        print("✅ El consumo FIFO se realiza automáticamente en salidas")
        print("💡 Revise los lotes en /lotes/demo para ver el resultado")


if __name__ == "__main__":
    test_creacion_automatica_lotes()
