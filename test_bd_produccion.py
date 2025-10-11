#!/usr/bin/env python3
"""
Script para inicializar la base de datos de producción via HTTP
"""
import requests
import time


def inicializar_bd_produccion():
    """Inicializa la base de datos de producción usando un endpoint HTTP"""

    print("🚀 INICIALIZANDO BASE DE DATOS VIA HTTP")
    print("=" * 50)

    base_url = "https://mantenimiento-470311.ew.r.appspot.com"

    # Esperar a que la aplicación esté lista
    print("🔄 Esperando a que la aplicación esté lista...")
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/health", timeout=30)
            if response.status_code == 200:
                print("✅ Aplicación lista")
                break
        except Exception as e:
            print(f"⏳ Intento {i+1}/5 - Esperando... ({e})")
            time.sleep(10)
    else:
        print("❌ La aplicación no responde")
        return False

    # Llamar al endpoint de inicialización de BD
    print("\n📋 Iniciando parches de base de datos...")
    try:
        response = requests.get(f"{base_url}/api/cron/db-fix", timeout=60)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Respuesta: {data}")
            except:
                print(f"   Respuesta: {response.text[:200]}...")

    except Exception as e:
        print(f"   ⚠️ Error: {e}")

    # Intentar acceder a la página de login
    print("\n🔐 Verificando acceso a login...")
    try:
        response = requests.get(f"{base_url}/login", timeout=30)
        print(f"   Status login: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Página de login accesible")
        elif response.status_code == 500:
            print("   ❌ Error 500 - Problema con la base de datos")
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error accediendo al login: {e}")

    # Probar login
    print("\n👤 Probando login con admin/admin123...")
    try:
        session = requests.Session()
        login_data = {"username": "admin", "password": "admin123"}
        response = session.post(f"{base_url}/login", json=login_data, timeout=30)
        print(f"   Status login POST: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    print("   ✅ Login exitoso!")
                else:
                    print(
                        f"   ❌ Login falló: {data.get('error', 'Error desconocido')}"
                    )
            except:
                print("   ⚠️ Respuesta no JSON")
        elif response.status_code == 401:
            print("   ❌ Credenciales incorrectas o usuario no existe")
        elif response.status_code == 500:
            print("   ❌ Error 500 - Problema con la base de datos")
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error en login: {e}")

    print("\n" + "=" * 50)
    print("🎯 RESUMEN:")
    print("   🌐 URL: https://mantenimiento-470311.ew.r.appspot.com")
    print("   👤 Usuario: admin")
    print("   🔑 Contraseña: admin123")
    print("\n🔍 Si el login aún no funciona, puede necesitarse más tiempo")
    print("   para que la base de datos se inicialice completamente.")


if __name__ == "__main__":
    inicializar_bd_produccion()
