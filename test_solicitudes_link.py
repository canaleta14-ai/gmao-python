#!/usr/bin/env python3
"""
Script para probar el enlace de solicitudes en el sidebar
"""

import requests


def test_solicitudes_link():
    # Crear sesión
    session = requests.Session()

    # Hacer login
    login_data = {"username": "admin", "password": "admin123"}
    login_response = session.post("http://localhost:5000/login", data=login_data)

    print(f"Login status: {login_response.status_code}")

    if login_response.status_code in [200, 302]:
        print("✅ Login exitoso")

        # Acceder a solicitudes admin
        response = session.get("http://localhost:5000/admin/solicitudes/")
        print(f"Solicitudes admin status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Enlace de solicitudes funciona correctamente")
            if "Gestión de Solicitudes" in response.text:
                print("✅ Página de gestión de solicitudes cargada correctamente")
                return True
            else:
                print("⚠️ Página cargada pero contenido no esperado")
                print("Contenido (primeros 300 chars):", response.text[:300])
                return False
        else:
            print(f"❌ Error al acceder a solicitudes: {response.status_code}")
            print("Respuesta:", response.text[:300])
            return False
    else:
        print("❌ Error en login")
        print("Respuesta login:", login_response.text[:300])
        return False


if __name__ == "__main__":
    test_solicitudes_link()
