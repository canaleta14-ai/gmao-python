import requests

# Test directo de los endpoints de inventario
try:
    print("ğŸ”� Probando endpoint de artÃ­culos...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/articulos")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"âœ… Total artÃ­culos: {data.get('total', 0)}")
        print(f"âœ… ArtÃ­culos en respuesta: {len(data.get('articulos', []))}")

        # Mostrar algunos artÃ­culos si existen
        if data.get("articulos"):
            print("ğŸ“¦ Primeros artÃ­culos:")
            for i, articulo in enumerate(data["articulos"][:3]):
                print(
                    f"  {i+1}. {articulo.get('nombre', 'Sin nombre')} - Stock: {articulo.get('stock_actual', 0)}"
                )
    else:
        print(f"â�Œ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"â�Œ Error de conexiÃ³n: {e}")

print("\n" + "=" * 50 + "\n")

try:
    print("ğŸ“Š Probando endpoint de estadÃ­sticas...")
    response = requests.get("http://127.0.0.1:5000/inventario/api/estadisticas")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"âœ… EstadÃ­sticas obtenidas:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print(f"â�Œ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"â�Œ Error de conexiÃ³n: {e}")
