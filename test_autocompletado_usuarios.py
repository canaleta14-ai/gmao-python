#!/usr/bin/env python3
"""
Script para probar el autocompletado de usuarios en conteos
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def test_autocompletado_usuarios():
    print("🔍 PRUEBA DEL AUTOCOMPLETADO DE USUARIOS EN CONTEOS")
    print("=" * 60)

    # 1. Verificar API de usuarios
    print("1️⃣ Probando API de usuarios...")
    try:
        response = requests.get(f"{BASE_URL}/usuarios/api?q=admin&limit=5", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            usuarios = data.get("usuarios", [])
            print(f"   ✅ Usuarios encontrados: {len(usuarios)}")
            if usuarios:
                user = usuarios[0]
                print(f"   📋 Primer usuario:")
                print(f"      - Username: {user.get('username', 'N/A')}")
                print(
                    f"      - Nombre: {user.get('nombre', 'N/A')} {user.get('apellido', 'N/A')}"
                )
                print(f"      - Rol: {user.get('rol', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

    # 2. Verificar que existen conteos para probar
    print("\n2️⃣ Verificando conteos disponibles...")
    try:
        response = requests.get(
            f"{BASE_URL}/inventario/api/conteos/resumen", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            resumen = data.get("resumen", {})
            print(f"   ✅ Conteos pendientes: {resumen.get('conteos_pendientes', 0)}")

            if resumen.get("conteos_pendientes", 0) == 0:
                print("   🎲 Generando algunos conteos para probar...")
                gen_response = requests.post(
                    f"{BASE_URL}/inventario/api/conteos/aleatorios",
                    json={"cantidad": 3},
                    timeout=10,
                )
                if gen_response.status_code == 200:
                    print("   ✅ Conteos generados exitosamente")
                else:
                    print(f"   ❌ Error generando conteos: {gen_response.text}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

    # 3. Verificar página web
    print("\n3️⃣ Verificando página de conteos...")
    try:
        response = requests.get(f"{BASE_URL}/inventario/conteos", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            checks = [
                ("conteo-usuario input", 'id="conteo-usuario"' in content),
                ("conteos.js script", "conteos.js" in content),
                ("autocomplete.js script", "autocomplete.js" in content),
                ("bootstrap modal", "modalProcesarConteo" in content),
            ]

            for check, found in checks:
                status = "✅" if found else "❌"
                print(f"   {status} {check}: {'Presente' if found else 'Ausente'}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

    print("\n🎯 INSTRUCCIONES PARA PROBAR:")
    print("   1. Ve a: http://127.0.0.1:5000/inventario/conteos")
    print("   2. Haz clic en el botón de procesar (✓) en cualquier conteo pendiente")
    print("   3. En el modal, ve al campo 'Usuario que realizó el conteo'")
    print("   4. Escribe 'admin' o cualquier nombre de usuario")
    print("   5. Deberías ver un desplegable con opciones de autocompletado")
    print("   6. Selecciona un usuario y completa el conteo")


if __name__ == "__main__":
    test_autocompletado_usuarios()
