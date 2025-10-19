#!/usr/bin/env python3
"""
Script para probar el login y verificar que el sistema funciona correctamente
"""
import requests
import json


def test_login_and_user_info():
    """Prueba el login y obtención de información de usuario"""
    base_url = "http://localhost:5000"

    # Datos de login
    login_data = {"username": "admin", "password": "admin123"}

    print("🔧 Probando el sistema GMAO...")

    # Crear sesión para mantener cookies
    session = requests.Session()

    try:
        # 1. Probar login
        print("1️⃣ Probando login...")
        login_response = session.post(
            f"{base_url}/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"   Status: {login_response.status_code}")

        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"   Respuesta: {login_result}")

            if login_result.get("success"):
                print("   ✅ Login exitoso")

                # 2. Probar obtener información de usuario
                print("2️⃣ Probando /api/user/info...")
                user_info_response = session.get(f"{base_url}/api/user/info")
                print(f"   Status: {user_info_response.status_code}")

                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    print("   ✅ Información de usuario obtenida correctamente:")
                    print(f"   📝 Usuario: {user_info}")

                    return True
                else:
                    print(
                        f"   ❌ Error obteniendo info de usuario: {user_info_response.status_code}"
                    )
                    print(f"   📝 Respuesta: {user_info_response.text}")
                    return False
            else:
                print(f"   ❌ Login falló: {login_result}")
                return False
        else:
            print(f"   ❌ Error en login: {login_response.status_code}")
            print(f"   📝 Respuesta: {login_response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema GMAO")

    success = test_login_and_user_info()

    if success:
        print("\n✅ ¡Todas las pruebas pasaron exitosamente!")
        print("🎉 El sistema GMAO está funcionando correctamente")
        print("\n📋 Resumen:")
        print("  - Base de datos: gmao_sistema_db (PostgreSQL)")
        print("  - Usuario admin: admin / admin123")
        print("  - Login: ✅ Funcionando")
        print("  - API user info: ✅ Funcionando")
    else:
        print("\n❌ Hay problemas con el sistema")
        print("🔍 Revisa los logs del servidor para más detalles")
