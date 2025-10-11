#!/usr/bin/env python3
"""
Script simplificado para probar módulos principales del GMAO
"""

import requests
import time
import re

BASE_URL = "http://localhost:5000"


def test_endpoint(name, url, expected_status=200):
    """Prueba un endpoint específico"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Error de conexión - {e}")
        return False


def test_login():
    """Prueba el login del sistema"""
    print("🔐 Probando sistema de login...")

    session = requests.Session()

    try:
        # Obtener página de login
        response = session.get(f"{BASE_URL}/login")
        if response.status_code != 200:
            print(f"❌ Login page: Error {response.status_code}")
            return False

        # Extraer token CSRF
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if not csrf_match:
            print("❌ Login: No se pudo obtener token CSRF")
            return False

        csrf_token = csrf_match.group(1)

        # Intentar login
        login_data = {
            "username": "admin",
            "password": "admin123",
            "csrf_token": csrf_token,
        }

        response = session.post(f"{BASE_URL}/login", data=login_data)

        if response.status_code == 302:  # Redirección = login exitoso
            print("✅ Login: Exitoso")
            return True
        else:
            print(f"❌ Login: Falló ({response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Login: Error - {e}")
        return False


def main():
    print("🚀 Sistema de Pruebas GMAO - Versión Simplificada")
    print("=" * 60)

    # Verificar que la aplicación esté disponible
    print("🔍 Verificando disponibilidad de la aplicación...")
    time.sleep(2)  # Dar tiempo a que arranque

    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"✅ Aplicación disponible en {BASE_URL} ({response.status_code})")
    except Exception as e:
        print(f"❌ No se puede conectar a {BASE_URL}: {e}")
        print(
            "⚠️ Asegúrate de que la aplicación esté ejecutándose con 'python run_direct_local.py'"
        )
        return False

    print("\n📋 Probando módulos principales...")

    # Lista de endpoints a probar
    tests = [
        ("Dashboard", f"{BASE_URL}/"),
        ("Login Page", f"{BASE_URL}/login"),
        ("Usuarios", f"{BASE_URL}/usuarios"),
        ("Activos", f"{BASE_URL}/activos"),
        ("Órdenes de Trabajo", f"{BASE_URL}/ordenes"),
        ("Planes de Mantenimiento", f"{BASE_URL}/planes"),
        ("Inventario", f"{BASE_URL}/inventario"),
        ("Proveedores", f"{BASE_URL}/proveedores"),
        ("Solicitudes", f"{BASE_URL}/solicitudes"),
        ("Reportes", f"{BASE_URL}/reportes"),
    ]

    results = []

    # Probar endpoints
    for name, url in tests:
        result = test_endpoint(name, url)
        results.append((name, result))

    # Probar login específicamente
    print("\n🔐 Probando funcionalidad de login...")
    login_result = test_login()
    results.append(("Login Funcional", login_result))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name:25} {status}")

    print("-" * 60)
    print(f"Total pruebas: {len(results)}")
    print(f"✅ Pasaron: {passed}")
    print(f"❌ Fallaron: {failed}")
    print(f"📈 Éxito: {(passed/len(results)*100):.1f}%")

    if failed == 0:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema GMAO está funcionando correctamente en local.")
    elif failed <= 2:
        print(f"\n⚠️ Sistema funcional con {failed} problemas menores.")
    else:
        print(f"\n❌ Sistema con {failed} problemas importantes.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏁 Sistema listo para usar en local.")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin123")
        print("🌐 URL: http://localhost:5000")
    else:
        print("\n🔧 Revisa los errores anteriores para solucionar problemas.")
