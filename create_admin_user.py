#!/usr/bin/env python3
"""
Script para crear un usuario administrador de prueba
"""

from flask import Flask
from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

def crear_usuario_admin():
    """Crea un usuario administrador de prueba"""
    print("🔧 Creando usuario administrador de prueba...")
    
    # Verificar si ya existe un admin
    admin_existente = Usuario.query.filter_by(rol='Administrador').first()
    if admin_existente:
        print(f"✅ Ya existe un usuario administrador: {admin_existente.username}")
        return admin_existente
    
    # Crear nuevo usuario admin
    try:
        admin_user = Usuario(
            username='admin',
            email='admin@test.com',
            nombre='Administrador Sistema',
            rol='Administrador',
            activo=True
        )
        admin_user.set_password('admin123')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Usuario administrador creado exitosamente:")
        print(f"   👤 Usuario: admin")
        print(f"   🔑 Contraseña: admin123")
        print(f"   📧 Email: admin@test.com")
        print(f"   🎭 Rol: Administrador")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        db.session.rollback()
        return None

def main():
    """Función principal"""
    print("🚀 Creando usuario administrador de prueba")
    print("=" * 50)
    
    # Crear aplicación Flask
    app = create_app()
    
    with app.app_context():
        crear_usuario_admin()

if __name__ == "__main__":
    main()