#!/usr/bin/env python3
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
