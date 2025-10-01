"""
Script para probar directamente la función listar_ordenes del controlador.
"""

from app import create_app
from app.extensions import db


def test_listar_ordenes():
    """Prueba la función listar_ordenes directamente."""
    app = create_app()

    with app.app_context():
        print("=" * 80)
        print("PROBANDO FUNCIÓN listar_ordenes(limit=5)")
        print("=" * 80)
        print()

        try:
            from app.controllers.ordenes_controller import listar_ordenes

            print("📋 Llamando a listar_ordenes(estado=None, limit=5)...")
            ordenes = listar_ordenes(estado=None, limit=5)

            print(f"✅ Éxito! Recibidas {len(ordenes)} órdenes")
            print()

            for orden in ordenes:
                print(f"  📋 {orden['numero_orden']}")
                print(f"     Estado: {orden['estado']}")
                print(f"     Técnico: {orden.get('tecnico_nombre', 'Sin asignar')}")
                print(f"     Activo: {orden.get('activo_nombre', 'Sin activo')}")
                print()

        except Exception as e:
            print(f"❌ Excepción: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            import traceback

            print()
            print("Traceback completo:")
            traceback.print_exc()

        print()
        print("=" * 80)


if __name__ == "__main__":
    test_listar_ordenes()
