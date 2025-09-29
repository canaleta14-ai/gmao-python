#!/usr/bin/env python3
"""
Script para verificar y crear usuario admin por defecto
"""

from app.factory import create_app
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash


def main():
    app = create_app()
    with app.app_context():
        # Verificar usuarios existentes
        users = Usuario.query.all()
        print(f"Usuarios encontrados: {len(users)}")

        if users:
            print("Usuarios existentes:")
            for user in users:
                print(
                    f"  - ID: {user.id}, Username: {user.username}, Rol: {user.rol}, Activo: {user.activo}"
                )
        else:
            print("No hay usuarios. Creando usuario admin...")

            # Crear usuario admin
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

            print("✅ Usuario admin creado exitosamente!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Rol: Administrador")


if __name__ == "__main__":
    main()
