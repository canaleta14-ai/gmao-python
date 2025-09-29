#!/usr/bin/env python3
"""
Script de prueba para verificar la autenticación en GMAO
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.models.usuario import Usuario
from app.extensions import db
from flask_login import login_user, current_user, logout_user


def test_auth():
    """Prueba básica de autenticación"""
    app = create_app()

    with app.app_context():
        print("=== PRUEBA DE AUTENTICACIÓN ===")

        # Verificar conexión a BD
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✓ Conexión a base de datos OK")
        except Exception as e:
            print(f"✗ Error de conexión a BD: {e}")
            return

        # Buscar usuario de prueba
        user = Usuario.query.filter_by(username="admin").first()
        if not user:
            print("✗ Usuario 'admin' no encontrado")
            return

        print(
            f"✓ Usuario encontrado: {user.username} (ID: {user.id}, Activo: {user.activo})"
        )

        # Probar login
        with app.test_request_context():
            login_user(user)
            print(f"✓ Login exitoso para {current_user.username}")
            print(f"✓ Usuario autenticado: {current_user.is_authenticated}")
            print(f"✓ ID de usuario: {current_user.id}")

            # Probar logout
            logout_user()
            print(f"✓ Logout exitoso, autenticado: {current_user.is_authenticated}")

        print("=== PRUEBA COMPLETADA ===")


if __name__ == "__main__":
    test_auth()
