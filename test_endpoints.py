import requests

try:
    print("Probando endpoint de estadísticas...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/estadisticas")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error de conexión: {e}")

print("\n" + "=" * 50 + "\n")

try:
    print("Probando endpoint de artículos...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/articulos")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f'Total artículos: {data.get("total", 0)}')
        print(f'Artículos en respuesta: {len(data.get("articulos", []))}')
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error de conexión: {e}")
