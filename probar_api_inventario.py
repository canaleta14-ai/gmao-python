"""
Script para probar el endpoint de artículos del inventario
"""

import requests


def probar_endpoint():
    """Probar el endpoint de artículos"""
    try:
        # URL del endpoint
        url = "http://127.0.0.1:5000/inventario/api/articulos"

        # Hacer la petición
        response = requests.get(url)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nTotal artículos: {data.get('total', 0)}")
            print(f"Artículos en esta página: {len(data.get('articulos', []))}")

            # Mostrar primeros artículos
            if data.get("articulos"):
                print("\nPrimeros artículos:")
                for articulo in data["articulos"][:3]:
                    print(
                        f"  - {articulo.get('codigo')} - {articulo.get('descripcion')}"
                    )
        else:
            print("Error en la petición")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    probar_endpoint()
