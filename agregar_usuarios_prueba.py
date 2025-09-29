#!/usr/bin/env python3
"""
Script para agregar usuarios de prueba
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("👥 AGREGANDO USUARIOS DE PRUEBA:")
    print("=" * 50)

    try:
        # Verificar usuarios existentes
        usuarios_existentes = Usuario.query.all()
        print(f"Usuarios actuales: {len(usuarios_existentes)}")

        # Lista de usuarios de prueba
        usuarios_prueba = [
            {
                "username": "juan.perez",
                "email": "juan.perez@empresa.com",
                "nombre": "Juan Pérez",
                "rol": "Técnico",
            },
            {
                "username": "maria.garcia",
                "email": "maria.garcia@empresa.com",
                "nombre": "María García",
                "rol": "Supervisor",
            },
            {
                "username": "carlos.lopez",
                "email": "carlos.lopez@empresa.com",
                "nombre": "Carlos López",
                "rol": "Técnico",
            },
        ]

        usuarios_agregados = 0
        for usuario_data in usuarios_prueba:
            # Verificar si ya existe
            existing = Usuario.query.filter_by(
                username=usuario_data["username"]
            ).first()
            if not existing:
                nuevo_usuario = Usuario(
                    username=usuario_data["username"],
                    email=usuario_data["email"],
                    password=generate_password_hash("123456"),  # Contraseña por defecto
                    nombre=usuario_data["nombre"],
                    rol=usuario_data["rol"],
                    activo=True,
                )
                db.session.add(nuevo_usuario)
                usuarios_agregados += 1
                print(
                    f"✅ Agregado: {usuario_data['nombre']} ({usuario_data['username']})"
                )
            else:
                print(f"⚠️  Ya existe: {usuario_data['username']}")

        if usuarios_agregados > 0:
            db.session.commit()
            print(f"\n🎉 {usuarios_agregados} usuarios agregados correctamente")
        else:
            print("\nℹ️  No se agregaron nuevos usuarios")

        # Mostrar usuarios finales
        usuarios_finales = Usuario.query.all()
        print(f"\nTotal usuarios en DB: {len(usuarios_finales)}")

        for user in usuarios_finales:
            print(f"  - ID {user.id}: {user.nombre} ({user.username}) - {user.rol}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
