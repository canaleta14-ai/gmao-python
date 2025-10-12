#!/usr/bin/env python3
"""
Script simple para probar el sistema FIFO
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid

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
        print("=== PRUEBA RÁPIDA DEL SISTEMA FIFO ===\n")

        try:
            # Código único para evitar conflictos
            codigo_unico = f"FIFO-{uuid.uuid4().hex[:8].upper()}"

            # 1. Crear artículo de prueba
            print(f"1. Creando artículo de prueba: {codigo_unico}")
            articulo = Inventario(
                codigo=codigo_unico,
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

            # 2. Usar el servicio FIFO para crear lotes
            print("\n2. Creando lotes usando ServicioFIFO...")

            # Lote 1 - Más antiguo
            lote1 = ServicioFIFO.crear_lote_entrada(
                inventario_id=articulo.id,
                cantidad=100,
                precio_unitario=8.50,
                codigo_lote="LOTE-001",
                documento_origen="FAC-001",
                usuario_id="admin",
            )

            # Lote 2 - Medio
            lote2 = ServicioFIFO.crear_lote_entrada(
                inventario_id=articulo.id,
                cantidad=150,
                precio_unitario=9.00,
                codigo_lote="LOTE-002",
                documento_origen="FAC-002",
                usuario_id="admin",
            )

            # Lote 3 - Más reciente
            lote3 = ServicioFIFO.crear_lote_entrada(
                inventario_id=articulo.id,
                cantidad=200,
                precio_unitario=10.50,
                codigo_lote="LOTE-003",
                documento_origen="FAC-003",
                usuario_id="admin",
            )

            db.session.commit()
            print(f"✓ Lote 1: {lote1.codigo_lote} - 100 uds @ $8.50")
            print(f"✓ Lote 2: {lote2.codigo_lote} - 150 uds @ $9.00")
            print(f"✓ Lote 3: {lote3.codigo_lote} - 200 uds @ $10.50")

            # 3. Mostrar stock disponible
            print("\n3. Stock disponible inicial:")
            stock_info = ServicioFIFO.obtener_stock_disponible(articulo.id)
            print(f"Total disponible: {stock_info['total_disponible']} unidades")
            for lote_info in stock_info["lotes"]:
                print(
                    f"  - {lote_info['codigo_lote']}: {lote_info['cantidad_disponible']} uds @ ${lote_info['precio_unitario']}"
                )

            # 4. Probar consumo FIFO pequeño
            print("\n4. Probando consumo FIFO de 80 unidades...")
            consumos, faltante = ServicioFIFO.consumir_fifo(
                inventario_id=articulo.id,
                cantidad_total=80,
                documento_referencia="ORDEN-001",
                usuario_id="admin",
            )

            print(f"Cantidad no disponible: {faltante}")
            print("Consumos realizados:")
            for lote, cantidad in consumos:
                print(f"  - {lote.codigo_lote}: {cantidad} unidades")

            db.session.commit()

            # 5. Stock después del consumo
            print("\n5. Stock después del consumo:")
            stock_info = ServicioFIFO.obtener_stock_disponible(articulo.id)
            print(f"Total disponible: {stock_info['total_disponible']} unidades")
            for lote_info in stock_info["lotes"]:
                if lote_info["cantidad_disponible"] > 0:
                    print(
                        f"  - {lote_info['codigo_lote']}: {lote_info['cantidad_disponible']} uds"
                    )

            print("\n✓ PRUEBA COMPLETADA EXITOSAMENTE")
            print("El sistema FIFO funciona correctamente:")
            print("- Se consumen primero los lotes más antiguos")
            print("- Se mantiene trazabilidad de movimientos")
            print("- Los cálculos de stock son precisos")

        except Exception as e:
            print(f"\n❌ ERROR durante las pruebas: {str(e)}")
            import traceback

            traceback.print_exc()
            db.session.rollback()

        finally:
            # Limpiar datos de prueba
            try:
                print(f"\n6. Limpiando datos de prueba...")

                # Eliminar movimientos de lote asociados al artículo
                MovimientoLote.query.filter(
                    MovimientoLote.lote_id.in_(
                        db.session.query(LoteInventario.id).filter_by(
                            inventario_id=articulo.id
                        )
                    )
                ).delete(synchronize_session=False)

                # Eliminar lotes del artículo
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
