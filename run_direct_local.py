#!/usr/bin/env python3
"""
Script directo para ejecutar GMAO local sin Google Cloud
"""

import os

# Configurar entorno completamente local
os.environ["SECRETS_PROVIDER"] = "env"
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_DEBUG"] = "true"
os.environ["DB_TYPE"] = "sqlite"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gmao_local.db"
os.environ["SECRET_KEY"] = (
    "desarrollo-local-secret-key-super-larga-para-cumplir-requisitos-minimos-64-chars-completos"
)

# Eliminar cualquier variable de Google Cloud
google_vars = [
    "GOOGLE_CLOUD_PROJECT",
    "GAE_ENV",
    "K_SERVICE",
    "GCLOUD_PROJECT",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_QUOTA_PROJECT",
]
for key in google_vars:
    if key in os.environ:
        del os.environ[key]
        print(f"   Eliminada variable: {key}")

# También eliminar otras variables que puedan causar problemas
for key in list(os.environ.keys()):
    if key.startswith("GOOGLE") or key.startswith("GAE") or key.startswith("GCLOUD"):
        del os.environ[key]

print("🚀 Iniciando GMAO local sin Google Cloud...")
print("✅ Variables configuradas:")
print(f"   SECRETS_PROVIDER: {os.environ.get('SECRETS_PROVIDER')}")
print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
print(f"   DB_TYPE: {os.environ.get('DB_TYPE')}")

from main import app

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
