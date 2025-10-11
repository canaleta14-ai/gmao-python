#!/usr/bin/env python3
"""
Script para probar el login y funcionalidades básicas del GMAO local
"""

import requests
import os

# Configurar entorno
os.environ["FLASK_ENV"] = "development"
os.environ["DB_TYPE"] = "sqlite"


def test_local_app():
    """Prueba las funcionalidades básicas de la aplicación local"""

    base_url = "http://localhost:5000"

    try:
        print("🔍 Probando aplicación GMAO local...")

        # Probar página principal
        print("   Verificando página principal...")
        response = requests.get(base_url)
        if response.status_code == 200:
            print("   ✅ Página principal accesible")
        else:
            print(f"   ❌ Error en página principal: {response.status_code}")
            return False

        # Probar página de login
        print("   Verificando página de login...")
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("   ✅ Página de login accesible")
        else:
            print(f"   ❌ Error en página de login: {response.status_code}")
            return False

        # Intentar obtener CSRF token
        session = requests.Session()
        login_page = session.get(f"{base_url}/login")

        if "csrf_token" in login_page.text:
            print("   ✅ CSRF Token disponible")

        print("🎉 ¡Aplicación local funcionando correctamente!")
        print("🌐 Accede a: http://localhost:5000")
        print("👤 Usa: admin / admin123")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación")
        print("   Asegúrate de que esté ejecutándose con: python run_local.py")
        return False

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


if __name__ == "__main__":
    test_local_app()
