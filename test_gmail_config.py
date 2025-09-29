#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Gmail
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def test_gmail_config():
    """Prueba la configuración de Gmail"""
    try:
        # Configuración desde variables de entorno
        mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        mail_port = int(os.getenv("MAIL_PORT", "587"))
        mail_use_tls = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
        mail_username = os.getenv("MAIL_USERNAME")
        mail_password = os.getenv("MAIL_PASSWORD")

        print("=== Configuración de Email ===")
        print(f"Servidor: {mail_server}")
        print(f"Puerto: {mail_port}")
        print(f"TLS: {mail_use_tls}")
        print(f"Usuario: {mail_username}")
        print(
            f"Contraseña: {'*' * len(mail_password) if mail_password else 'No configurada'}"
        )

        if not all([mail_username, mail_password]):
            print("❌ ERROR: Configuración incompleta")
            return False

        print("\n=== Probando conexión SMTP ===")

        # Crear mensaje de prueba
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Prueba de configuración GMAO"
        msg["From"] = mail_username
        msg["To"] = mail_username  # Enviar a sí mismo

        contenido_html = """
        <html>
        <body>
            <h1>Prueba de Configuración</h1>
            <p>Esta es una prueba automática del sistema GMAO.</p>
            <p>Si recibe este email, la configuración está funcionando correctamente.</p>
        </body>
        </html>
        """

        # Extraer texto plano
        import re

        contenido_texto = re.sub(r"<[^>]+>", "", contenido_html)
        contenido_texto = re.sub(r"\s+", " ", contenido_texto).strip()

        # Adjuntar partes
        part1 = MIMEText(contenido_texto, "plain", "utf-8")
        part2 = MIMEText(contenido_html, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        # Conectar al servidor
        print(f"Conectando a {mail_server}:{mail_port}...")
        server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        server.ehlo()

        if mail_use_tls:
            print("Iniciando conexión TLS...")
            server.starttls()
            server.ehlo()

        # Autenticar
        print(f"Autenticando como {mail_username}...")
        server.login(mail_username, mail_password)

        # Enviar email
        print(f"Enviando email de prueba a {mail_username}...")
        server.sendmail(mail_username, mail_username, msg.as_string())

        # Cerrar conexión
        server.quit()

        print("✅ Email enviado exitosamente")
        print("Si no recibe el email, verifique:")
        print("1. Que la contraseña de aplicación sea correcta (si tiene 2FA)")
        print("2. Que Gmail no esté bloqueando la aplicación")
        print("3. Que la dirección de email sea correcta")

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ ERROR de autenticación: {e}")
        print("Posibles causas:")
        print("- Contraseña incorrecta")
        print("- Necesita contraseña de aplicación (si tiene 2FA)")
        print("- Gmail está bloqueando la aplicación")
    except smtplib.SMTPConnectError as e:
        print(f"❌ ERROR de conexión: {e}")
        print("Verifique la conexión a internet y la configuración del servidor")
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        print("Verifique la configuración completa")

    return False


if __name__ == "__main__":
    # Cargar variables de entorno desde .env
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("Variables de entorno cargadas desde .env")
    except ImportError:
        print("python-dotenv no instalado, usando variables de entorno del sistema")

    success = test_gmail_config()
    sys.exit(0 if success else 1)
