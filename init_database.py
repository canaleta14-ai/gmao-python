#!/usr/bin/env python3
"""
Script para inicializar la base de datos Cloud SQL con las tablas necesarias
y crear un usuario administrador de prueba.
"""

import subprocess
import sys
import os


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
            if "already exists" in result.stderr.lower():
                print(f"ℹ️ El recurso ya existe, continuando...")
                return True
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Excepción en {description}: {e}")
        return False


def main():
    print("🚀 INICIALIZANDO BASE DE DATOS CLOUD SQL")
    print("=" * 50)

    project_id = "mantenimiento-470311"
    instance_name = "gmao-postgres-spain"

    # 1. Verificar que la instancia esté lista
    print("\n📊 Paso 1: Verificar instancia Cloud SQL")
    run_command(
        f'gcloud sql instances describe {instance_name} --project={project_id} --format="value(state)"',
        "Verificar estado de la instancia",
    )

    # 2. Crear base de datos gmao_production (además de postgres)
    print("\n🗄️ Paso 2: Crear base de datos adicional")
    run_command(
        f"gcloud sql databases create gmao_production --instance={instance_name} --project={project_id}",
        "Crear base de datos gmao_production",
    )

    # 3. Ejecutar migraciones usando el script local
    print("\n📋 Paso 3: Ejecutar migraciones")

    # Configurar variables de entorno para la migración
    env_vars = {
        "FLASK_ENV": "production",
        "SECRETS_PROVIDER": "gcp",
        "GOOGLE_CLOUD_PROJECT": project_id,
        "DB_TYPE": "postgresql",
        "DB_USER": "postgres",
        "DB_NAME": "postgres",
        "DB_HOST": f"/cloudsql/{project_id}:europe-southwest1:{instance_name}",
        "DB_PORT": "5432",
    }

    # Crear archivo temporal con variables de entorno
    env_content = "\\n".join([f"export {k}={v}" for k, v in env_vars.items()])

    # Crear script de migración
    migration_script = f"""
# Configurar variables de entorno
{env_content}

# Ejecutar migraciones
echo "📋 Ejecutando migraciones de base de datos..."
python -c "
from app import create_app
from app.extensions import db
import os

print('Creando aplicación...')
app = create_app()

with app.app_context():
    print('Creando todas las tablas...')
    db.create_all()
    print('✅ Tablas creadas correctamente')
    
    # Crear usuario administrador
    from app.models.usuario import Usuario
    from werkzeug.security import generate_password_hash
    
    print('Verificando usuario administrador...')
    admin = Usuario.query.filter_by(email='admin@disfood.com').first()
    if not admin:
        admin = Usuario(
            nombre='Administrador',
            apellido='Sistema',
            email='admin@disfood.com',
            password_hash=generate_password_hash('admin123'),
            rol='admin',
            activo=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuario administrador creado: admin@disfood.com / admin123')
    else:
        print('ℹ️ Usuario administrador ya existe')
"
"""

    # Escribir script temporal
    with open("temp_migration.sh", "w") as f:
        f.write(migration_script)

    # Hacer ejecutable y ejecutar
    os.chmod("temp_migration.sh", 0o755)
    run_command("bash temp_migration.sh", "Ejecutar migraciones y crear usuario admin")

    # Limpiar archivo temporal
    if os.path.exists("temp_migration.sh"):
        os.remove("temp_migration.sh")

    print("\n" + "=" * 50)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("\n📋 Credenciales de prueba:")
    print("   Email: admin@disfood.com")
    print("   Contraseña: admin123")
    print("\n🌐 Probar login en:")
    print(f"   https://{project_id}.ew.r.appspot.com/login")


if __name__ == "__main__":
    main()
