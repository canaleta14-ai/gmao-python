# Configuración Local para GMAO
# Variables de entorno para desarrollo local

import os


class LocalConfig:
    """Configuración para desarrollo local con SQLite"""

    # Base de datos local
    SQLALCHEMY_DATABASE_URI = "sqlite:///gmao_local.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clave secreta para Flask
    SECRET_KEY = "local-development-secret-key-123456"

    # Configuración de email (deshabilitada en local)
    MAIL_SERVER = None
    MAIL_PORT = None
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None

    # Debug activado
    DEBUG = True

    # Configuración específica para desarrollo
    ENV = "development"
    TESTING = False


# Variables de entorno para el sistema
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_DEBUG"] = "1"
