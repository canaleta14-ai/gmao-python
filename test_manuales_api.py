#!/usr/bin/env python3
"""
Test rápido para verificar que la API de manuales funciona correctamente
"""
import requests
import json


def test_manuales_api():
    """Test simple para la API de manuales"""
    base_url = "http://127.0.0.1:5000"

    try:
        # Test 1: Obtener manuales de activo ID 2
        print("🧪 Testing manuales API...")
        response = requests.get(f"{base_url}/activos/api/2/manuales", timeout=5)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: API respondió correctamente")
            print(f"📄 Datos recibidos: {json.dumps(data, indent=2)}")
        elif response.status_code == 500:
            print(f"❌ ERROR 500: {response.text}")
        else:
            print(f"⚠️  Código inesperado {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando JSON: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_manuales_api()
