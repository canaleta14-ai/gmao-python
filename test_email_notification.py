#!/usr/bin/env python3
"""
Script para probar las notificaciones por email del sistema de solicitudes
"""

import requests
import json
from datetime import datetime

# URL base de la aplicación en producción
BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"


def test_email_notification():
    """Crear una solicitud para probar las notificaciones por email"""

    # Datos de la solicitud de prueba
    solicitud_data = {
        "tipo": "MANTENIMIENTO",
        "prioridad": "MEDIA",
        "descripcion": "Prueba de notificación por email - "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ubicacion": "Oficina Principal",
        "solicitante": "Sistema de Prueba",
        "email_solicitante": "test@ejemplo.com",
        "telefono_solicitante": "123456789",
    }

    try:
        print(
            "🧪 Creando solicitud de prueba para verificar notificaciones por email..."
        )
        print(f"📧 Email configurado: j_hidalgo@gmail.com")
        print(f"🌐 URL: {BASE_URL}")

        # Realizar petición POST para crear la solicitud
        response = requests.post(
            f"{BASE_URL}/solicitudes", data=solicitud_data, timeout=30
        )

        print(f"📝 Código de respuesta: {response.status_code}")

        if response.status_code == 200 or response.status_code == 201:
            print("✅ Solicitud creada exitosamente")
            print("📧 Verificar email en j_hidalgo@gmail.com")
            print("📋 Si no llega el email, revisar logs de la aplicación")
        else:
            print(f"❌ Error al crear solicitud: {response.status_code}")
            print(f"📋 Respuesta: {response.text[:200]}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_email_notification()
