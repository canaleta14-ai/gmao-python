#!/usr/bin/env python3
"""
Script para probar directamente las funciones de email
"""

import requests
import json
import logging

# URL base de la aplicación en producción
BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"


def crear_solicitud_con_logs():
    """Crear una solicitud y verificar logs de email"""

    print("🧪 Creando solicitud para probar emails...")
    print(f"🌐 URL: {BASE_URL}")

    # Obtener página de solicitudes para el token CSRF
    session = requests.Session()

    try:
        # Paso 1: Obtener página
        print("📋 Obteniendo página de solicitudes...")
        response = session.get(f"{BASE_URL}/solicitudes")

        if response.status_code != 200:
            print(f"❌ Error obteniendo página: {response.status_code}")
            return

        # Paso 2: Extraer token CSRF (método simple)
        content = response.text
        csrf_start = content.find('name="csrf_token" value="')
        if csrf_start == -1:
            print("❌ No se encontró token CSRF")
            return

        csrf_start += len('name="csrf_token" value="')
        csrf_end = content.find('"', csrf_start)
        csrf_token = content[csrf_start:csrf_end]

        print(f"🔐 Token CSRF obtenido: {csrf_token[:20]}...")

        # Paso 3: Crear solicitud
        solicitud_data = {
            "csrf_token": csrf_token,
            "tipo": "MANTENIMIENTO",
            "prioridad": "ALTA",
            "descripcion": "🧪 PRUEBA DE EMAIL - Solicitud creada para verificar notificaciones por email",
            "ubicacion": "Oficina Principal - Test Email",
            "solicitante": "Sistema Prueba Email",
            "email_solicitante": "testprueba@ejemplo.com",
            "telefono_solicitante": "987654321",
        }

        print("📤 Enviando solicitud...")
        response = session.post(
            f"{BASE_URL}/solicitudes",
            data=solicitud_data,
            timeout=30,
            allow_redirects=False,
        )

        print(f"📝 Respuesta: {response.status_code}")

        if response.status_code in [200, 302]:
            print("✅ Solicitud creada exitosamente")

            # Extraer número de solicitud si está en la respuesta
            if "location" in response.headers:
                location = response.headers["location"]
                print(f"📍 Redirección: {location}")

                # Obtener la página de confirmación
                if "/confirmacion/" in location:
                    conf_response = session.get(f"{BASE_URL}{location}")
                    if conf_response.status_code == 200:
                        content = conf_response.text
                        if "SOL-" in content:
                            # Buscar el código de solicitud
                            import re

                            match = re.search(r"SOL-\d{4}-\d{4}", content)
                            if match:
                                codigo = match.group(0)
                                print(f"🆔 Código de solicitud: {codigo}")

            print()
            print("📧 VERIFICAR AHORA:")
            print("1. Email j_hidalgo@gmail.com")
            print("2. Logs de aplicación:")
            print("   gcloud app logs tail -s default")
            print()
            print("📋 Si no llegan emails, revisar:")
            print("- Configuración MAIL_USERNAME/MAIL_PASSWORD")
            print("- Logs de errores SMTP")
            print("- Configuración de Gmail (app passwords)")

        else:
            print(f"❌ Error creando solicitud: {response.status_code}")
            print(f"📋 Respuesta: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Error: {e}")


def verificar_logs_email():
    """Comando para verificar logs de email"""
    print("\n🔍 Para verificar logs de email en tiempo real:")
    print("gcloud app logs tail -s default")
    print()
    print("🔍 Para buscar errores específicos:")
    print('gcloud app logs read --limit=100 | findstr /i "email mail smtp error"')


if __name__ == "__main__":
    crear_solicitud_con_logs()
    verificar_logs_email()
