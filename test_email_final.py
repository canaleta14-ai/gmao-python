#!/usr/bin/env python3
"""
Script para crear solicitud y probar emails siguiendo redirecciones
"""

import requests
from datetime import datetime


def crear_solicitud_test_emails():
    """Crear solicitud siguiendo redirecciones para probar emails"""

    BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"

    print("🧪 PRUEBA FINAL DE EMAILS")
    print("=" * 40)
    print(f"🌐 URL: {BASE_URL}")
    print(f"📧 Email destino: j_hidalgo@gmail.com")
    print(f"🔐 Nueva contraseña: mqffpsznrqehwzdm")
    print()

    session = requests.Session()

    try:
        # 1. Obtener página de solicitudes
        print("📋 Obteniendo página de solicitudes...")
        response = session.get(f"{BASE_URL}/solicitudes/", timeout=30)

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return

        # 2. Extraer token CSRF
        content = response.text
        csrf_start = content.find('name="csrf_token" value="')
        if csrf_start == -1:
            print("❌ Token CSRF no encontrado")
            return

        csrf_start += len('name="csrf_token" value="')
        csrf_end = content.find('"', csrf_start)
        csrf_token = content[csrf_start:csrf_end]

        print(f"🔐 Token CSRF: {csrf_token[:15]}...")

        # 3. Preparar datos de solicitud
        solicitud_data = {
            "csrf_token": csrf_token,
            "tipo": "MANTENIMIENTO",
            "prioridad": "ALTA",
            "descripcion": f'🧪 PRUEBA EMAIL FINAL - {datetime.now().strftime("%H:%M:%S")} - Verificación de notificaciones con nueva contraseña Gmail',
            "ubicacion": "Test - Oficina Principal",
            "solicitante": "Sistema Test Email Final",
            "email_solicitante": "prueba.final@test.com",
            "telefono_solicitante": "999888777",
        }

        # 4. Enviar solicitud (siguiendo redirecciones)
        print("📤 Enviando solicitud...")
        response = session.post(
            f"{BASE_URL}/solicitudes/",
            data=solicitud_data,
            timeout=30,
            allow_redirects=True,  # Seguir redirecciones automáticamente
        )

        print(f"📝 Respuesta final: {response.status_code}")
        print(f"📍 URL final: {response.url}")

        if response.status_code == 200:
            # Buscar código de solicitud en la respuesta
            if "SOL-" in response.text:
                import re

                matches = re.findall(r"SOL-\d{4}-\d{4}", response.text)
                if matches:
                    codigo = matches[0]
                    print(f"✅ Solicitud creada: {codigo}")
                else:
                    print("✅ Solicitud creada (código no detectado)")
            else:
                print("✅ Solicitud procesada")

            print()
            print("📧 VERIFICAR AHORA:")
            print("1. Email en j_hidalgo@gmail.com")
            print("2. Bandeja de entrada y spam")
            print("3. Buscar emails del sistema GMAO")
            print()
            print("📋 Logs en tiempo real:")
            print("   gcloud app logs tail -s default")

        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📋 Contenido: {response.text[:300]}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    crear_solicitud_test_emails()
