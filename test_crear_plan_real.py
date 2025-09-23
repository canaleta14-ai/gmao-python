#!/usr/bin/env python3
"""
Script para simular la creación real de un plan como lo hace el navegador
"""

import requests
import json


def test_crear_plan_real():
    url = "http://127.0.0.1:5000/planes/api"

    # Datos exactos como los enviaría el formulario del navegador
    data = {
        "nombre": "Test Miercoles Real",
        "descripcion": "Plan de prueba para miércoles",
        "activo_id": 1,
        "frecuencia": "Semanal",
        "tipo_frecuencia": "semanal",
        "intervalo_semanas": 1,
        "dias_semana": ["miercoles"],
    }

    headers = {"Content-Type": "application/json"}

    print("=== CREAR PLAN REAL VIA API ===")
    print(f"URL: {url}")
    print(f"Datos enviados: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            print(f"Plan creado exitosamente:")
            print(f"- ID: {response_data.get('id')}")
            print(f"- Código: {response_data.get('codigo_plan')}")
            if "proxima_ejecucion" in response_data:
                print(f"- Próxima ejecución: {response_data['proxima_ejecucion']}")
        else:
            print(f"Error en la creación del plan: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_crear_plan_real()
