#!/usr/bin/env python3
"""
Test directo de autenticación SMTP para j_hidalgo@disfood.com
"""

import smtplib
from email.mime.text import MIMEText


def test_smtp_disfood():
    """
    Probar autenticación SMTP directa con disfood.com
    """
    print("🧪 TEST DIRECTO SMTP - DISFOOD.COM")
    print("=" * 40)

    # Configuración SMTP
    mail_server = "smtp.gmail.com"
    mail_port = 587
    mail_username = "j_hidalgo@disfood.com"
    mail_password = "mqffpsznrqehwzdm"  # Contraseña actual

    print(f"📧 Servidor: {mail_server}:{mail_port}")
    print(f"👤 Usuario: {mail_username}")
    print(f"🔐 Password: {mail_password[:8]}...")
    print()

    try:
        print("🔌 Conectando al servidor SMTP...")
        server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        server.ehlo()

        print("🔒 Iniciando TLS...")
        server.starttls()
        server.ehlo()

        print("🔑 Intentando autenticación...")
        server.login(mail_username, mail_password)

        print("✅ ¡Autenticación exitosa!")

        # Crear email de prueba
        msg = MIMEText(
            "Test directo de autenticación SMTP desde Python", "plain", "utf-8"
        )
        msg["Subject"] = "Test SMTP Directo - Disfood"
        msg["From"] = mail_username
        msg["To"] = mail_username

        print("📨 Enviando email de prueba...")
        server.send_message(msg)

        server.quit()
        print("✅ ¡Email enviado exitosamente!")
        print("📬 Revisa la bandeja de entrada de j_hidalgo@disfood.com")

    except smtplib.SMTPAuthenticationError as e:
        print("❌ ERROR DE AUTENTICACIÓN SMTP:")
        print(f"   {e}")
        print()
        print("🔧 POSIBLES SOLUCIONES:")
        print("   1. Generar nueva App Password para j_hidalgo@disfood.com")
        print("   2. Verificar que la cuenta tenga 2FA habilitado")
        print("   3. Ir a https://myaccount.google.com/apppasswords")

    except smtplib.SMTPException as e:
        print(f"❌ ERROR SMTP: {e}")

    except Exception as e:
        print(f"💥 ERROR: {e}")


if __name__ == "__main__":
    test_smtp_disfood()
