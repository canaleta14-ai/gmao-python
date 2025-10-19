#!/usr/bin/env python3
"""
Script para crear usuario administrador en PostgreSQL
"""
import os
import sys
from pathlib import Path

# Agregar la raíz del proyecto al path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario


def crear_admin_postgres():
    """Crear usuario admin en PostgreSQL"""
    try:
        # Crear la aplicación
        app = create_app()

        with app.app_context():
            # Verificar si el admin ya existe
            admin_existente = Usuario.query.filter_by(username="admin").first()

            if admin_existente:
                print(f"Usuario admin ya existe con ID: {admin_existente.id}")
                # Actualizar contraseña por si acaso
                admin_existente.set_password("admin123")
                db.session.commit()
                print("Contraseña del admin actualizada a 'admin123'")
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

                print(f"Usuario admin creado exitosamente con ID: {admin.id}")
                print("Credenciales: admin / admin123")

            # Verificar la creación
            admin_verify = Usuario.query.filter_by(username="admin").first()
            if admin_verify:
                print(f"✅ Verificación exitosa:")
                print(f"   - ID: {admin_verify.id}")
                print(f"   - Username: {admin_verify.username}")
                print(f"   - Email: {admin_verify.email}")
                print(f"   - Nombre: {admin_verify.nombre}")
                print(f"   - Rol: {admin_verify.rol}")
                print(f"   - Activo: {admin_verify.activo}")
                return True
            else:
                print("❌ Error: No se pudo verificar la creación del usuario")
                return False

    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Creando usuario administrador en PostgreSQL...")
    success = crear_admin_postgres()

    if success:
        print("\n✅ Usuario admin configurado correctamente")
        print("Puedes iniciar sesión con: admin / admin123")
    else:
        print("\n❌ Error configurando usuario admin")
        sys.exit(1)
