#!/usr/bin/env python3
"""
Script para actualizar configuración para el proyecto mantenimiento-470311
"""

import os
import re


def update_config_files():
    """Actualizar archivos de configuración con el proyecto correcto"""

    print("🔧 Actualizando configuración para proyecto mantenimiento-470311...")

    project_id = "mantenimiento-470311"
    bucket_name = "mantenimiento-gmao-uploads-eu"

    # Archivos a actualizar
    files_to_update = {
        "app-production.yaml": [
            ("disfood-gmao", project_id),
            ("disfood-gmao-uploads-eu", bucket_name),
            ("europe-west1:gmao-db", f"europe-west1:gmao-db"),
        ],
        "run_production.py": [
            ("disfood-gmao", project_id),
            ("disfood-gmao-uploads", bucket_name),
        ],
        "config_secrets.py": [
            ("disfood-gmao", project_id),
        ],
    }

    for filename, replacements in files_to_update.items():
        if os.path.exists(filename):
            print(f"📝 Actualizando {filename}...")

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            for old_value, new_value in replacements:
                content = content.replace(old_value, new_value)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ {filename} actualizado")
        else:
            print(f"⚠️ {filename} no encontrado")

    # Configurar variables de entorno
    print("\n🌍 Configurando variables de entorno...")

    env_vars = {
        "GOOGLE_CLOUD_PROJECT": project_id,
        "GCP_PROJECT": project_id,
        "GCS_BUCKET_NAME": bucket_name,
        "GCLOUD_REGION": "europe-west1",
        "TIMEZONE": "Europe/Madrid",
        "LANGUAGE": "es",
        "GDPR_COMPLIANCE": "true",
        "DATA_RETENTION_YEARS": "7",
    }

    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"   {var} = {value}")

    print("\n✅ Configuración actualizada para España/GDPR")
    print(f"📋 Proyecto: {project_id}")
    print(f"🪣 Bucket: {bucket_name}")
    print(f"🌍 Región: europe-west1")
    print(f"🇪🇸 Zona horaria: Europe/Madrid")

    return True


if __name__ == "__main__":
    update_config_files()
    print("\n🚀 Listo para deployment. Ejecuta: .\deploy_step2.ps1")
