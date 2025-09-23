import requests

# Test directo de los endpoints de inventario
try:
    print("🔍 Probando endpoint de artículos...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/articulos")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total artículos: {data.get('total', 0)}")
        print(f"✅ Artículos en respuesta: {len(data.get('articulos', []))}")

        # Mostrar algunos artículos si existen
        if data.get("articulos"):
            print("📦 Primeros artículos:")
            for i, articulo in enumerate(data["articulos"][:3]):
                print(
                    f"  {i+1}. {articulo.get('nombre', 'Sin nombre')} - Stock: {articulo.get('stock_actual', 0)}"
                )
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error de conexión: {e}")

print("\n" + "=" * 50 + "\n")

try:
    print("📊 Probando endpoint de estadísticas...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/estadisticas")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Estadísticas obtenidas:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
