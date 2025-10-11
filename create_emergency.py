#!/usr/bin/env python3
"""
Solución de emergencia para errores 401 - Usar versión local SQLite
"""

import os
import shutil


def create_emergency_version():
    """Crear configuración de emergencia con SQLite"""

    print("🚑 CREANDO VERSIÓN DE EMERGENCIA CON SQLITE")
    print("=" * 50)

    # Crear app.yaml temporal con SQLite
    emergency_yaml = """# App Engine config - EMERGENCY SQLite Version
runtime: python311

# Variables de entorno SQLite temporal
env_variables:
  FLASK_ENV: "production"
  DB_TYPE: "sqlite"
  SECRETS_PROVIDER: "local"
  FORCE_LOCAL_STORAGE: "true"
  
  # Proyecto básico
  GOOGLE_CLOUD_PROJECT: "mantenimiento-470311"
  
  # Variables temporales para funcionamiento
  SECRET_KEY: "emergency-key-2025"
  ADMIN_EMAILS: "j_hidalgo@disfood.com"
  
  # Configuración España
  TIMEZONE: "Europe/Madrid"
  LANGUAGE: "es"
  GDPR_COMPLIANCE: "true"

# Manejadores básicos
handlers:
  - url: /static
    static_dir: static
    secure: always
    
  - url: /.*
    script: auto
    secure: always
"""

    with open("app-emergency.yaml", "w", encoding="utf-8") as f:
        f.write(emergency_yaml)

    print("✅ Archivo app-emergency.yaml creado")

    # Crear run_emergency.py
    emergency_run = """#!/usr/bin/env python3
# Emergency runner with SQLite

import os
import sys

# Configurar para SQLite local
os.environ["DB_TYPE"] = "sqlite"
os.environ["FORCE_LOCAL_STORAGE"] = "true"
os.environ["SECRETS_PROVIDER"] = "local"
os.environ["FLASK_ENV"] = "production"

# Variables básicas
os.environ["SECRET_KEY"] = "emergency-key-2025"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mantenimiento-470311"

print("🚑 Modo emergencia: SQLite configurado")

try:
    from app.factory import create_app
    app = create_app()
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""

    with open("run_emergency.py", "w", encoding="utf-8") as f:
        f.write(emergency_run)

    print("✅ Archivo run_emergency.py creado")

    print("\n🚀 Para desplegar versión de emergencia:")
    print("gcloud app deploy app-emergency.yaml --version=emergency --no-promote")

    return True


if __name__ == "__main__":
    create_emergency_version()
