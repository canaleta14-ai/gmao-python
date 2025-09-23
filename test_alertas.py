#!/usr/bin/env python3
"""
Script para probar el endpoint de alertas de mantenimiento
"""
import requests
import json

# Crear una sesión para mantener cookies
session = requests.Session()

print("🔍 Probando el endpoint de alertas de mantenimiento...")
print("=" * 60)

# Paso 1: Hacer login primero
print("\n1️⃣ Haciendo login...")
try:
    login_data = {"username": "admin", "password": "admin123"}

    response = session.post(
        "http://127.0.0.1:5000/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 200:
        print("   ✅ Login exitoso")
    else:
        print(f"   ❌ Error en login: {response.status_code}")
        exit(1)

except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Paso 2: Probar el endpoint de alertas
print("\n2️⃣ Probando /api/alertas-mantenimiento...")
try:
    response = session.get("http://127.0.0.1:5000/api/alertas-mantenimiento")
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("   ✅ Respuesta JSON válida:")
            print(f'   • Success: {data.get("success", "N/A")}')
            print(f'   • Total alertas: {data.get("total", "N/A")}')
            print(f'   • Vencidos: {data.get("vencidos", "N/A")}')
            print(f'   • Próximos: {data.get("proximos", "N/A")}')

            alertas = data.get("alertas", [])
            if alertas:
                print("\n   📋 Alertas encontradas:")
                for i, alerta in enumerate(
                    alertas[:3], 1
                ):  # Solo mostrar las primeras 3
                    print(f'   {i}. {alerta.get("titulo", "Sin título")}')
                    print(f'      - Tipo: {alerta.get("tipo", "N/A")}')
                    print(f'      - Prioridad: {alerta.get("prioridad", "N/A")}')
                    print(f'      - Activo: {alerta.get("activo", "N/A")}')
                if len(alertas) > 3:
                    print(f"   ... y {len(alertas) - 3} más")
            else:
                print("\n   ℹ️ No hay alertas de mantenimiento")

        except json.JSONDecodeError as e:
            print(f"   ❌ Error al parsear JSON: {e}")
            print(f"   Contenido: {response.text[:200]}...")
    else:
        print(f"   ❌ Error HTTP: {response.status_code}")
        print(f"   Contenido: {response.text[:200]}...")

except Exception as e:
    print(f"   ❌ Error de conexión: {e}")

# Paso 3: Verificar si hay planes de mantenimiento en la BD
print("\n3️⃣ Verificando planes de mantenimiento en la base de datos...")
try:
    # Usar el CLI de Python para verificar la BD
    import subprocess

    result = subprocess.run(
        [
            "C:/gmao - copia/.venv/Scripts/python.exe",
            "-c",
            """
from app.factory import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.activo import Activo

app = create_app()
with app.app_context():
    planes = PlanMantenimiento.query.all()
    print(f'Total planes: {len(planes)}')
    for plan in planes[:3]:
        print(f'- {plan.nombre} (Estado: {plan.estado})')
        if hasattr(plan, 'activo') and plan.activo:
            print(f'  Activo: {plan.activo.nombre}')
        if hasattr(plan, 'proxima_ejecucion') and plan.proxima_ejecucion:
            print(f'  Próxima ejecución: {plan.proxima_ejecucion}')
""",
        ],
        capture_output=True,
        text=True,
        cwd="C:/gmao - copia",
    )

    if result.returncode == 0:
        print("   ✅ Consulta a la base de datos exitosa:")
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                print(f"   {line}")
    else:
        print(f"   ❌ Error en consulta: {result.stderr}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Diagnóstico completado")
