#!/usr/bin/env python3
"""
Script para configurar permisos del usuario gmao-user en la base de datos gmao
"""

import subprocess
import sys
import time


def run_command(cmd, description=""):
    """Ejecuta un comando y retorna el resultado"""
    print(f"🔧 {description}")
    print(f"   Comando: {cmd}")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        print(f"   Return code: {result.returncode}")
        if result.stdout.strip():
            print(f"   stdout: {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"   stderr: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("   ❌ Timeout ejecutando comando")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("CONFIGURACIÓN DE PERMISOS GMAO-USER")
    print("=" * 60)

    # SQL Commands para configurar permisos
    sql_commands = [
        # Conectar como postgres y configurar permisos
        'GRANT ALL PRIVILEGES ON DATABASE gmao TO "gmao-user";',
        "\\c gmao",
        'GRANT ALL PRIVILEGES ON SCHEMA public TO "gmao-user";',
        'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "gmao-user";',
        'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "gmao-user";',
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "gmao-user";',
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "gmao-user";',
    ]

    # Crear archivo temporal con comandos SQL
    sql_file = "temp_permissions.sql"
    with open(sql_file, "w") as f:
        for cmd in sql_commands:
            f.write(cmd + "\n")

    print("📋 Comandos SQL creados:")
    for cmd in sql_commands:
        print(f"   {cmd}")

    # Ejecutar comandos SQL usando gcloud sql connect
    print("\n🔗 Conectando a Cloud SQL para ejecutar comandos...")
    cmd = f"gcloud sql connect gmao-postgres-spain --user=postgres --database=postgres < {sql_file}"

    success = run_command(cmd, "Ejecutando comandos SQL de permisos")

    # Limpiar archivo temporal
    try:
        import os

        os.remove(sql_file)
        print(f"🧹 Archivo temporal {sql_file} eliminado")
    except:
        pass

    if success:
        print("\n✅ Permisos configurados exitosamente")

        # Verificar la configuración
        print("\n🔍 Verificando configuración...")

        # Intentar conectar con gmao-user
        test_cmd = 'echo "SELECT current_user, current_database();" | gcloud sql connect gmao-postgres-spain --user=gmao-user --database=gmao'
        test_success = run_command(test_cmd, "Probando conexión con gmao-user")

        if test_success:
            print(
                "\n🎉 ¡Configuración exitosa! gmao-user puede conectar a la base de datos gmao"
            )
        else:
            print("\n⚠️  Configuración completada pero hay problemas de conexión")
    else:
        print("\n❌ Error configurando permisos")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
