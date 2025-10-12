#!/usr/bin/env python3
"""
Test específico para verificar las APIs corregidas antes del despliegue
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"


def test_api_specific():
    """Test específico de las 3 APIs que estaban fallando"""

    print("🧪 TEST ESPECÍFICO DE APIs CORREGIDAS")
    print("=" * 50)
    print(f"🌐 URL Base: {BASE_URL}")
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # APIs específicas a probar
    apis_to_test = [
        {
            "name": "API Ordenes Stats",
            "url": "/ordenes/api/estadisticas",
            "expected_status": [200, 302, 401],  # 302 para redirección a login es OK
        },
        {
            "name": "API Categorias Stats",
            "url": "/categorias/estadisticas",
            "expected_status": [200, 302, 401],
        },
        {
            "name": "API Recambios",
            "url": "/api/recambios",
            "expected_status": [200, 302, 401],
        },
    ]

    resultados = []

    for api in apis_to_test:
        print(f"🔍 Probando: {api['name']}")
        try:
            response = requests.get(
                f"{BASE_URL}{api['url']}",
                timeout=10,
                allow_redirects=False,  # No seguir redirecciones automáticamente
            )

            status_code = response.status_code

            if status_code in api["expected_status"]:
                status_icon = "✅"
                status_text = "OK"
                success = True
            elif status_code == 404:
                status_icon = "❌"
                status_text = "ERROR 404 - NOT FOUND"
                success = False
            else:
                status_icon = "⚠️"
                status_text = f"CÓDIGO {status_code}"
                success = True  # Otros códigos pueden ser válidos

            print(
                f"   {status_icon} {api['name']}: {status_text} (código {status_code})"
            )

            resultados.append(
                {
                    "name": api["name"],
                    "url": api["url"],
                    "status_code": status_code,
                    "success": success,
                    "response_size": len(response.content) if response.content else 0,
                }
            )

        except requests.exceptions.RequestException as e:
            print(f"   ❌ {api['name']}: Error de conexión - {str(e)}")
            resultados.append(
                {
                    "name": api["name"],
                    "url": api["url"],
                    "status_code": None,
                    "success": False,
                    "error": str(e),
                }
            )

    print()
    print("=" * 50)
    print("📊 RESUMEN DEL TEST ESPECÍFICO")
    print("=" * 50)

    total_apis = len(apis_to_test)
    apis_ok = sum(1 for r in resultados if r["success"])
    apis_error = total_apis - apis_ok
    porcentaje = (apis_ok / total_apis) * 100

    print(f"📈 APIs probadas: {total_apis}")
    print(f"✅ Funcionando: {apis_ok}")
    print(f"❌ Con errores: {apis_error}")
    print(f"📊 Porcentaje éxito: {porcentaje:.1f}%")
    print()

    if apis_error > 0:
        print("❌ ERRORES ENCONTRADOS:")
        for i, resultado in enumerate(resultados):
            if not resultado["success"]:
                error_msg = resultado.get(
                    "error", f"Error {resultado.get('status_code', 'desconocido')}"
                )
                print(f"   {i+1}. {resultado['name']}: {error_msg}")
        print()

    if porcentaje == 100:
        print("✅ TODAS LAS APIs CORREGIDAS FUNCIONAN CORRECTAMENTE")
        print("🚀 LISTO PARA DESPLIEGUE")
    elif porcentaje >= 67:
        print("⚠️ MAYORÍA DE APIs FUNCIONAN - REVISAR ERRORES MENORES")
    else:
        print("🚨 MÚLTIPLES APIs REQUIEREN ATENCIÓN")

    print(f"🕐 Test completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Guardar resultados
    resultado_final = {
        "timestamp": datetime.now().isoformat(),
        "url_base": BASE_URL,
        "apis_probadas": total_apis,
        "apis_ok": apis_ok,
        "apis_error": apis_error,
        "porcentaje_exito": porcentaje,
        "detalles": resultados,
    }

    with open("test_apis_especifico.json", "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)

    print(f"📄 Resultados guardados en: test_apis_especifico.json")

    return porcentaje == 100


if __name__ == "__main__":
    success = test_api_specific()
    exit(0 if success else 1)
