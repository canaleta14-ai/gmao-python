#!/usr/bin/env python3
"""
Script para ejecutar GMAO en modo desarrollo local
Configura todas las variables de entorno necesarias para desarrollo
"""

import os


def setup_local_environment():
    """Configura variables de entorno para desarrollo local"""

    # Forzar modo de desarrollo
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "true"
    os.environ["ENV"] = "development"
    os.environ["SECRETS_PROVIDER"] = "env"

    # No estamos en Google Cloud
    if "GAE_ENV" in os.environ:
        del os.environ["GAE_ENV"]

    # Configuración de base de datos local
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gmao_local.db"

    # Secret key suficientemente larga
    os.environ["SECRET_KEY"] = (
        "local-development-secret-key-muy-segura-123456789-abcdefghijklmnopqrstuvwxyz-DESARROLLO"
    )

    # Configuración del servidor
    os.environ["FLASK_HOST"] = "localhost"
    os.environ["FLASK_PORT"] = "5000"

    # Email deshabilitado en desarrollo
    os.environ["MAIL_SERVER"] = ""
    os.environ["MAIL_USERNAME"] = ""
    os.environ["MAIL_PASSWORD"] = ""

    print("✅ Entorno local configurado:")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   DB_TYPE: {os.environ.get('DB_TYPE')}")
    print(
        f"   SECRET_KEY: {'***configurada***' if os.environ.get('SECRET_KEY') else 'NO'}"
    )
    print(f"   DEBUG: {os.environ.get('FLASK_DEBUG')}")


if __name__ == "__main__":
    print("🚀 Iniciando GMAO en modo desarrollo local...")

    # Configurar entorno
    setup_local_environment()

    # Importar y ejecutar la aplicación
    from main import app

    print("🌐 Aplicación disponible en: http://localhost:5000")
    print("👤 Usuario: admin | Contraseña: admin123")
    print("📱 Presiona Ctrl+C para detener")

    app.run(debug=True, host="localhost", port=5000)
