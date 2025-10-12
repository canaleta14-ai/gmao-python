#!/usr/bin/env python3
"""
Script para inicializar la base de datos gmao-madrid-final con las tablas necesarias
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def inicializar_base_datos():
    """Inicializa la base de datos con todas las tablas necesarias"""
    print("🚀 INICIALIZANDO BASE DE DATOS gmao-madrid-final")
    print("=" * 60)

    # Configurar variables de entorno para la instancia actual
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "temporal-key-for-db-init-only-not-for-production-use"
    os.environ["DB_TYPE"] = "postgresql"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = "GmaoMadrid2025!"
    os.environ["DB_NAME"] = "gmao_production"
    os.environ["DB_HOST"] = (
        "/cloudsql/mantenimiento-470311:europe-southwest1:gmao-madrid-final"
    )

    from app.factory import create_app
    from app.extensions import db

    app = create_app()

    with app.app_context():
        try:
            print("\n1. 🔍 Verificando conexión a Cloud SQL...")
            result = db.session.execute(
                db.text("SELECT current_database(), current_user")
            )
            db_info = result.fetchone()
            print(f"   ✅ Conectado a: {db_info[0]} como {db_info[1]}")

            print("\n2. 📊 Verificando estado actual de la BD...")
            try:
                # Verificar si existen tablas
                result = db.session.execute(
                    db.text(
                        """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """
                    )
                )
                tablas = [row[0] for row in result.fetchall()]
                print(f"   📋 Tablas existentes: {len(tablas)}")
                if tablas:
                    for tabla in tablas:
                        print(f"      - {tabla}")
                else:
                    print("   ⚠️ No hay tablas, base de datos vacía")

            except Exception as e:
                print(f"   ⚠️ Error verificando tablas: {e}")

            print("\n3. 🔄 Creando tablas...")
            try:
                # Crear todas las tablas
                db.create_all()
                print("   ✅ Tablas creadas exitosamente")

                # Verificar que las tablas se crearon
                result = db.session.execute(
                    db.text(
                        """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """
                    )
                )
                tablas_nuevas = [row[0] for row in result.fetchall()]
                print(f"   📋 Tablas después de creación: {len(tablas_nuevas)}")
                for tabla in tablas_nuevas:
                    print(f"      ✓ {tabla}")

            except Exception as e:
                print(f"   ❌ Error creando tablas: {e}")
                raise

            print("\n4. 👤 Creando usuario administrador...")
            try:
                from app.models.usuario import Usuario

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
                        nombre="Administrador",
                        rol="Administrador",
                        activo=True,
                    )
                    admin.set_password("admin123")
                    db.session.add(admin)
                    db.session.commit()
                    print("   ✅ Usuario admin creado (admin/admin123)")

            except Exception as e:
                print(f"   ❌ Error creando usuario: {e}")
                import traceback

                traceback.print_exc()
                # No es crítico, continuar

            print("\n5. 🎯 Verificación final...")
            try:
                # Contar registros en tablas principales
                tablas_verificar = [
                    "usuario",
                    "activo",
                    "plan_mantenimiento",
                    "orden_trabajo",
                ]
                for tabla in tablas_verificar:
                    try:
                        result = db.session.execute(
                            db.text(f"SELECT COUNT(*) FROM {tabla}")
                        )
                        count = result.scalar()
                        print(f"   📊 {tabla}: {count} registros")
                    except Exception as e:
                        print(f"   ⚠️ {tabla}: error verificando - {e}")

            except Exception as e:
                print(f"   ⚠️ Error en verificación final: {e}")

            print("\n6. ✅ INICIALIZACIÓN COMPLETADA")
            print("   🎉 La base de datos está lista para usar")

        except Exception as e:
            print(f"❌ Error durante inicialización: {e}")
            import traceback

            traceback.print_exc()
            return False

    return True


if __name__ == "__main__":
    if inicializar_base_datos():
        print("\n🚀 Base de datos inicializada correctamente")
        print("📌 Credenciales: admin / admin123")
    else:
        print("\n❌ Error en inicialización - revisar logs")
        sys.exit(1)
