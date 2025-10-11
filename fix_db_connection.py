#!/usr/bin/env python3
"""
Script para actualizar la conexión de base de datos de la aplicación actual
para que use la instancia gmao-db que ya está funcionando.
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Completado")
            if result.stdout.strip():
                print(f"📋 Resultado: {result.stdout.strip()}")
        else:
            print(f"❌ Error en {description}: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Excepción en {description}: {e}")
        return False


def main():
    print("🔄 ACTUALIZANDO CONEXIÓN DE BASE DE DATOS")
    print("=" * 50)

    project_id = "mantenimiento-470311"

    # 1. Crear secreto con nombre de base de datos correcto
    print("\n📋 Paso 1: Configurar nombre de base de datos")
    run_command(
        f'echo "gmao_production" | gcloud secrets create gmao-db-name --data-file=- --project={project_id}',
        "Crear secreto gmao-db-name",
    )

    # 2. Crear secreto con usuario correcto
    print("\n👤 Paso 2: Configurar usuario de base de datos")
    run_command(
        f'echo "gmao_user" | gcloud secrets create gmao-db-user --data-file=- --project={project_id}',
        "Crear secreto gmao-db-user",
    )

    # 3. Crear secreto con host correcto (instancia que funciona)
    print("\n🌐 Paso 3: Configurar host de base de datos")
    run_command(
        f'echo "/cloudsql/{project_id}:europe-west1:gmao-db" | gcloud secrets create gmao-db-host-working --data-file=- --project={project_id}',
        "Crear secreto gmao-db-host-working",
    )

    # 4. Verificar secretos creados
    print("\n📊 Paso 4: Verificar secretos")
    run_command(
        f'gcloud secrets list --project={project_id} --filter="name:gmao-db"',
        "Listar secretos de base de datos",
    )

    # 5. Forzar reinicio de la aplicación
    print("\n🔄 Paso 5: Reiniciar aplicación")
    run_command(
        f"gcloud app services set-traffic default --splits=madrid-fix44=1 --project={project_id}",
        "Reiniciar aplicación para cargar nuevos secretos",
    )

    print("\n" + "=" * 50)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("\n📋 Próximos pasos:")
    print("1. Esperar 30-60 segundos para reinicio")
    print("2. Probar la aplicación: https://mantenimiento-470311.ew.r.appspot.com")
    print("3. Si sigue con errores, verificar logs:")
    print(
        f"   gcloud app logs read --service=default --version=madrid-fix44 --limit=10 --project={project_id}"
    )


if __name__ == "__main__":
    main()
