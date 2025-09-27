#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la codificación UTF-8 en las respuestas de la API
"""

import requests
import json


def test_planes_encoding():
    """Probar que las respuestas de la API usen codificación UTF-8 correcta"""

    print("🔍 Probando codificación de mensajes en API de planes...")

    # URL base
    base_url = "http://localhost:5000"

    # Probar crear un plan para ver el mensaje de respuesta
    plan_data = {
        "nombre": "Plan de Prueba",
        "descripcion": "Descripción con acentos: áéíóú ñ",
        "activo_id": 1,
        "tiempo_estimado": 1.5,
        "tipo_frecuencia": "semanal",
        "intervalo_semanas": "1",
        "dias_semana": ["lunes"],
        "frecuencia": "Semanal",
    }

    try:
        # Hacer una sesión para manejar cookies
        session = requests.Session()

        # Intentar hacer login primero (si es necesario)
        login_data = {"username": "admin", "password": "admin123"}
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"Login status: {login_response.status_code}")

        # Probar crear plan
        print("\n📝 Creando plan de prueba...")
        response = session.post(
            f"{base_url}/planes/api",
            json=plan_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"Status Code: {response.status_code}")
        print(
            f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}"
        )
        print(f"Encoding: {response.encoding}")

        if response.status_code == 200:
            # Probar decodificar como UTF-8
            response_text = response.text
            print(f"\nRespuesta raw: {response_text}")

            try:
                data = response.json()
                print(f"\nRespuesta JSON parseada:")
                print(f"  success: {data.get('success')}")
                print(f"  message: {data.get('message')}")

                # Verificar que el mensaje se vea correctamente
                message = data.get("message", "")
                print(f"\nAnálisis del mensaje:")
                print(f"  Longitud: {len(message)}")
                print(f"  Contiene 'éxito': {'éxito' in message}")
                print(
                    f"  Contiene caracteres problemáticos: {any(c in message for c in ['√', '‚', '∫'])}"
                )

                # Mostrar caracteres individuales si hay problemas
                if any(c in message for c in ["√", "‚", "∫"]):
                    print(f"  Caracteres problemáticos encontrados:")
                    for i, char in enumerate(message):
                        if ord(char) > 127:  # No ASCII
                            print(
                                f"    Posición {i}: '{char}' (Unicode: {ord(char)}, hex: {hex(ord(char))})"
                            )

            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta cruda: {response_text}")

        else:
            print(f"❌ Error en request: {response.status_code}")
            print(f"Respuesta: {response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:5000?"
        )
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_planes_encoding()
