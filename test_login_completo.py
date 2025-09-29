#!/usr/bin/env python3
"""
Script para probar el login completo via API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("🌐 PRUEBA DE LOGIN VIA WEB:")
print("=" * 40)

# Crear una sesión para mantener cookies
session = requests.Session()

try:
    # 1. Probar acceso a página protegida sin login
    print("1. Probando acceso sin login a /usuarios...")
    response = session.get(f"{BASE_URL}/usuarios")
    if response.status_code == 302 and "/login" in response.headers.get("Location", ""):
        print("✅ Redirección correcta a login")
    else:
        print(f"❌ Respuesta inesperada: {response.status_code}")

    # 2. Probar login
    print("\n2. Probando login con admin/admin123...")
    login_data = {"username": "admin", "password": "admin123"}

    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code == 200 or response.status_code == 302:
        print("✅ Login exitoso")

        # 3. Probar acceso a página protegida después del login
        print("\n3. Probando acceso a /usuarios después del login...")
        response = session.get(f"{BASE_URL}/usuarios")
        if response.status_code == 200:
            print("✅ Acceso a usuarios exitoso")

            # 4. Probar API de usuarios
            print("\n4. Probando API /usuarios/api...")
            response = session.get(f"{BASE_URL}/usuarios/api")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API usuarios funciona - {len(data)} usuarios encontrados")
            else:
                print(f"❌ Error en API usuarios: {response.status_code}")
        else:
            print(f"❌ Error accediendo a usuarios: {response.status_code}")
    else:
        print(f"❌ Error en login: {response.status_code}")
        print("Respuesta:", response.text[:200])

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 40)
print("CREDENCIALES DE PRUEBA:")
print("Usuario: admin")
print("Contraseña: admin123")
print("=" * 40)
