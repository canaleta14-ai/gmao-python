#!/usr/bin/env python3
"""
Script para probar las notificaciones por email del sistema de solicitudes
mediante la interfaz web con CSRF token
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# URL base de la aplicación en producción
BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"


def test_email_notification_web():
    """Crear una solicitud mediante la interfaz web para probar las notificaciones por email"""

    session = requests.Session()

    try:
        print("🧪 Probando notificaciones por email mediante interfaz web...")
        print(f"📧 Email configurado: j_hidalgo@gmail.com")
        print(f"🌐 URL: {BASE_URL}")

        # 1. Obtener la página de solicitudes para obtener el CSRF token
        print("📋 Obteniendo página de solicitudes...")
        response = session.get(f"{BASE_URL}/solicitudes")

        if response.status_code != 200:
            print(f"❌ Error al acceder a solicitudes: {response.status_code}")
            return

        # 2. Extraer CSRF token de la página
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = None

        # Buscar el token CSRF en los campos hidden
        csrf_input = soup.find("input", {"name": "csrf_token"})
        if csrf_input:
            csrf_token = csrf_input.get("value")

        # También buscar en meta tags
        if not csrf_token:
            csrf_meta = soup.find("meta", {"name": "csrf-token"})
            if csrf_meta:
                csrf_token = csrf_meta.get("content")

        if not csrf_token:
            print("❌ No se pudo obtener el CSRF token")
            return

        print(f"🔐 CSRF token obtenido: {csrf_token[:10]}...")

        # 3. Datos de la solicitud de prueba
        solicitud_data = {
            "csrf_token": csrf_token,
            "tipo": "MANTENIMIENTO",
            "prioridad": "MEDIA",
            "descripcion": f'🧪 Prueba de notificación por email - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            "ubicacion": "Oficina Principal - Prueba",
            "solicitante": "Sistema de Prueba Email",
            "email_solicitante": "test.email@ejemplo.com",
            "telefono_solicitante": "123456789",
        }

        # 4. Enviar solicitud con CSRF token
        print("📤 Enviando solicitud con CSRF token...")
        response = session.post(
            f"{BASE_URL}/solicitudes",
            data=solicitud_data,
            timeout=30,
            allow_redirects=True,
        )

        print(f"📝 Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            if (
                "solicitud creada" in response.text.lower()
                or "éxito" in response.text.lower()
            ):
                print("✅ Solicitud creada exitosamente")
                print("📧 Verificar email en j_hidalgo@gmail.com")
                print("📋 Deberíais recibir:")
                print("   - Email de confirmación")
                print("   - Email de notificación al administrador")
            else:
                print("⚠️  Respuesta 200 pero contenido incierto")
                print(f"📋 Fragmento de respuesta: {response.text[:300]}")
        else:
            print(f"❌ Error al crear solicitud: {response.status_code}")
            if "csrf" in response.text.lower():
                print("🔐 Error relacionado con CSRF token")
            print(f"📋 Respuesta: {response.text[:500]}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def check_email_logs():
    """Verificar los logs de email de la aplicación"""
    print("\n📧 Para verificar si los emails se están enviando:")
    print("   gcloud app logs tail -s default | grep -i email")
    print("   gcloud app logs tail -s default | grep -i mail")
    print("   gcloud app logs tail -s default | grep -i smtp")


if __name__ == "__main__":
    test_email_notification_web()
    check_email_logs()
