#!/usr/bin/env python3
"""
Verificación rápida de configuración de email
"""
import os
import sys


def check_email_config():
    """Verifica la configuración de email"""
    print("=== Verificación de Configuración de Email ===\n")

    # Verificar variables de entorno
    mail_server = os.getenv("MAIL_SERVER")
    mail_port = os.getenv("MAIL_PORT")
    mail_use_tls = os.getenv("MAIL_USE_TLS")
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    server_url = os.getenv("SERVER_URL")
    admin_emails = os.getenv("ADMIN_EMAILS")

    checks = [
        ("MAIL_SERVER", mail_server),
        ("MAIL_PORT", mail_port),
        ("MAIL_USE_TLS", mail_use_tls),
        ("MAIL_USERNAME", mail_username),
        ("MAIL_PASSWORD", mail_password),
        ("SERVER_URL", server_url),
        ("ADMIN_EMAILS", admin_emails),
    ]

    all_good = True
    for name, value in checks:
        if name == "MAIL_PASSWORD":
            status = "✅" if value else "❌"
            display_value = "*" * len(value) if value else "NO CONFIGURADO"
        else:
            status = "✅" if value else "❌"
            display_value = value or "NO CONFIGURADO"

        print(f"{status} {name}: {display_value}")
        if not value:
            all_good = False

    print("\n=== Instrucciones para Gmail ===")
    print("1. Si tienes 2FA habilitado, usa una CONTRASEÑA DE APLICACIÓN")
    print("2. Crea una en: https://myaccount.google.com/apppasswords")
    print("3. Para Google Workspace, usa tu contraseña normal")
    print("4. Ejecuta: python test_gmail_config.py para probar")

    return all_good


if __name__ == "__main__":
    # Cargar .env si existe
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    success = check_email_config()
    if not success:
        print("\n❌ Configuración incompleta. Revisa el archivo .env")
        sys.exit(1)
    else:
        print("\n✅ Configuración básica completa")
        print("Ejecuta 'python test_gmail_config.py' para probar el envío")
