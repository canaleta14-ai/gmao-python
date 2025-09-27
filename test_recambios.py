"""
Test rápido para validar la funcionalidad de recambios en órdenes
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def test_recambios():
    print("🧪 Probando API de recambios...")

    # Primero, intentar obtener recambios de una orden (probablemente vacía)
    try:
        response = requests.get(f"{BASE_URL}/api/ordenes/1/recambios")
        print(f"📋 GET recambios orden 1: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Recambios encontrados: {len(data.get('recambios', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en GET recambios: {e}")

    # Probar agregar un recambio (necesitamos una orden y un artículo existente)
    try:
        # Datos de prueba - usar IDs que probablemente existan
        test_data = {
            "inventario_id": 1,
            "cantidad_solicitada": 5,
            "observaciones": "Prueba de recambio",
        }

        response = requests.post(
            f"{BASE_URL}/api/ordenes/1/recambios",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
        )

        print(f"📦 POST nuevo recambio: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data.get('message', 'Recambio agregado')}")
        else:
            data = response.json()
            print(f"   ⚠️ {data.get('error', 'Error desconocido')}")

    except Exception as e:
        print(f"❌ Error en POST recambio: {e}")

    print("🏁 Test completado")


if __name__ == "__main__":
    test_recambios()
