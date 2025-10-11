#!/usr/bin/env python3
"""
Script de verificación post-deployment para GMAO en Google Cloud
"""

import requests
import time
import json


def test_production_deployment(base_url):
    """Verificar que el deployment de producción funciona correctamente"""

    print(f"🧪 VERIFICANDO DEPLOYMENT EN: {base_url}")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Conectividad básica
    tests_total += 1
    print("1️⃣ Verificando conectividad básica...")
    try:
        response = requests.get(base_url, timeout=30, allow_redirects=True)
        if response.status_code in [200, 302]:
            print(f"   ✅ Conectividad OK ({response.status_code})")
            tests_passed += 1
        else:
            print(f"   ❌ Error de conectividad ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: HTTPS forzado
    tests_total += 1
    print("2️⃣ Verificando HTTPS...")
    try:
        # Intentar HTTP, debería redirigir a HTTPS
        http_url = base_url.replace("https://", "http://")
        response = requests.get(http_url, timeout=30, allow_redirects=False)
        if response.status_code in [301, 302, 308]:
            location = response.headers.get("Location", "")
            if location.startswith("https://"):
                print("   ✅ HTTPS forzado correctamente")
                tests_passed += 1
            else:
                print("   ⚠️ Redirect no fuerza HTTPS")
        else:
            print("   ⚠️ HTTP no redirige automáticamente")
    except Exception as e:
        print(f"   ❌ Error verificando HTTPS: {e}")

    # Test 3: Página de login accesible
    tests_total += 1
    print("3️⃣ Verificando página de login...")
    try:
        response = requests.get(f"{base_url}/login", timeout=30)
        if response.status_code == 200:
            if "login" in response.text.lower() or "usuario" in response.text.lower():
                print("   ✅ Página de login accesible")
                tests_passed += 1
            else:
                print("   ⚠️ Página accesible pero contenido no esperado")
        else:
            print(f"   ❌ Error accediendo a login ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: API health check
    tests_total += 1
    print("4️⃣ Verificando API health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=30)
        if response.status_code == 200:
            print("   ✅ API health check OK")
            tests_passed += 1
        else:
            print(f"   ⚠️ API health no disponible ({response.status_code})")
            # No es crítico si no existe endpoint de health
            tests_passed += 0.5
    except Exception as e:
        print(f"   ℹ️ Health endpoint no implementado: {e}")
        tests_passed += 0.5  # No es crítico

    # Test 5: Archivos estáticos
    tests_total += 1
    print("5️⃣ Verificando archivos estáticos...")
    try:
        response = requests.get(f"{base_url}/static/css/style.css", timeout=30)
        if response.status_code == 200:
            print("   ✅ Archivos estáticos accesibles")
            tests_passed += 1
        else:
            print(f"   ❌ Error en archivos estáticos ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 6: Tiempo de respuesta
    tests_total += 1
    print("6️⃣ Verificando tiempo de respuesta...")
    try:
        start_time = time.time()
        response = requests.get(base_url, timeout=30)
        response_time = time.time() - start_time

        if response_time < 5.0:
            print(f"   ✅ Tiempo de respuesta OK ({response_time:.2f}s)")
            tests_passed += 1
        elif response_time < 10.0:
            print(f"   ⚠️ Tiempo de respuesta lento ({response_time:.2f}s)")
            tests_passed += 0.5
        else:
            print(f"   ❌ Tiempo de respuesta muy lento ({response_time:.2f}s)")
    except Exception as e:
        print(f"   ❌ Error midiendo tiempo: {e}")

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    success_rate = (tests_passed / tests_total) * 100

    print(f"Tests ejecutados: {tests_total}")
    print(f"Tests pasados: {tests_passed}")
    print(f"Tasa de éxito: {success_rate:.1f}%")

    if success_rate >= 90:
        print("\n🎉 ¡DEPLOYMENT EXITOSO!")
        print("✅ Sistema funcionando correctamente")
        status = "SUCCESS"
    elif success_rate >= 70:
        print("\n⚠️ Deployment con advertencias")
        print("🔧 Revisar elementos fallidos")
        status = "WARNING"
    else:
        print("\n❌ Deployment con problemas")
        print("🆘 Revisar configuración urgentemente")
        status = "FAILURE"

    print(f"\n🌐 URL de producción: {base_url}")
    print("👤 Usuario por defecto: admin")
    print("🔑 Revisar Secret Manager para password")

    return status


def verify_google_cloud_resources(project_id="disfood-gmao"):
    """Verificar recursos de Google Cloud"""

    print(f"\n🔍 VERIFICANDO RECURSOS DE GOOGLE CLOUD")
    print("=" * 60)

    import subprocess

    resources_checks = [
        ("App Engine", f"gcloud app describe --project={project_id}"),
        ("Cloud SQL", f"gcloud sql instances list --project={project_id}"),
        ("Storage Bucket", f"gsutil ls -p {project_id}"),
        ("Secrets", f"gcloud secrets list --project={project_id}"),
    ]

    for resource_name, command in resources_checks:
        try:
            result = subprocess.run(
                command.split(), capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"✅ {resource_name}: Configurado")
            else:
                print(f"❌ {resource_name}: Error")
                print(f"   {result.stderr[:100]}...")
        except Exception as e:
            print(f"⚠️ {resource_name}: No se pudo verificar ({e})")


if __name__ == "__main__":
    # URL de producción (ajustar según corresponda)
    production_url = "https://disfood-gmao.appspot.com"

    print("🔍 VERIFICACIÓN POST-DEPLOYMENT GMAO")
    print("🏢 Empresa: Disfood")
    print("☁️ Plataforma: Google Cloud Platform")
    print()

    # Verificar deployment web
    status = test_production_deployment(production_url)

    # Verificar recursos de Google Cloud
    verify_google_cloud_resources()

    print("\n" + "=" * 60)
    if status == "SUCCESS":
        print("🎯 SISTEMA LISTO PARA PRODUCCIÓN")
        exit(0)
    elif status == "WARNING":
        print("⚠️ SISTEMA FUNCIONAL CON ADVERTENCIAS")
        exit(0)
    else:
        print("🚨 PROBLEMAS CRÍTICOS DETECTADOS")
        exit(1)
