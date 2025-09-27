#!/usr/bin/env python3
"""
Script para probar autocompletado con sesión autenticada
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def test_with_login():
    print("🔐 PRUEBA CON AUTENTICACIÓN")
    print("=" * 50)

    # Crear una sesión
    session = requests.Session()

    # 1. Intentar hacer login (si existe la funcionalidad)
    print("1️⃣ Intentando login...")
    try:
        # Primero obtener la página de login para ver si existe
        login_page = session.get(f"{BASE_URL}/login", timeout=10)
        print(f"   Login page status: {login_page.status_code}")

        if login_page.status_code == 200:
            # Intentar login con credenciales por defecto
            login_data = {
                "username": "admin",
                "password": "admin123",  # Contraseña común por defecto
            }

            login_response = session.post(
                f"{BASE_URL}/login", data=login_data, timeout=10
            )
            print(f"   Login attempt status: {login_response.status_code}")

            # Verificar si estamos autenticados probando una página protegida
            dashboard = session.get(f"{BASE_URL}/dashboard", timeout=10)
            print(f"   Dashboard access: {dashboard.status_code}")

            if dashboard.status_code == 200 and "dashboard" in dashboard.text.lower():
                print("   ✅ Autenticación exitosa")

                # Ahora probar la API de usuarios
                print("\n2️⃣ Probando API de usuarios autenticada...")
                api_response = session.get(
                    f"{BASE_URL}/usuarios/api/autocomplete?q=admin&limit=5", timeout=10
                )
                print(f"   API Status: {api_response.status_code}")
                print(f"   Content-Type: {api_response.headers.get('Content-Type')}")

                if "application/json" in api_response.headers.get("Content-Type", ""):
                    data = api_response.json()
                    print(f"   ✅ Usuarios encontrados: {len(data)}")
                    if data:
                        print(f"   📋 Primer usuario: {data[0].get('username', 'N/A')}")
                else:
                    print(f"   ❌ API devuelve HTML, no JSON")
            else:
                print("   ❌ Autenticación fallida")
        else:
            print("   ⚠️ Página de login no disponible")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n💡 ALTERNATIVA:")
    print("   Como el autocompletado necesita autenticación,")
    print("   puedes probar manualmente:")
    print("   1. Ve a http://127.0.0.1:5000/login")
    print("   2. Inicia sesión con tus credenciales")
    print("   3. Ve a http://127.0.0.1:5000/inventario/conteos")
    print("   4. Prueba el autocompletado en el modal de conteo")


if __name__ == "__main__":
    test_with_login()
