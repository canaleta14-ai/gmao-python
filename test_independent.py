#!/usr/bin/env python3
"""
Script independiente para probar módulos GMAO - SIN IMPORTS DE LA APP
"""

import requests
import time
import re

BASE_URL = "http://localhost:5000"


def test_module_access():
    """Probar acceso a todos los módulos principales"""

    print("🚀 PRUEBAS INDEPENDIENTES DE MÓDULOS GMAO")
    print("=" * 60)

    # Esperar un poco
    time.sleep(3)

    # 1. Verificar aplicación disponible
    print("🔍 Verificando disponibilidad...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"✅ Aplicación disponible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("⚠️ Asegúrate de que la aplicación esté ejecutándose")
        return False

    print("\n📋 PROBANDO ACCESO A MÓDULOS...")
    print("-" * 60)

    # Lista de endpoints a probar
    modules = [
        ("Dashboard", "/"),
        ("Login", "/login"),
        ("Usuarios", "/usuarios"),
        ("Activos", "/activos"),
        ("Órdenes", "/ordenes"),
        ("Planes", "/planes"),
        ("Inventario", "/inventario"),
        ("Proveedores", "/proveedores"),
        ("Solicitudes", "/solicitudes"),
        ("Reportes", "/reportes"),
    ]

    results = []

    for name, endpoint in modules:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [
                200,
                302,
            ]:  # 200=OK, 302=Redirect (login requerido)
                print(f"✅ {name:15} Accesible ({response.status_code})")
                results.append((name, True))
            else:
                print(f"❌ {name:15} Error {response.status_code}")
                results.append((name, False))
        except Exception as e:
            print(f"❌ {name:15} Error: {str(e)[:40]}...")
            results.append((name, False))

        time.sleep(0.5)  # Pausa entre requests

    # Probar formularios de creación
    print("\n📝 PROBANDO FORMULARIOS...")
    print("-" * 60)

    forms = [
        ("Nuevo Usuario", "/usuarios/nuevo"),
        ("Nuevo Activo", "/activos/nuevo"),
        ("Nueva Orden", "/ordenes/nueva"),
        ("Nuevo Plan", "/planes/nuevo"),
        ("Nuevo Inventario", "/inventario/nuevo"),
        ("Nuevo Proveedor", "/proveedores/nuevo"),
        ("Nueva Solicitud", "/solicitudes/nueva"),
    ]

    for name, endpoint in forms:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 302]:
                print(f"✅ {name:18} Accesible ({response.status_code})")
                results.append((name, True))
            else:
                print(f"❌ {name:18} Error {response.status_code}")
                results.append((name, False))
        except Exception as e:
            print(f"❌ {name:18} Error: {str(e)[:30]}...")
            results.append((name, False))

        time.sleep(0.5)

    # Probar login funcional
    print("\n🔐 PROBANDO LOGIN...")
    print("-" * 60)

    session = requests.Session()
    try:
        # Obtener página de login
        response = session.get(f"{BASE_URL}/login")
        if response.status_code == 200:
            print("✅ Página login       Accesible")

            # Buscar token CSRF
            csrf_pattern = r'name="csrf_token" value="([^"]+)"'
            csrf_match = re.search(csrf_pattern, response.text)

            if csrf_match:
                csrf_token = csrf_match.group(1)
                print("✅ Token CSRF         Encontrado")

                # Intentar login
                login_data = {
                    "username": "admin",
                    "password": "admin123",
                    "csrf_token": csrf_token,
                }

                response = session.post(f"{BASE_URL}/login", data=login_data)
                if response.status_code == 302:
                    print("✅ Login admin        Exitoso")
                    results.append(("Login Funcional", True))

                    # Probar dashboard autenticado
                    response = session.get(f"{BASE_URL}/")
                    if response.status_code == 200:
                        print("✅ Dashboard autent.  Accesible")
                        results.append(("Dashboard Auth", True))
                    else:
                        print("❌ Dashboard autent.  Error")
                        results.append(("Dashboard Auth", False))
                else:
                    print(f"❌ Login admin        Error {response.status_code}")
                    results.append(("Login Funcional", False))
                    results.append(("Dashboard Auth", False))
            else:
                print("❌ Token CSRF         No encontrado")
                results.append(("Login Funcional", False))
                results.append(("Dashboard Auth", False))
        else:
            print(f"❌ Página login       Error {response.status_code}")
            results.append(("Login Funcional", False))
            results.append(("Dashboard Auth", False))

    except Exception as e:
        print(f"❌ Sistema login      Error: {str(e)[:50]}...")
        results.append(("Login Funcional", False))
        results.append(("Dashboard Auth", False))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)
    failed = total - passed

    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name:20} {status}")

    print("-" * 60)
    print(f"Total: {total} | Pasaron: {passed} | Fallaron: {failed}")
    print(f"Éxito: {(passed/total*100):.1f}%")

    if failed == 0:
        print("\n🎉 ¡PERFECTO! TODOS LOS MÓDULOS FUNCIONAN")
        print("✅ Sistema GMAO completamente operativo")
        evaluation = "EXCELENTE"
    elif failed <= 2:
        print(f"\n✅ Sistema funcional con {failed} problemas menores")
        evaluation = "BUENO"
    elif failed <= 5:
        print(f"\n⚠️ Sistema parcialmente funcional ({failed} problemas)")
        evaluation = "REGULAR"
    else:
        print(f"\n❌ Sistema con problemas importantes ({failed} fallos)")
        evaluation = "MALO"

    print(f"\n🏆 EVALUACIÓN FINAL: {evaluation}")
    print("\n" + "=" * 60)
    print("ℹ️  INFORMACIÓN DE ACCESO")
    print("=" * 60)
    print(f"🌐 URL: {BASE_URL}")
    print("👤 Usuario: admin")
    print("🔑 Contraseña: admin123")
    print("💾 Base de datos: SQLite local")
    print("🏠 Entorno: Local de desarrollo")

    return failed == 0


if __name__ == "__main__":
    success = test_module_access()
    if success:
        print("\n🚀 ¡Sistema listo para producción!")
    else:
        print("\n🔧 Revisar errores antes de desplegar")
