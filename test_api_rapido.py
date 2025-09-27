#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rápido para verificar APIs de categorías
"""

import requests
import json


def test_api_categorias():
    """Test de la API de categorías"""

    base_url = "http://127.0.0.1:5000"

    try:
        print("=== Test API Categorías ===\n")

        # 1. Test obtener todas las categorías
        print("1. Probando GET /api/categorias/")
        response = requests.get(f"{base_url}/api/categorias/")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Éxito: {data.get('total', 0)} categorías encontradas")

            if data.get("categorias"):
                categoria = data["categorias"][0]
                categoria_id = categoria["id"]
                print(
                    f"   📝 Primera categoría: {categoria['nombre']} ({categoria['prefijo']})"
                )

                # 2. Test generar código
                print(f"\n2. Probando GET /api/categorias/{categoria_id}/codigo")
                codigo_response = requests.get(
                    f"{base_url}/api/categorias/{categoria_id}/codigo"
                )
                print(f"   Status: {codigo_response.status_code}")

                if codigo_response.status_code == 200:
                    codigo_data = codigo_response.json()
                    if codigo_data.get("success"):
                        print(f"   ✅ Código generado: {codigo_data['codigo']}")
                    else:
                        print(f"   ❌ Error: {codigo_data.get('message')}")
                else:
                    print(f"   ❌ Error HTTP {codigo_response.status_code}")

        else:
            print(f"   ❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Error desconocido')}")
            except:
                print(f"   Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor en http://127.0.0.1:5000")
        print("   Asegúrese de que Flask esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")


if __name__ == "__main__":
    test_api_categorias()
