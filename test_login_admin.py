#!/usr/bin/env python3
"""
Script para probar el login del usuario admin
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    print("🔐 PRUEBA DE LOGIN ADMIN:")
    print("=" * 40)

    try:
        # Buscar usuario admin
        admin_user = Usuario.query.filter_by(username="admin").first()

        if admin_user:
            print(f"✅ Usuario admin encontrado:")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Nombre: {admin_user.nombre}")
            print(f"   Rol: {admin_user.rol}")
            print(f"   Activo: {admin_user.activo}")

            # Probar contraseña
            password_test = "admin123"
            if admin_user.check_password(password_test):
                print(f"✅ Contraseña '{password_test}' es correcta")
            else:
                print(f"❌ Contraseña '{password_test}' es incorrecta")

                # Intentar resetear la contraseña
                print("\n🔧 Reseteando contraseña...")
                admin_user.set_password("admin123")

                from app.extensions import db

                db.session.commit()

                print("✅ Contraseña reseteada a 'admin123'")

                # Probar nuevamente
                if admin_user.check_password(password_test):
                    print(f"✅ Contraseña '{password_test}' ahora funciona")
                else:
                    print(f"❌ Contraseña '{password_test}' sigue sin funcionar")
        else:
            print("❌ Usuario admin no encontrado")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
