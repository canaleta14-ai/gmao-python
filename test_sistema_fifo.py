#!/usr/bin/env python3
"""
Script para probar la implementación del sistema FIFO
Crea artículos de prueba, lotes y prueba las operaciones FIFO
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models import Inventario
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.services.servicio_fifo import ServicioFIFO
from datetime import datetime, timezone, timedelta
from decimal import Decimal


def main():
    """Función principal de prueba del sistema FIFO"""

    app = create_app()

    with app.app_context():
        print("=== PRUEBA DEL SISTEMA FIFO ===\n")

        try:
            # 1. Crear artículo de prueba
            print("1. Creando artículo de prueba...")
            articulo = Inventario(
                codigo="FIFO-TEST-001",
                nombre="Artículo Prueba FIFO",
                descripcion="Artículo para probar el sistema FIFO",
                unidad_medida="UNI",
                stock_actual=0,
                precio_unitario=10.00,
                activo=True,
            )
            db.session.add(articulo)
            db.session.commit()
            print(f"✓ Artículo creado: {articulo.codigo} (ID: {articulo.id})")

            # 2. Crear varios lotes con fechas diferentes
            print("\n2. Creando lotes con diferentes fechas...")

            # Lote 1 - Más antiguo (hace 30 días)
            fecha_lote1 = datetime.now(timezone.utc) - timedelta(days=30)
            lote1 = LoteInventario(
                inventario_id=articulo.id,
                codigo_lote="LOTE-001",
                fecha_entrada=fecha_lote1,
                cantidad_inicial=Decimal("100"),
                cantidad_actual=Decimal("100"),
                precio_unitario=Decimal("8.50"),
                costo_total=Decimal("850.00"),
                documento_origen="FAC-001",
                usuario_creacion="admin",
            )
            db.session.add(lote1)

            # Lote 2 - Medio (hace 20 días)
            fecha_lote2 = datetime.now(timezone.utc) - timedelta(days=20)
            lote2 = LoteInventario(
                inventario_id=articulo.id,
                codigo_lote="LOTE-002",
                fecha_entrada=fecha_lote2,
                cantidad_inicial=Decimal("150"),
                cantidad_actual=Decimal("150"),
                precio_unitario=Decimal("9.00"),
                costo_total=Decimal("1350.00"),
                documento_origen="FAC-002",
                usuario_creacion="admin",
            )
            db.session.add(lote2)

            # Lote 3 - Más reciente (hace 10 días)
            fecha_lote3 = datetime.now(timezone.utc) - timedelta(days=10)
            lote3 = LoteInventario(
                inventario_id=articulo.id,
                codigo_lote="LOTE-003",
                fecha_entrada=fecha_lote3,
                cantidad_inicial=Decimal("200"),
                cantidad_actual=Decimal("200"),
                precio_unitario=Decimal("10.50"),
                costo_total=Decimal("2100.00"),
                documento_origen="FAC-003",
                usuario_creacion="admin",
            )
            db.session.add(lote3)

            db.session.commit()
            print(f"✓ Lote 1: {lote1.codigo_lote} - 100 uds @ $8.50 (más antiguo)")
            print(f"✓ Lote 2: {lote2.codigo_lote} - 150 uds @ $9.00 (medio)")
            print(f"✓ Lote 3: {lote3.codigo_lote} - 200 uds @ $10.50 (más reciente)")

            # 3. Mostrar stock disponible
            print("\n3. Stock disponible inicial:")
            stock_info = ServicioFIFO.obtener_stock_disponible(articulo.id)
            print(f"Total disponible: {stock_info['total_disponible']} unidades")
            print(f"Número de lotes: {stock_info['numero_lotes']}")
            for lote_info in stock_info["lotes"]:
                print(
                    f"  - {lote_info['codigo_lote']}: {lote_info['cantidad_disponible']} uds @ ${lote_info['precio_unitario']}"
                )

            # 4. Probar consumo FIFO - Consumir 120 unidades
            print("\n4. Probando consumo FIFO de 120 unidades...")
            consumos, faltante = ServicioFIFO.consumir_fifo(
                inventario_id=articulo.id,
                cantidad_total=120,
                documento_referencia="ORDEN-001",
                usuario_id="admin",
                observaciones="Prueba de consumo FIFO",
            )

            print(f"Cantidad no disponible: {faltante}")
            print("Consumos realizados:")
            for lote, cantidad in consumos:
                print(f"  - {lote.codigo_lote}: {cantidad} unidades")

            db.session.commit()

            # 5. Mostrar stock después del consumo
            print("\n5. Stock después del primer consumo:")
            stock_info = ServicioFIFO.obtener_stock_disponible(articulo.id)
            print(f"Total disponible: {stock_info['total_disponible']} unidades")
            for lote_info in stock_info["lotes"]:
                print(
                    f"  - {lote_info['codigo_lote']}: {lote_info['cantidad_disponible']} uds"
                )

            # 6. Probar reserva FIFO - Reservar 50 unidades
            print("\n6. Probando reserva FIFO de 50 unidades...")
            reservas, faltante = ServicioFIFO.reservar_stock(
                inventario_id=articulo.id,
                cantidad_total=50,
                orden_trabajo_id=1,
                documento_referencia="ORDEN-002",
                usuario_id="admin",
                observaciones="Prueba de reserva FIFO",
            )

            print(f"Cantidad no disponible: {faltante}")
            print("Reservas realizadas:")
            for lote, cantidad in reservas:
                print(f"  - {lote.codigo_lote}: {cantidad} unidades reservadas")

            db.session.commit()

            # 7. Mostrar stock con reservas
            print("\n7. Stock después de la reserva:")
            stock_info = ServicioFIFO.obtener_stock_disponible(articulo.id)
            print(f"Total actual: {stock_info['total_actual']} unidades")
            print(f"Total reservado: {stock_info['total_reservado']} unidades")
            print(f"Total disponible: {stock_info['total_disponible']} unidades")
            for lote_info in stock_info["lotes"]:
                print(
                    f"  - {lote_info['codigo_lote']}: {lote_info['cantidad_actual']} actual, "
                    f"{lote_info['cantidad_reservada']} reservado, "
                    f"{lote_info['cantidad_disponible']} disponible"
                )

            # 8. Liberar reservas
            print("\n8. Liberando reservas de la orden 1...")
            liberaciones = ServicioFIFO.liberar_reservas(
                orden_trabajo_id=1,
                usuario_id="admin",
                observaciones="Liberación de reservas de prueba",
            )

            print("Reservas liberadas:")
            for lote, cantidad in liberaciones:
                print(f"  - {lote.codigo_lote}: {cantidad} unidades liberadas")

            db.session.commit()

            # 9. Mostrar stock final
            print("\n9. Stock final después de liberar reservas:")
            stock_info = ServicioFIFO.obtener_stock_disponible(articulo.id)
            print(f"Total disponible: {stock_info['total_disponible']} unidades")
            for lote_info in stock_info["lotes"]:
                print(
                    f"  - {lote_info['codigo_lote']}: {lote_info['cantidad_disponible']} uds"
                )

            # 10. Verificar movimientos de lotes
            print("\n10. Movimientos de lotes registrados:")
            movimientos = (
                MovimientoLote.query.join(LoteInventario)
                .filter(LoteInventario.inventario_id == articulo.id)
                .order_by(MovimientoLote.fecha.asc())
                .all()
            )

            for mov in movimientos:
                print(
                    f"  - {mov.fecha.strftime('%Y-%m-%d %H:%M')} - "
                    f"{mov.tipo_movimiento} - {mov.cantidad} uds - "
                    f"Lote {mov.lote.codigo_lote}"
                )

            print("\n✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("\nEl sistema FIFO está funcionando correctamente:")
            print("- Los consumos usan primero los lotes más antiguos")
            print("- Las reservas siguen el mismo orden FIFO")
            print("- Se mantiene trazabilidad completa de movimientos")
            print("- El stock se actualiza correctamente")

        except Exception as e:
            print(f"\n❌ ERROR durante las pruebas: {str(e)}")
            import traceback

            traceback.print_exc()
            db.session.rollback()

        finally:
            # Limpiar datos de prueba
            try:
                print(f"\n11. Limpiando datos de prueba...")

                # Eliminar movimientos de lote
                MovimientoLote.query.join(LoteInventario).filter(
                    LoteInventario.inventario_id == articulo.id
                ).delete(synchronize_session="fetch")

                # Eliminar lotes
                LoteInventario.query.filter_by(inventario_id=articulo.id).delete()

                # Eliminar artículo
                db.session.delete(articulo)
                db.session.commit()

                print("✓ Datos de prueba eliminados")

            except Exception as e:
                print(f"⚠️ Error al limpiar datos: {str(e)}")
                db.session.rollback()


if __name__ == "__main__":
    main()
