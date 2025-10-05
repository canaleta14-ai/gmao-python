#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la configuración de email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "j_hidalgo@disfood.com"
MAIL_PASSWORD = "dvematimfpjjpxji"
DESTINATARIO = "j_hidalgo@disfood.com"


def test_email():
    """Prueba de envío de email"""
    try:
        print("=" * 70)
        print("PRUEBA DE CONFIGURACIÓN DE EMAIL - GMAIL EMPRESARIAL")
        print("=" * 70)
        print()

        print(f"📧 Servidor SMTP: {MAIL_SERVER}:{MAIL_PORT}")
        print(f"👤 Usuario: {MAIL_USERNAME}")
        print(f"📬 Destinatario: {DESTINATARIO}")
        print()

        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✅ Prueba de Email - Sistema GMAO"
        msg["From"] = MAIL_USERNAME
        msg["To"] = DESTINATARIO

        # Contenido con caracteres españoles para probar UTF-8
        contenido_html = """
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #28a745;">✅ Prueba de Email Exitosa</h2>
                <p>Este es un mensaje de prueba del <strong>Sistema GMAO</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Prueba de caracteres españoles:</h3>
                    <ul>
                        <li>Eñe: Español, Niño, Año</li>
                        <li>Tildes: Informática, José, María</li>
                        <li>Símbolos: € £ ¥ © ®</li>
                    </ul>
                </div>
                
                <p>Si recibes este email, la configuración de Gmail empresarial está funcionando correctamente.</p>
                
                <hr>
                <small style="color: #6c757d;">
                    Sistema de Gestión de Mantenimiento - GMAO<br>
                    Fecha: 2 de octubre de 2025
                </small>
            </body>
        </html>
        """

        contenido_texto = """
        ✅ Prueba de Email Exitosa
        
        Este es un mensaje de prueba del Sistema GMAO.
        
        Prueba de caracteres españoles:
        - Eñe: Español, Niño, Año
        - Tildes: Informática, José, María
        
        Si recibes este email, la configuración está funcionando correctamente.
        """

        # Adjuntar partes
        part1 = MIMEText(contenido_texto, "plain", "utf-8")
        part2 = MIMEText(contenido_html, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        # Conectar al servidor SMTP
        print("🔌 Conectando al servidor SMTP...")
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=30)
        server.set_debuglevel(0)  # Cambiar a 1 para ver debug detallado

        print("👋 Enviando EHLO...")
        server.ehlo()

        print("🔒 Iniciando TLS...")
        server.starttls()
        server.ehlo()

        print(f"🔑 Autenticando como {MAIL_USERNAME}...")
        server.login(MAIL_USERNAME, MAIL_PASSWORD)

        print(f"📤 Enviando email a {DESTINATARIO}...")
        server.send_message(msg)

        print("🔌 Cerrando conexión...")
        server.quit()

        print()
        print("=" * 70)
        print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
        print("=" * 70)
        print()
        print("📬 Revisa tu bandeja de entrada en: j_hidalgo@disfood.com")
        print("⚠️  Si no lo ves, revisa también la carpeta de SPAM")
        print()

        return True

    except smtplib.SMTPAuthenticationError as e:
        print()
        print("=" * 70)
        print("❌ ERROR DE AUTENTICACIÓN")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        print("Posibles soluciones:")
        print("1. Verifica que la verificación en dos pasos esté habilitada")
        print("2. Genera una nueva contraseña de aplicación:")
        print("   https://myaccount.google.com/apppasswords")
        print("3. Para Google Workspace, contacta al administrador del dominio")
        print("4. Verifica que el acceso de aplicaciones menos seguras esté habilitado")
        print()
        return False

    except smtplib.SMTPConnectError as e:
        print()
        print("=" * 70)
        print("❌ ERROR DE CONEXIÓN")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        print("Verifica tu conexión a internet y que el puerto 587 no esté bloqueado")
        print()
        return False

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR INESPERADO")
        print("=" * 70)
        print(f"Error: {e}")
        print(f"Tipo: {type(e).__name__}")
        print()
        return False


if __name__ == "__main__":
    test_email()
