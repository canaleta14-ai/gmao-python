import requests

try:
    print("Probando página principal de inventario...")
    response = requests.get("http://127.0.0.1:5000/inventario/")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Página de inventario carga correctamente")
        # Verificar si contiene elementos clave
        if "loading-row" in response.text:
            print("✅ Spinner de carga encontrado en el HTML")
        if "tabla-inventario-body" in response.text:
            print("✅ Tabla de inventario encontrada en el HTML")
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
