#!/usr/bin/env python3
"""
Script para ejecutar migraciones en Cloud SQL (producción)
"""
import os
import sys
from app.factory import create_app
from app.extensions import db
from flask_migrate import upgrade


def setup_production_environment():
    """Configurar entorno de producción para migraciones"""
    print("🔧 Configurando entorno de producción...")

    # Configuración de producción
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRETS_PROVIDER"] = "gcp"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mantenimiento-470311"
    os.environ["DB_TYPE"] = "postgresql"

    # Configuración directa para evitar problemas con Secret Manager
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_NAME"] = "gmao_production"
    os.environ["DB_HOST"] = (
        "/cloudsql/mantenimiento-470311:europe-southwest1:gmao-madrid-final"
    )
    os.environ["DB_PASSWORD"] = "GmaoMadrid2025!"

    # SECRET_KEY temporal para migraciones
    os.environ["SECRET_KEY"] = (
        "migration-key-for-database-setup-only-not-for-production-use"
    )

    print("✅ Variables de entorno configuradas")


def run_migrations():
    """Ejecutar migraciones en la base de datos"""
    try:
        print("🚀 Creando aplicación Flask...")
        app = create_app()

        with app.app_context():
            print("🔍 Verificando conexión a la base de datos...")

            # Verificar conexión
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(db.text("SELECT 1"))
                    result.fetchone()
                print("✅ Conexión a Cloud SQL establecida")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
                return False

            print("📊 Ejecutando migraciones...")

            # Ejecutar migraciones
            try:
                upgrade()
                print("✅ Migraciones ejecutadas exitosamente")

                # Verificar tablas creadas
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"📋 Tablas en la base de datos: {len(tables)}")
                for table in sorted(tables):
                    print(f"   - {table}")

                return True

            except Exception as e:
                print(f"❌ Error ejecutando migraciones: {e}")
                return False

    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        return False


def verify_data():
    """Verificar estado de los datos después de la migración"""
    try:
        app = create_app()
        with app.app_context():
            print("🔍 Verificando datos existentes...")

            # Importar modelos para verificación
            from app.models.usuario import Usuario
            from app.models.inventario import Inventario
            from app.models.activo import Activo

            # Contar registros
            usuarios_count = Usuario.query.count()
            inventario_count = Inventario.query.count()
            activos_count = Activo.query.count()

            print(f"📊 Estado de la base de datos:")
            print(f"   - Usuarios: {usuarios_count}")
            print(f"   - Items de inventario: {inventario_count}")
            print(f"   - Activos: {activos_count}")

            return True

    except Exception as e:
        print(f"⚠️  Error verificando datos: {e}")
        return False


def main():
    """Función principal"""
    print("🏗️  === MIGRACIONES CLOUD SQL - GMAO SISTEMA ===")
    print()

    # Configurar entorno
    setup_production_environment()

    # Ejecutar migraciones
    if run_migrations():
        print("✅ Migraciones completadas exitosamente")

        # Verificar datos
        verify_data()

        print()
        print("🎉 Base de datos de producción lista!")
        print("🔗 Conexión: mantenimiento-470311:europe-southwest1:gmao-madrid-final")
        print("🗄️  Base de datos: gmao_production")

        return True
    else:
        print("❌ Error en las migraciones")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
