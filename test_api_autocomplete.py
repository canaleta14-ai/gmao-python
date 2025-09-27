# Test script para verificar el autocompletado
import requests
import json


def test_api():
    """Test para verificar que la API funciona"""
    print("🧪 Probando API de artículos...")

    try:
        # Test con localhost (ajusta el puerto si es necesario)
        url = "http://localhost:5000/inventario/api/articulos"

        # Test 1: Sin parámetros
        print("\n1️⃣ Test sin parámetros...")
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Artículos encontrados: {len(data.get('articulos', []))}")

        # Test 2: Con parámetro 'q'
        print("\n2️⃣ Test con parámetro 'q=a'...")
        response = requests.get(url, params={"q": "a", "per_page": 5})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Artículos encontrados: {len(data.get('articulos', []))}")
            if data.get("articulos"):
                print("Primer artículo:")
                print(json.dumps(data["articulos"][0], indent=2, ensure_ascii=False))

        # Test 3: Con parámetro 'busqueda'
        print("\n3️⃣ Test con parámetro 'busqueda=a'...")
        response = requests.get(url, params={"busqueda": "a", "per_page": 5})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Artículos encontrados: {len(data.get('articulos', []))}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ No se pudo conectar al servidor. ¿Está ejecutándose en localhost:5000?"
        )
        print("   Ejecuta: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_api()
