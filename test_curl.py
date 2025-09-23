#!/usr/bin/env python3
"""
Script para simular la creación real de un plan usando curl
"""

import subprocess
import json


def test_crear_plan_curl():
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

    print("=== CREAR PLAN REAL VIA CURL ===")
    print(f"URL: {url}")
    print(f"Datos enviados: {json.dumps(data, indent=2)}")

    # Convertir datos a JSON string para curl
    json_data = json.dumps(data)

    # Comando curl
    curl_cmd = [
        "curl",
        "-X",
        "POST",
        url,
        "-H",
        "Content-Type: application/json",
        "-d",
        json_data,
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        print(f"Status Code: {result.returncode}")
        print(f"Response: {result.stdout}")

        if result.stderr:
            print(f"Errors: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("❌ Error: Timeout al conectar al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_crear_plan_curl()
