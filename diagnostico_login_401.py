#!/usr/bin/env python3
"""
Script de diagnóstico para el error 401 en login
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models.usuario import Usuario
from app.extensions import db
from flask_login import current_user


def diagnosticar_login():
    """Diagnostica problemas de login"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE LOGIN")
    print("=" * 50)

    app = create_app()

    with app.app_context():
        try:
            # 1. Verificar conexión a BD
            print("\n1. Verificando conexión a base de datos...")
            db.session.execute(db.text("SELECT 1"))
            print("✅ Conexión a BD exitosa")

            # 2. Verificar tabla usuarios
            print("\n2. Verificando tabla usuarios...")
            usuarios_count = Usuario.query.count()
            print(f"✅ Tabla usuarios existe - {usuarios_count} usuarios encontrados")

            # 3. Verificar usuario admin
            print("\n3. Verificando usuario admin...")
            admin_user = Usuario.query.filter_by(username="admin").first()
            if admin_user:
                print(f"✅ Usuario admin encontrado:")
                print(f"   - ID: {admin_user.id}")
                print(f"   - Username: {admin_user.username}")
                print(f"   - Email: {admin_user.email}")
                print(f"   - Activo: {admin_user.activo}")
                print(f"   - Rol: {admin_user.rol}")
                print(
                    f"   - Password hash: {'***' if admin_user.password else 'NO DEFINIDO'}"
                )

                # 4. Probar autenticación
                print("\n4. Probando autenticación con admin/admin123...")
                if admin_user.check_password("admin123"):
                    print("✅ Autenticación exitosa")
                else:
                    print("❌ Fallo en autenticación - contraseña incorrecta")
                    # Intentar resetear password
                    print("🔧 Reseteando contraseña a 'admin123'...")
                    admin_user.set_password("admin123")
                    db.session.commit()
                    print("✅ Contraseña reseteada")

            else:
                print("❌ Usuario admin NO encontrado")
                print("🔧 Creando usuario admin...")
                from werkzeug.security import generate_password_hash

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
                print("✅ Usuario admin creado")

            # 5. Verificar configuración de Flask-Login
            print("\n5. Verificando configuración de Flask-Login...")
            from flask_login import LoginManager

            login_manager = app.login_manager
            print(f"✅ LoginManager configurado: {login_manager is not None}")
            print(f"✅ Login view: {login_manager.login_view}")

            # 6. Verificar rutas de login
            print("\n6. Verificando rutas de login...")
            for rule in app.url_map.iter_rules():
                if "login" in rule.rule:
                    print(f"✅ Ruta encontrada: {rule.rule} -> {rule.endpoint}")

            # 7. Verificar variables de entorno críticas
            print("\n7. Verificando variables de entorno...")
            secret_key = app.config.get("SECRET_KEY")
            print(f"✅ SECRET_KEY configurado: {'Sí' if secret_key else 'NO'}")

            if secret_key:
                print(f"   Longitud: {len(secret_key)} caracteres")

            # 8. Verificar sesiones
            print("\n8. Verificando configuración de sesiones...")
            print(
                f"✅ SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE')}"
            )
            print(
                f"✅ SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}"
            )
            print(
                f"✅ SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}"
            )

        except Exception as e:
            print(f"❌ Error durante diagnóstico: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    diagnosticar_login()
