#!/usr/bin/env python3
"""
Test para verificar los movimientos de inventario
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models.movimiento_inventario import MovimientoInventario
from app.controllers.inventario_controller_simple import obtener_movimientos_articulo
from app.extensions import db


def test_movimientos():
    """Test para verificar movimientos en la base de datos"""
    app = create_app()

    with app.app_context():
        print("🧪 Verificando movimientos de inventario...")

        # Test 1: Verificar si hay movimientos en la base de datos
        print("\n1️⃣ Conteo total de movimientos:")
        total_movimientos = db.session.query(MovimientoInventario).count()
        print(f"   Total de movimientos: {total_movimientos}")

        if total_movimientos == 0:
            print("   ❌ No hay movimientos registrados en la base de datos")
            print("   💡 Necesitas crear algunos movimientos primero")
            return

        # Test 2: Mostrar algunos movimientos de ejemplo
        print("\n2️⃣ Primeros 5 movimientos:")
        movimientos = db.session.query(MovimientoInventario).limit(5).all()
        for i, mov in enumerate(movimientos):
            print(
                f"   {i+1}. ID: {mov.id}, Inventario: {mov.inventario_id}, Tipo: {mov.tipo}, Cantidad: {mov.cantidad}"
            )

        # Test 3: Verificar movimientos por inventario específico
        print("\n3️⃣ Movimientos por inventario:")
        inventario_ids = (
            db.session.query(MovimientoInventario.inventario_id)
            .distinct()
            .limit(3)
            .all()
        )

        for inventario_tuple in inventario_ids:
            inventario_id = inventario_tuple[0]
            print(f"\n   📦 Inventario ID {inventario_id}:")

            # Usar la función del controlador
            try:
                data = obtener_movimientos_articulo(inventario_id, 1, 10)
                print(f"      Success: {data.get('success', 'N/A')}")
                print(f"      Total: {data.get('total', 0)}")
                if data.get("movimientos"):
                    print(f"      Movimientos encontrados: {len(data['movimientos'])}")
                    for mov in data["movimientos"][:2]:  # Solo primeros 2
                        print(
                            f"         - {mov.get('fecha', 'N/A')}: {mov.get('tipo', 'N/A')} de {mov.get('cantidad', 'N/A')}"
                        )
                else:
                    print("      ⚠️ Sin movimientos en respuesta")
            except Exception as e:
                print(f"      ❌ Error en controlador: {e}")


if __name__ == "__main__":
    test_movimientos()
