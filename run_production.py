#!/usr/bin/env python3
"""
Script de configuración para producción en Google Cloud - Disfood España
"""

import os
import sys


def main():
    print("🚀 Configurando GMAO para producción en Google Cloud - Disfood España...")

    # Configurar variables de producción
    os.environ["SECRETS_PROVIDER"] = "gcp"  # Usar Google Secret Manager
    os.environ["FLASK_ENV"] = "production"
    os.environ["DB_TYPE"] = "postgresql"  # PostgreSQL en Cloud SQL

    # Variables específicas de Disfood España
    os.environ["GCP_PROJECT"] = "mantenimiento-470311"  # Ajustar según proyecto real
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mantenimiento-470311"
    os.environ["GCLOUD_REGION"] = "europe-west1"  # Región europea para GDPR

    # Configuración regional España
    os.environ["TIMEZONE"] = "Europe/Madrid"
    os.environ["LANGUAGE"] = "es"
    os.environ["LOCALE"] = "es_ES.UTF-8"

    # Base de datos PostgreSQL en Cloud SQL (región europea)
    os.environ["DB_HOST"] = "127.0.0.1"  # Cloud SQL Proxy
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = "gmao_production"
    os.environ["DB_USER"] = "gmao_user"
    # DB_PASSWORD se obtiene de Secret Manager

    # Storage para archivos (región europea)
    os.environ["GCS_BUCKET_NAME"] = "mantenimiento-470311-uploads-eu"
    os.environ["FORCE_LOCAL_STORAGE"] = "false"  # Usar Google Cloud Storage

    # Configuración de seguridad y GDPR
    os.environ["SESSION_COOKIE_SECURE"] = "true"
    os.environ["REMEMBER_COOKIE_SECURE"] = "true"
    os.environ["WTF_CSRF_SSL_STRICT"] = "true"
    os.environ["GDPR_COMPLIANCE"] = "true"
    os.environ["DATA_RETENTION_DAYS"] = "2555"  # 7 años según normativa española

    # Rate limiting más estricto
    os.environ["RATELIMIT_STORAGE_URL"] = "redis://localhost:6379"

    print("✅ Variables de producción configuradas para España:")
    print("   SECRETS_PROVIDER: gcp (Google Secret Manager)")
    print("   FLASK_ENV: production")
    print("   DB_TYPE: postgresql (Cloud SQL)")
    print("   REGIÓN: europe-west1 (Cumplimiento GDPR)")
    print("   TIMEZONE: Europe/Madrid")
    print("   LANGUAGE: es (Español)")
    print("   GCS_BUCKET: mantenimiento-470311-uploads-eu")
    print("   SECURITY: Cookies seguras habilitadas")
    print("   GDPR: Cumplimiento activado (7 años retención)")

    # Importar y ejecutar la aplicación
    try:
        from app.factory import create_app

        app = create_app()

        print("\n✅ Aplicación configurada para producción")
        print("🌐 Lista para deployment en Google Cloud")
        print("🏢 Entorno: Disfood")
        print("--------------------------------------------------")

        # En producción, usar Gunicorn en lugar de Flask dev server
        if len(sys.argv) > 1 and sys.argv[1] == "--dev-test":
            print("⚠️ MODO TEST - NO USAR EN PRODUCCIÓN")
            app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        else:
            print(
                "ℹ️ Para ejecutar: gunicorn --bind :$PORT --workers 4 'run_production:app'"
            )
            return app

    except Exception as e:
        print(f"❌ Error configurando aplicación: {e}")
        sys.exit(1)


# Para importar la app desde Gunicorn
app = None

if __name__ == "__main__":
    app = main()
else:
    # Cuando se importa desde Gunicorn
    app = main()
