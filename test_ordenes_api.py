"""
Script para probar el endpoint de órdenes y ver el error detallado.
"""

import requests
from app import create_app
from app.extensions import db
from app.models.usuario import Usuario


def test_ordenes_endpoint():
    """Prueba el endpoint de órdenes directamente."""
    app = create_app()

    with app.app_context():
        # Crear cliente de prueba
        client = app.test_client()

        # Obtener un usuario para autenticación
        usuario = Usuario.query.filter_by(activo=True).first()

        if not usuario:
            print("❌ No hay usuarios activos en el sistema")
            return

        # Iniciar sesión
        with client.session_transaction() as sess:
            sess["user_id"] = usuario.id
            sess["username"] = usuario.username

        print("=" * 80)
        print("PROBANDO ENDPOINT /ordenes/api?limit=5")
        print("=" * 80)
        print(f"Usuario: {usuario.username}")
        print()

        # Hacer petición
        try:
            response = client.get("/ordenes/api?limit=5")

            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.content_type}")
            print()

            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Éxito! Recibidas {len(data)} órdenes")
                print()
                for orden in data:
                    print(f"  📋 {orden['numero_orden']}")
                    print(f"     Estado: {orden['estado']}")
                    print(f"     Técnico: {orden.get('tecnico_nombre', 'Sin asignar')}")
                    print()
            else:
                print(f"❌ Error {response.status_code}")
                print("Respuesta:")
                print(response.get_data(as_text=True))

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
    test_ordenes_endpoint()
