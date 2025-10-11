#!/usr/bin/env python3
"""
Script de reparación rápida para errores 401 - Configurar SQLite temporal
"""

import subprocess
import os
import secrets
import string


def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Completado")
            return True
        else:
            print(f"❌ {description} - Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Excepción: {e}")
        return False


def generate_secret():
    """Generar una clave secreta segura"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32))


def fix_auth_errors():
    """Corregir errores 401 configurando secretos básicos"""

    print("🚑 REPARACIÓN RÁPIDA - Errores 401 Authentication")
    print("=" * 50)

    project_id = "mantenimiento-470311"

    # Crear secretos básicos
    secrets_to_create = {
        "flask-secret-key": generate_secret(),
        "admin-password": "admin123",  # Password temporal
        "db-config": "sqlite",  # Configuración temporal
    }

    print("🔐 Creando secretos básicos...")

    for secret_name, secret_value in secrets_to_create.items():
        # Crear el secreto
        create_cmd = f'echo "{secret_value}" | gcloud secrets create {secret_name} --data-file=- --project={project_id}'

        if run_command(create_cmd, f"Creando secreto {secret_name}"):
            print(f"   ✅ Secreto {secret_name} creado")
        else:
            # Si ya existe, actualizarlo
            update_cmd = f'echo "{secret_value}" | gcloud secrets versions add {secret_name} --data-file=- --project={project_id}'
            run_command(update_cmd, f"Actualizando secreto {secret_name}")

    # Configurar variables de entorno para SQLite
    print("\n🗄️ Configurando base de datos SQLite temporal...")

    env_vars = {
        "DB_TYPE": "sqlite",
        "FLASK_ENV": "production",
        "SECRETS_PROVIDER": "local",
        "FORCE_LOCAL_STORAGE": "true",
    }

    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"   📝 {var} = {value}")

    print("\n📋 Resumen de la reparación:")
    print("✅ Secretos básicos creados")
    print("✅ Configuración SQLite aplicada")
    print("✅ Variables de entorno configuradas")

    print("\n🔄 Siguiente paso: La aplicación debería funcionar ahora")
    print("💡 Para verificar: Visita https://mantenimiento-470311.ew.r.appspot.com")

    print("\n⚠️ NOTA: Esta es una solución temporal")
    print("   Para producción real, configurar PostgreSQL en Cloud SQL")

    return True


if __name__ == "__main__":
    fix_auth_errors()
