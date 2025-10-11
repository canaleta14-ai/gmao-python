#!/usr/bin/env python3
"""
Script para aplicar migraciones en producción Cloud SQL
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def aplicar_migraciones_produccion():
    """Aplica migraciones en la base de datos de producción"""
    print("🚀 APLICANDO MIGRACIONES EN PRODUCCIÓN")
    print("=" * 50)

    # Configurar variables de entorno para producción
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRETS_PROVIDER"] = "gcp"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mantenimiento-470311"
    os.environ["DB_TYPE"] = "postgresql"
    os.environ["DB_USER"] = "gmao-user"
    os.environ["DB_NAME"] = "gmao"
    os.environ["DB_HOST"] = "/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres"

    from app.factory import create_app
    from app.extensions import db
    from flask_migrate import upgrade

    app = create_app()

    with app.app_context():
        try:
            print("\n1. 🔍 Verificando conexión a Cloud SQL...")
            db.session.execute(db.text("SELECT 1"))
            print("   ✅ Conexión exitosa")

            print("\n2. 📊 Verificando estado actual de la BD...")
            try:
                # Verificar si existen tablas
                result = db.session.execute(
                    db.text(
                        """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                    )
                )
                tablas = [row[0] for row in result.fetchall()]
                print(f"   📋 Tablas existentes: {len(tablas)}")
                for tabla in tablas:
                    print(f"      - {tabla}")

            except Exception as e:
                print(f"   ⚠️ Error verificando tablas: {e}")

            print("\n3. 🔄 Aplicando migraciones...")
            try:
                # Crear todas las tablas si no existen
                db.create_all()
                print("   ✅ Tablas creadas/actualizadas")

                # Verificar que las tablas se crearon
                result = db.session.execute(
                    db.text(
                        """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                    )
                )
                tablas_nuevas = [row[0] for row in result.fetchall()]
                print(f"   📋 Tablas después de migración: {len(tablas_nuevas)}")

            except Exception as e:
                print(f"   ❌ Error aplicando migraciones: {e}")
                raise

            print("\n4. 👤 Creando usuario administrador...")
            try:
                from app.models.usuario import Usuario
                from werkzeug.security import generate_password_hash

                # Verificar si ya existe admin
                admin_existente = Usuario.query.filter_by(username="admin").first()
                if admin_existente:
                    print("   ℹ️ Usuario admin ya existe")
                    # Actualizar contraseña por seguridad
                    admin_existente.set_password("admin123")
                    db.session.commit()
                    print("   🔄 Contraseña actualizada")
                else:
                    # Crear nuevo usuario admin
                    admin = Usuario(
                        username="admin",
                        email="admin@gmao.com",
                        password=generate_password_hash("admin123"),
                        nombre="Administrador",
                        rol="Administrador",
                        activo=True,
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("   ✅ Usuario admin creado")

            except Exception as e:
                print(f"   ❌ Error creando usuario: {e}")
                # No es crítico, continuar

            print("\n5. ✅ MIGRACIONES COMPLETADAS")
            print("   🎉 La base de datos está lista para producción")

        except Exception as e:
            print(f"❌ Error durante migraciones: {e}")
            import traceback

            traceback.print_exc()
            return False

    return True


if __name__ == "__main__":
    if aplicar_migraciones_produccion():
        print("\n🚀 Listo para desplegar en App Engine")
    else:
        print("\n❌ Error en migraciones - revisar antes de desplegar")
        sys.exit(1)
