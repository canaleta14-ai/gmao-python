#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    print("👥 USUARIOS EN LA BASE DE DATOS:")
    print("=" * 50)

    try:
        usuarios = Usuario.query.all()
        print(f"Total usuarios: {len(usuarios)}")

        if usuarios:
            for user in usuarios:
                print(f"  - ID: {user.id}")
                print(f"    Username: {user.username}")
                print(f"    Nombre: {user.nombre}")
                print(f"    Email: {user.email}")
                print(f"    Rol: {user.rol}")
                print(f"    Activo: {user.activo}")
                print("    " + "-" * 30)
        else:
            print("❌ No hay usuarios en la base de datos")

            # Crear un usuario de prueba
            print("\n🔧 Creando usuario de prueba...")
            from werkzeug.security import generate_password_hash

            usuario_prueba = Usuario(
                username="admin",
                email="admin@test.com",
                password=generate_password_hash("admin123"),
                nombre="Administrador",
                rol="Administrador",
                activo=True,
            )

            from app.extensions import db

            db.session.add(usuario_prueba)
            db.session.commit()

            print("✅ Usuario creado:")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Rol: Administrador")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
