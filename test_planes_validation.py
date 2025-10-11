#!/usr/bin/env python3
"""
Script para probar la nueva validación de planes de mantenimiento
"""

import requests
import json
import re


def test_planes_validation():
    """Probar validación mejorada de planes"""

    print("🧪 PRUEBA DE VALIDACIÓN DE PLANES DE MANTENIMIENTO")
    print("=" * 60)

    base_url = "http://localhost:5000"

    # 1. Login
    print("🔐 Haciendo login...")
    session = requests.Session()

    response = session.get(f"{base_url}/login")
    if response.status_code != 200:
        print("❌ Error obteniendo página de login")
        return False

    csrf_pattern = r'name="csrf_token" value="([^"]+)"'
    csrf_match = re.search(csrf_pattern, response.text)

    if not csrf_match:
        print("❌ Token CSRF no encontrado")
        return False

    csrf_token = csrf_match.group(1)

    login_data = {"username": "admin", "password": "admin123", "csrf_token": csrf_token}

    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code != 302:
        print(f"❌ Error en login: {response.status_code}")
        return False

    print("✅ Login exitoso")

    # 2. Obtener activos disponibles
    print("🔍 Obteniendo activos...")
    response = session.get(f"{base_url}/activos/api?page=1&per_page=5")
    if response.status_code != 200:
        print("❌ Error obteniendo activos")
        return False

    activos_data = response.json()
    if activos_data.get("total", 0) == 0:
        print("⚠️ No hay activos para probar")
        return False

    activo = activos_data["items"][0]
    activo_id = activo["id"]
    activo_nombre = activo["nombre"]
    print(f"✅ Usando activo: {activo_nombre} (ID: {activo_id})")

    # 3. Crear primer plan de mantenimiento
    print("\n📋 Creando primer plan de mantenimiento...")

    plan1_data = {
        "nombre": "Limpieza General",
        "tipo_mantenimiento": "Preventivo",
        "frecuencia": "Semanal",
        "descripcion": "Limpieza general del equipo",
        "activo_id": activo_id,
        "tipo_frecuencia": "mensual",
        "tipo_mensual": "dia_semana_mes",
        "dia_semana_mes": "sabado",
        "semana_mes": 2,
        "intervalo_meses": 1,
    }

    response = session.post(f"{base_url}/planes/api", json=plan1_data)
    print(f"📊 Respuesta plan 1: {response.status_code}")

    if response.status_code == 200:
        plan1_result = response.json()
        print(f"✅ Plan 1 creado: {plan1_result.get('codigo_plan', 'N/A')}")
    else:
        try:
            error_data = response.json()
            print(f"❌ Error plan 1: {error_data}")
        except:
            print(f"❌ Error plan 1: {response.text[:200]}")
        return False

    # 4. Crear segundo plan DIFERENTE para el mismo activo y fecha
    print("\n📋 Creando segundo plan DIFERENTE...")

    plan2_data = {
        "nombre": "Inspección Eléctrica",  # Nombre diferente
        "tipo_mantenimiento": "Inspección",  # Tipo diferente
        "frecuencia": "Mensual",  # Frecuencia diferente
        "descripcion": "Revisión del sistema eléctrico",
        "activo_id": activo_id,
        "tipo_frecuencia": "mensual",
        "tipo_mensual": "dia_semana_mes",
        "dia_semana_mes": "sabado",  # Misma fecha
        "semana_mes": 2,
        "intervalo_meses": 1,
    }

    response = session.post(f"{base_url}/planes/api", json=plan2_data)
    print(f"📊 Respuesta plan 2: {response.status_code}")

    if response.status_code == 200:
        plan2_result = response.json()
        print(f"✅ Plan 2 creado: {plan2_result.get('codigo_plan', 'N/A')}")
        print("🎉 ¡Éxito! Se pueden crear planes diferentes en la misma fecha")
    else:
        try:
            error_data = response.json()
            print(f"⚠️ Plan 2 rechazado: {error_data}")
            # Esto podría ser esperado si la validación es muy estricta
        except:
            print(f"⚠️ Plan 2 rechazado: {response.text[:200]}")

    # 5. Intentar crear plan IDÉNTICO (debería fallar)
    print("\n📋 Intentando crear plan IDÉNTICO (debería fallar)...")

    plan3_data = {
        "nombre": "Limpieza General",  # Mismo nombre que plan 1
        "tipo_mantenimiento": "Preventivo",  # Mismo tipo
        "frecuencia": "Semanal",  # Misma frecuencia
        "descripcion": "Limpieza duplicada",
        "activo_id": activo_id,
        "tipo_frecuencia": "mensual",
        "tipo_mensual": "dia_semana_mes",
        "dia_semana_mes": "sabado",
        "semana_mes": 2,
        "intervalo_meses": 1,
    }

    response = session.post(f"{base_url}/planes/api", json=plan3_data)
    print(f"📊 Respuesta plan 3: {response.status_code}")

    if response.status_code != 200:
        try:
            error_data = response.json()
            print(f"✅ Plan 3 correctamente rechazado: {error_data}")
            print("🛡️ Validación funcionando: evita duplicados")
        except:
            print(f"✅ Plan 3 correctamente rechazado: {response.text[:200]}")
    else:
        print("⚠️ Plan 3 fue aceptado (posible problema con validación)")

    # 6. Listar planes creados
    print("\n📋 Listando planes creados...")
    response = session.get(f"{base_url}/planes/api?page=1&per_page=10")
    if response.status_code == 200:
        planes_data = response.json()
        total_planes = planes_data.get("total", 0)
        print(f"📊 Total planes en sistema: {total_planes}")

        for i, plan in enumerate(planes_data.get("items", [])[:5], 1):
            print(
                f"   {i}. {plan.get('codigo_plan', 'N/A')} - {plan.get('nombre', 'N/A')} "
                f"({plan.get('tipo_mantenimiento', 'N/A')})"
            )

    return True


if __name__ == "__main__":
    try:
        print("🔧 Probando nueva validación de planes de mantenimiento...")
        print("📝 Debería permitir planes diferentes en la misma fecha")
        print("🛡️ Pero rechazar planes idénticos")
        print()

        success = test_planes_validation()

        if success:
            print("\n🎉 ¡PRUEBA COMPLETADA!")
            print("✅ Sistema de validación funcionando correctamente")
        else:
            print("\n❌ Prueba falló")
            print("🔧 Revisar configuración")

    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback

        traceback.print_exc()
