#!/usr/bin/env python3
"""
Script para inicializar la base de datos mediante HTTP requests
"""
import requests
import time
import sys


def test_application():
    """Prueba la aplicación paso a paso"""
    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    print("=== INICIANDO VERIFICACIÓN DE APLICACIÓN ===")

    # 1. Verificar que la aplicación responde
    print("1. Verificando conectividad...")
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Aplicación responde correctamente")
        else:
            print(f"   ❌ Aplicación devuelve error: {response.status_code}")
            print(f"   Respuesta: {response.text[:500]}")
    except Exception as e:
        print(f"   ❌ Error conectando: {e}")
        return False

    # 2. Verificar endpoint de salud
    print("2. Verificando endpoint de salud...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sistema de salud OK: {data}")
        else:
            print(f"   ❌ Endpoint de salud falla: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en endpoint de salud: {e}")

    # 3. Intentar hacer login
    print("3. Probando login...")
    session = requests.Session()

    # Primero obtener la página de login para el CSRF token
    try:
        login_page = session.get(f"{base_url}/auth/login", timeout=30)
        print(f"   Página de login status: {login_page.status_code}")

        if login_page.status_code == 200:
            # Intentar login
            login_data = {"username": "admin", "password": "admin123"}

            login_response = session.post(
                f"{base_url}/auth/login",
                data=login_data,
                timeout=30,
                allow_redirects=False,
            )

            print(f"   Login status: {login_response.status_code}")
            if login_response.status_code in [200, 302]:
                print("   ✅ Login funciona correctamente")

                # Verificar dashboard
                dashboard = session.get(f"{base_url}/dashboard", timeout=30)
                print(f"   Dashboard status: {dashboard.status_code}")
                if dashboard.status_code == 200:
                    print("   ✅ Dashboard accesible")
                else:
                    print(f"   ❌ Dashboard inaccesible: {dashboard.status_code}")
            else:
                print(f"   ❌ Login falla: {login_response.status_code}")
                print(f"   Respuesta: {login_response.text[:500]}")
        else:
            print("   ❌ No se puede acceder a la página de login")

    except Exception as e:
        print(f"   ❌ Error en login: {e}")

    print("=== VERIFICACIÓN COMPLETADA ===")
    return True


if __name__ == "__main__":
    test_application()
