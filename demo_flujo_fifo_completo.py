#!/usr/bin/env python
"""
Demostración completa del sistema FIFO integrado con entradas automáticas.
Este script muestra el flujo completo desde entrada de producto hasta consumo automático.
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
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.models.movimiento_inventario import MovimientoInventario
from app.controllers.inventario_controller_simple import registrar_movimiento_inventario
from datetime import datetime


def demo_flujo_completo_fifo():
    """Demostración completa del flujo FIFO automatizado"""
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 80)
        print("🎯 DEMOSTRACIÓN COMPLETA: SISTEMA FIFO AUTOMATIZADO")
        print("=" * 80)
        print(
            "📋 Flujo: Entrada de producto → Creación automática de lotes → Consumo FIFO"
        )
        print()

        # Buscar artículo FIFO de prueba
        articulo = Inventario.query.filter(Inventario.codigo.like("FIFO-%")).first()

        if not articulo:
            print("❌ No se encontró artículo FIFO. Ejecute test_ui_fifo.py primero")
            return

        print(f"📦 Artículo seleccionado: {articulo.codigo} - {articulo.descripcion}")

        # Estado inicial
        stock_inicial = articulo.stock_actual
        lotes_iniciales = LoteInventario.query.filter_by(
            inventario_id=articulo.id
        ).count()

        print(f"📊 Estado inicial:")
        print(f"   Stock: {stock_inicial}")
        print(f"   Lotes: {lotes_iniciales}")

        print("\n" + "=" * 80)
        print("🔄 PASO 1: SIMULANDO COMPRAS (ENTRADAS AUTOMÁTICAS)")
        print("=" * 80)

        # Simular 3 compras en diferentes fechas con diferentes precios
        compras = [
            {
                "cantidad": 100,
                "precio": 10.50,
                "proveedor": "Proveedor A",
                "factura": "FACT-A-001",
            },
            {
                "cantidad": 75,
                "precio": 11.20,
                "proveedor": "Proveedor B",
                "factura": "FACT-B-002",
            },
            {
                "cantidad": 50,
                "precio": 9.80,
                "proveedor": "Proveedor C",
                "factura": "FACT-C-003",
            },
        ]

        for i, compra in enumerate(compras, 1):
            print(
                f"\n🛒 Compra {i}: {compra['cantidad']} unidades a €{compra['precio']} c/u"
            )
            print(f"   📄 {compra['factura']} - {compra['proveedor']}")

            try:
                # Registrar entrada (automáticamente crea lote FIFO)
                data_entrada = {
                    "inventario_id": articulo.id,
                    "tipo": "entrada",
                    "cantidad": compra["cantidad"],
                    "precio_unitario": compra["precio"],
                    "documento_referencia": compra["factura"],
                    "observaciones": f"Compra a {compra['proveedor']}",
                    "usuario_id": "sistema_compras",
                }

                movimiento = registrar_movimiento_inventario(data_entrada)
                print(f"   ✅ Entrada registrada (ID: {movimiento.id})")
                print(f"   🏷️  Lote FIFO creado automáticamente")

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

        # Verificar estado después de entradas
        db.session.refresh(articulo)
        lotes_después_entradas = (
            LoteInventario.query.filter_by(inventario_id=articulo.id)
            .order_by(LoteInventario.fecha_entrada)
            .all()
        )

        print(f"\n📊 Estado después de entradas:")
        print(f"   Stock total: {articulo.stock_actual}")
        print(f"   Lotes creados: {len(lotes_después_entradas) - lotes_iniciales}")
        print(f"   Precio promedio: €{articulo.precio_promedio or 0}")

        print(f"\n📋 Lotes ordenados por FIFO (más antiguos primero):")
        for lote in lotes_después_entradas[-3:]:  # Mostrar últimos 3 lotes
            print(f"   🏷️  {lote.codigo_lote or f'Lote-{lote.id}'}")
            print(f"      📅 Entrada: {lote.fecha_entrada.strftime('%d/%m/%Y %H:%M')}")
            print(f"      📦 Cantidad: {lote.cantidad_actual}")
            print(f"      💰 Precio: €{lote.precio_unitario}")
            if lote.documento_origen:
                print(f"      📄 Documento: {lote.documento_origen}")
            print()

        print("\n" + "=" * 80)
        print("🔄 PASO 2: SIMULANDO CONSUMOS (SALIDAS AUTOMÁTICAS FIFO)")
        print("=" * 80)

        # Simular varios consumos
        consumos = [
            {"cantidad": 80, "motivo": "Orden de trabajo OT-001", "orden": "OT-001"},
            {"cantidad": 60, "motivo": "Orden de trabajo OT-002", "orden": "OT-002"},
            {"cantidad": 45, "motivo": "Mantenimiento preventivo", "orden": "OT-003"},
        ]

        for i, consumo in enumerate(consumos, 1):
            print(f"\n📤 Consumo {i}: {consumo['cantidad']} unidades")
            print(f"   🔧 {consumo['motivo']}")

            # Mostrar lotes antes del consumo
            lotes_antes = (
                LoteInventario.query.filter_by(inventario_id=articulo.id)
                .filter(LoteInventario.cantidad_actual > 0)
                .order_by(LoteInventario.fecha_entrada)
                .limit(3)
                .all()
            )

            print(f"   📋 Lotes disponibles (FIFO):")
            for lote in lotes_antes:
                print(
                    f"      🏷️  {lote.codigo_lote or f'Lote-{lote.id}'}: {lote.cantidad_actual} unidades"
                )

            try:
                # Registrar salida (automáticamente consume FIFO)
                data_salida = {
                    "inventario_id": articulo.id,
                    "tipo": "salida",
                    "cantidad": consumo["cantidad"],
                    "documento_referencia": consumo["orden"],
                    "observaciones": consumo["motivo"],
                    "usuario_id": "sistema_ordenes",
                }

                movimiento = registrar_movimiento_inventario(data_salida)
                print(f"   ✅ Salida registrada (ID: {movimiento.id})")
                print(f"   🎯 Consumo FIFO automático ejecutado")

                # Mostrar movimientos de lotes generados
                movimientos_lote = MovimientoLote.query.filter_by(
                    documento_referencia=consumo["orden"]
                ).all()

                if movimientos_lote:
                    print(f"   📋 Lotes consumidos:")
                    for mov_lote in movimientos_lote:
                        lote = mov_lote.lote
                        print(
                            f"      🏷️  {lote.codigo_lote or f'Lote-{lote.id}'}: {mov_lote.cantidad} unidades"
                        )
                        print(
                            f"         💰 Precio: €{lote.precio_unitario} - Restante: {lote.cantidad_actual}"
                        )

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

        # Estado final
        db.session.refresh(articulo)
        lotes_finales = (
            LoteInventario.query.filter_by(inventario_id=articulo.id)
            .filter(LoteInventario.cantidad_actual > 0)
            .order_by(LoteInventario.fecha_entrada)
            .all()
        )

        print("\n" + "=" * 80)
        print("📊 ESTADO FINAL DEL SISTEMA")
        print("=" * 80)
        print(f"📦 Stock final: {articulo.stock_actual} unidades")
        print(f"🏷️  Lotes activos: {len(lotes_finales)}")
        print(f"💰 Precio promedio: €{articulo.precio_promedio or 0}")

        print(f"\n📋 Lotes restantes (ordenados por FIFO):")
        for lote in lotes_finales:
            estado_vencimiento = ""
            if lote.fecha_vencimiento:
                dias_para_vencer = (
                    lote.fecha_vencimiento.date() - datetime.now().date()
                ).days
                if dias_para_vencer < 0:
                    estado_vencimiento = " ⚠️ VENCIDO"
                elif dias_para_vencer <= 30:
                    estado_vencimiento = f" ⏰ Vence en {dias_para_vencer} días"

            print(f"   🏷️  {lote.codigo_lote or f'Lote-{lote.id}'}")
            print(f"      📦 Cantidad: {lote.cantidad_actual} unidades")
            print(f"      💰 Precio: €{lote.precio_unitario}")
            print(
                f"      📅 Entrada: {lote.fecha_entrada.strftime('%d/%m/%Y')}{estado_vencimiento}"
            )
            print()

        # Resumen de movimientos
        total_movimientos = MovimientoInventario.query.filter_by(
            inventario_id=articulo.id
        ).count()
        total_movimientos_lote = (
            MovimientoLote.query.join(LoteInventario)
            .filter(LoteInventario.inventario_id == articulo.id)
            .count()
        )

        print(f"📈 Resumen de movimientos:")
        print(f"   📦 Movimientos de inventario: {total_movimientos}")
        print(f"   🏷️  Movimientos de lotes: {total_movimientos_lote}")

        print("\n" + "=" * 80)
        print("🎉 DEMOSTRACIÓN COMPLETADA")
        print("=" * 80)
        print("✅ Sistema FIFO completamente automatizado:")
        print("   🔄 Entradas → Lotes creados automáticamente")
        print("   🔄 Salidas → Consumo FIFO automático")
        print("   🔄 Trazabilidad completa mantenida")
        print("   🔄 Sin intervención manual necesaria")
        print("\n💡 Visite /lotes/demo para ver la interfaz visual")


if __name__ == "__main__":
    demo_flujo_completo_fifo()
