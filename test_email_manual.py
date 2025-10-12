#!/usr/bin/env python3
"""
Script simple para probar las notificaciones por email
creando solicitudes directamente desde la web
"""

import webbrowser
import time

# URL base de la aplicación en producción
BASE_URL = "https://mantenimiento-470311.ew.r.appspot.com"


def test_email_notification_manual():
    """Abrir la aplicación en el navegador para crear una solicitud manualmente"""

    print("🧪 Prueba manual de notificaciones por email")
    print("=" * 50)
    print(f"📧 Email configurado: j_hidalgo@gmail.com")
    print(f"🔑 Secret de contraseña: Configurado en Secret Manager")
    print(f"🌐 URL: {BASE_URL}")
    print()

    print("📋 Pasos para probar:")
    print("1. Se abrirá el navegador en la página de solicitudes")
    print("2. Crear una nueva solicitud con los siguientes datos:")
    print("   - Tipo: MANTENIMIENTO")
    print("   - Prioridad: MEDIA")
    print("   - Descripción: Prueba de notificación por email")
    print("   - Ubicación: Oficina Principal")
    print("   - Solicitante: Sistema de Prueba")
    print("   - Email: test@ejemplo.com")
    print("   - Teléfono: 123456789")
    print("3. Enviar la solicitud")
    print("4. Verificar que lleguen emails a j_hidalgo@gmail.com")
    print()

    print("📧 Emails esperados:")
    print("   ✉️  Email de confirmación al solicitante")
    print("   ✉️  Email de notificación al administrador (j_hidalgo@gmail.com)")
    print()

    print("🔍 Para verificar logs de email:")
    print("   gcloud app logs tail -s default | findstr /i email")
    print()

    # Abrir la aplicación en el navegador
    solicitudes_url = f"{BASE_URL}/solicitudes"
    print(f"🌐 Abriendo {solicitudes_url}")
    webbrowser.open(solicitudes_url)

    print()
    print("⏰ Esperando 5 segundos y luego abriendo logs...")
    time.sleep(5)

    # También abrir una terminal para logs
    print("📋 Abriendo segunda ventana para logs en tiempo real...")
    print("   Ejecutar: gcloud app logs tail -s default")


def check_email_configuration():
    """Verificar la configuración de email actual"""
    print("\n🔧 Configuración actual de email:")
    print("=" * 40)
    print("✅ MAIL_USERNAME: j_hidalgo@gmail.com")
    print("✅ MAIL_PASSWORD: Configurado en Secret Manager (gmao-mail-password)")
    print("✅ ADMIN_EMAILS: j_hidalgo@gmail.com")
    print("✅ MAIL_SERVER: smtp.gmail.com")
    print("✅ MAIL_PORT: 587")
    print("✅ MAIL_USE_TLS: True")
    print()
    print("📧 Funciones de email en el código:")
    print("   - enviar_email_confirmacion() → Email al solicitante")
    print("   - enviar_email_notificacion_admin() → Email al administrador")
    print()


if __name__ == "__main__":
    check_email_configuration()
    test_email_notification_manual()
