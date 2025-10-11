#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos y crear un usuario de prueba.
"""


def test_login():
    """Probar login con un usuario existente o crear uno nuevo"""
    print("🔐 PROBANDO CONEXIÓN Y LOGIN")
    print("=" * 40)

    # Configurar variables de entorno
    import os

    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRETS_PROVIDER"] = "gcp"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mantenimiento-470311"
    os.environ["DB_TYPE"] = "postgresql"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_NAME"] = "postgres"
    os.environ["DB_HOST"] = (
        "/cloudsql/mantenimiento-470311:europe-southwest1:gmao-postgres-spain"
    )
    os.environ["DB_PORT"] = "5432"

    try:
        print("📱 Importando aplicación...")
        from app import create_app
        from app.extensions import db

        print("🚀 Creando aplicación...")
        app = create_app()

        with app.app_context():
            print("🔍 Verificando conexión a base de datos...")

            # Probar conexión básica
            result = db.engine.execute("SELECT 1 as test")
            print("✅ Conexión a base de datos exitosa")

            # Verificar si existen tablas
            tables = db.engine.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            ).fetchall()

            print(f"📋 Tablas encontradas: {len(tables)}")

            if len(tables) == 0:
                print("🔧 No hay tablas, creando estructura...")
                db.create_all()
                print("✅ Tablas creadas")

            # Verificar/crear usuario administrador
            from app.models.usuario import Usuario
            from werkzeug.security import generate_password_hash

            print("👤 Verificando usuario administrador...")
            admin = Usuario.query.filter_by(email="admin@disfood.com").first()

            if not admin:
                print("🔧 Creando usuario administrador...")
                admin = Usuario(
                    nombre="Admin",
                    apellido="Sistema",
                    email="admin@disfood.com",
                    password_hash=generate_password_hash("admin123"),
                    rol="admin",
                    activo=True,
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario admin creado: admin@disfood.com / admin123")
            else:
                print("ℹ️ Usuario admin ya existe")

            print("\n" + "=" * 40)
            print("✅ BASE DE DATOS LISTA PARA LOGIN")
            print("\n📋 Credenciales de prueba:")
            print("   Email: admin@disfood.com")
            print("   Contraseña: admin123")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_login()
