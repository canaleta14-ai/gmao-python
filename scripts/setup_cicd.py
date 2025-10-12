#!/usr/bin/env python3
"""
Script para configurar CI/CD automáticamente en Google Cloud Platform
Ejecutar: python scripts/setup_cicd.py
"""

import subprocess
import json
import sys
import os


def run_command(command, capture_output=True):
    """Ejecutar comando shell y retornar resultado"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Error ejecutando: {command}")
                print(f"Error: {result.stderr}")
                return None
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0
    except Exception as e:
        print(f"❌ Excepción ejecutando {command}: {e}")
        return None


def check_gcloud_auth():
    """Verificar autenticación con gcloud"""
    print("🔍 Verificando autenticación con Google Cloud...")

    result = run_command("gcloud auth list --format='value(account)'")
    if not result:
        print("❌ No hay sesión activa en gcloud")
        print("💡 Ejecuta: gcloud auth login")
        return False

    print(f"✅ Autenticado como: {result}")
    return True


def check_project():
    """Verificar proyecto activo"""
    print("🔍 Verificando proyecto de Google Cloud...")

    project = run_command("gcloud config get-value project")
    if project != "mantenimiento-470311":
        print(f"⚠️ Proyecto actual: {project}")
        print("🔧 Configurando proyecto correcto...")

        if not run_command(
            "gcloud config set project mantenimiento-470311", capture_output=False
        ):
            print("❌ Error configurando proyecto")
            return False

    print("✅ Proyecto configurado: mantenimiento-470311")
    return True


def enable_apis():
    """Habilitar APIs necesarias"""
    print("🔧 Habilitando APIs necesarias...")

    apis = [
        "appengine.googleapis.com",
        "cloudsql.googleapis.com",
        "storage-api.googleapis.com",
        "iam.googleapis.com",
    ]

    for api in apis:
        print(f"  Habilitando {api}...")
        run_command(f"gcloud services enable {api}")

    print("✅ APIs habilitadas")


def create_service_account():
    """Crear service account para CI/CD"""
    print("🤖 Configurando service account para CI/CD...")

    sa_email = "gmao-ci-cd@mantenimiento-470311.iam.gserviceaccount.com"

    # Verificar si ya existe
    existing = run_command(f"gcloud iam service-accounts describe {sa_email}")
    if existing:
        print("✅ Service account ya existe")
    else:
        print("  Creando service account...")
        cmd = """gcloud iam service-accounts create gmao-ci-cd \
            --description="Service Account para CI/CD de GMAO" \
            --display-name="GMAO CI/CD\""""
        run_command(cmd)

    # Asignar roles necesarios
    print("  Asignando roles...")
    roles = [
        "roles/appengine.appAdmin",
        "roles/storage.admin",
        "roles/cloudsql.client",
        "roles/viewer",
    ]

    for role in roles:
        cmd = f"""gcloud projects add-iam-policy-binding mantenimiento-470311 \
            --member="serviceAccount:{sa_email}" \
            --role="{role}\""""
        run_command(cmd)

    print("✅ Service account configurado")
    return sa_email


def generate_service_account_key(sa_email):
    """Generar clave JSON para service account"""
    print("🔑 Generando clave de service account...")

    key_file = "gmao-ci-cd-key.json"

    # Eliminar clave anterior si existe
    if os.path.exists(key_file):
        os.remove(key_file)

    cmd = f"""gcloud iam service-accounts keys create {key_file} \
        --iam-account={sa_email}"""

    if run_command(cmd, capture_output=False):
        print(f"✅ Clave generada: {key_file}")

        # Leer y mostrar la clave para configurar en GitHub
        with open(key_file, "r") as f:
            key_content = f.read()

        print("\n" + "=" * 60)
        print("🔐 CONFIGURACIÓN DE GITHUB SECRETS")
        print("=" * 60)
        print("1. Ve a tu repositorio en GitHub")
        print("2. Settings > Secrets and variables > Actions")
        print("3. Agrega estos Repository secrets:")
        print("")
        print("GCP_PROJECT_ID:")
        print("mantenimiento-470311")
        print("")
        print("GCP_SA_KEY:")
        print(key_content)
        print("")
        print("=" * 60)

        return True
    else:
        print("❌ Error generando clave")
        return False


def setup_app_engine():
    """Configurar App Engine si no existe"""
    print("🚀 Verificando configuración de App Engine...")

    # Verificar si App Engine ya está configurado
    result = run_command("gcloud app describe")
    if result:
        print("✅ App Engine ya configurado")
        return True

    print("  Configurando App Engine...")
    cmd = "gcloud app create --region=europe-west1"

    if run_command(cmd, capture_output=False):
        print("✅ App Engine configurado")
        return True
    else:
        print("❌ Error configurando App Engine")
        return False


def validate_setup():
    """Validar que todo esté configurado correctamente"""
    print("✅ Validando configuración...")

    # Verificar que se pueda hacer deploy
    print("  Verificando permisos de deployment...")

    # Crear un app.yaml temporal mínimo para test
    test_app_yaml = """
runtime: python39
service: ci-cd-test

handlers:
- url: /.*
  script: auto
"""

    with open("test-app.yaml", "w") as f:
        f.write(test_app_yaml)

    # Intentar validar (sin hacer deploy real)
    result = run_command(
        "gcloud app deploy test-app.yaml --no-promote --version=test --quiet --dry-run"
    )

    # Limpiar archivo temporal
    if os.path.exists("test-app.yaml"):
        os.remove("test-app.yaml")

    if result is not None:
        print("✅ Configuración validada correctamente")
        return True
    else:
        print("⚠️ Posibles problemas en la configuración")
        return False


def main():
    """Función principal"""
    print("🔧 CONFIGURACIÓN AUTOMÁTICA CI/CD PARA GMAO SISTEMA")
    print("=" * 60)

    steps = [
        ("Verificar autenticación", check_gcloud_auth),
        ("Verificar proyecto", check_project),
        ("Habilitar APIs", enable_apis),
        ("Configurar App Engine", setup_app_engine),
        ("Crear service account", create_service_account),
    ]

    sa_email = None

    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")

        if step_func == create_service_account:
            sa_email = step_func()
            if not sa_email:
                print(f"❌ Error en: {step_name}")
                sys.exit(1)
        else:
            if not step_func():
                print(f"❌ Error en: {step_name}")
                sys.exit(1)

    # Generar clave de service account
    print(f"\n📋 Generar clave de service account...")
    if not generate_service_account_key(sa_email):
        print("❌ Error generando clave")
        sys.exit(1)

    # Validar configuración
    print(f"\n📋 Validar configuración...")
    validate_setup()

    print("\n🎉 CONFIGURACIÓN COMPLETADA!")
    print("=" * 60)
    print("📝 PRÓXIMOS PASOS:")
    print("1. Configura los secrets en GitHub (ver arriba)")
    print("2. Haz push de los archivos .github/workflows/")
    print("3. Los deployments se ejecutarán automáticamente")
    print("4. develop -> staging, main -> production")
    print("")
    print("🔗 URLs importantes:")
    print("📊 Production: https://mantenimiento-470311.ew.r.appspot.com")
    print("🧪 Staging: https://staging-dot-mantenimiento-470311.ew.r.appspot.com")
    print("")
    print(
        "⚠️ RECUERDA: Elimina el archivo gmao-ci-cd-key.json después de configurar GitHub"
    )


if __name__ == "__main__":
    main()
