#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de autenticación y carga de usuario
"""
import requests
import json

# Crear una sesión para mantener cookies
session = requests.Session()

print("🔍 Probando el sistema de autenticación y carga de usuario...")
print("=" * 60)

# Test 1: Intentar acceder al endpoint de información del usuario sin login
print("\n1. Probando acceso a /api/user/info sin autenticación...")
try:
    response = session.get("http://127.0.0.1:5000/api/user/info")
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Redirección correcta (usuario no autenticado)")
    elif response.status_code == 401:
        print("   ✅ Respuesta 401 correcta (usuario no autenticado)")
    else:
        print(f"   ‚ö† Respuesta inesperada: {response.status_code}")
        try:
            data = response.json()
            print(f"   Datos: {json.dumps(data, indent=2)}")
        except:
            print(f"   Contenido: {response.text[:200]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Hacer login con credenciales válidas
print("\n2. Probando login con credenciales admin/admin123...")
try:
    login_data = {"username": "admin", "password": "admin123"}

    response = session.post(
        "http://127.0.0.1:5000/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            if data.get("success"):
                print("   ✅ Login exitoso")
            else:
                print(f'   ❌ Login falló: {data.get("message", "Error desconocido")}')
        except:
            print("   ✅ Login exitoso (respuesta HTML)")
    else:
        print(f"   ❌ Error en login: {response.status_code}")
        try:
            data = response.json()
            print(f'   Error: {data.get("message", "Error desconocido")}')
        except:
            print(f"   Contenido: {response.text[:200]}...")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Ahora intentar acceder a la información del usuario autenticado
print("\n3. Probando acceso a /api/user/info después del login...")
try:
    response = session.get("http://127.0.0.1:5000/api/user/info")
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("   ✅ Información del usuario obtenida:")
            if data.get("success"):
                user = data.get("user", {})
                print(f'   ¢ Nombre: {user.get("nombre", "N/A")}')
                print(f'   ¢ Username: {user.get("username", "N/A")}')
                print(f'   ¢ Email: {user.get("email", "N/A")}')
                print(f'   ¢ Rol: {user.get("rol", "N/A")}')
                print(f'   ¢ Activo: {user.get("activo", "N/A")}')
            else:
                print(
                    f'   ❌ Error en respuesta: {data.get("error", "Error desconocido")}'
                )
        except Exception as json_error:
            print(f"   ❌ Error al parsear JSON: {json_error}")
            print(f"   Contenido: {response.text[:200]}...")
    else:
        print(f"   ❌ Error: {response.status_code}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Pruebas de autenticación completadas")
print("\nüìå Para probar completamente:")
print("   1. Abre http://127.0.0.1:5000 en el navegador")
print("   2. Haz login con admin/admin123")
print("   3. Verifica que el sidebar muestre el nombre y rol correctos")
print("   4. Verifica que no haya problemas de carga en el dashboard")
