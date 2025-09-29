#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de email
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno
os.environ["FLASK_APP"] = "run.py"
os.environ["FLASK_ENV"] = "development"

from app import create_app
from app.utils.email_utils import enviar_email


def test_email():
    """Prueba el envío de email"""
    try:
        app = create_app()

        with app.app_context():
            print("Probando configuración de email...")

            # Verificar configuración
            mail_server = os.getenv("MAIL_SERVER")
            mail_username = os.getenv("MAIL_USERNAME")
            mail_password = os.getenv("MAIL_PASSWORD")

            print(f"MAIL_SERVER: {mail_server}")
            print(f"MAIL_USERNAME: {mail_username}")
            print(
                f"MAIL_PASSWORD: {'*' * len(mail_password) if mail_password else 'No configurado'}"
            )

            if not all([mail_username, mail_password]):
                print("ERROR: Configuración de email incompleta")
                return False

            # Enviar email de prueba
            print("Enviando email de prueba...")
            resultado = enviar_email(
                destinatario=mail_username,  # Enviar a sí mismo
                asunto="Prueba de configuración GMAO",
                contenido_html="<h1>Prueba exitosa</h1><p>La configuración de email está funcionando correctamente.</p>",
            )

            if resultado:
                print("✅ Email enviado exitosamente")
                return True
            else:
                print("❌ Error enviando email")
                return False

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


if __name__ == "__main__":
    success = test_email()
    sys.exit(0 if success else 1)
