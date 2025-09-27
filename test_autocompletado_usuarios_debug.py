#!/usr/bin/env python3
"""
Script para probar el autocompletado de usuarios en conteos
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"


def test_autocompletado_usuarios():
    print("🧪 PRUEBA DEL AUTOCOMPLETADO DE USUARIOS")
    print("=" * 50)

    # Crear una sesión para mantener cookies
    session = requests.Session()

    # 1. Verificar que la página de conteos se carga
    print("1️⃣ Verificando página de conteos...")
    try:
        response = session.get(f"{BASE_URL}/inventario/conteos")
        print(f"   Status: {response.status_code}")

        # Buscar elementos clave en el HTML
        html = response.text
        checks = [
            ("conteo-usuario input", 'id="conteo-usuario"' in html),
            ("conteos.js script", "conteos.js" in html),
            ("autocomplete.js", "autocomplete.js" in html),
        ]

        for check, found in checks:
            status = "✅" if found else "❌"
            print(f"   {status} {check}: {'Presente' if found else 'Ausente'}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # 2. Intentar hacer login para acceder a la API de usuarios
    print("\n2️⃣ Intentando acceso sin login...")
    try:
        response = session.get(f"{BASE_URL}/usuarios/api/autocomplete?q=admin")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Usuarios encontrados: {len(data)}")
                for user in data[:3]:  # Mostrar máximo 3
                    print(
                        f"      - {user.get('username', 'N/A')}: {user.get('nombre', 'N/A')}"
                    )
            except:
                print(f"   ⚠️ Respuesta no JSON: {response.text[:100]}...")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            if "login" in response.text.lower():
                print("   🔒 Requiere autenticación")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 3. Verificar si hay usuarios en la base de datos
    print("\n3️⃣ Verificando datos de prueba...")
    try:
        # Intentar una consulta simple que no requiera auth
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✅ Servidor funcionando")

        print("\n💡 INSTRUCCIONES PARA PRUEBA MANUAL:")
        print("   1. Ve a http://127.0.0.1:5000/login")
        print("   2. Inicia sesión con tus credenciales")
        print("   3. Ve a http://127.0.0.1:5000/inventario/conteos")
        print("   4. Haz clic en cualquier fila de conteo pendiente")
        print("   5. En el modal, prueba escribir en el campo 'Usuario'")
        print("   6. Deberías ver sugerencias de autocompletado")

    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_autocompletado_usuarios()
