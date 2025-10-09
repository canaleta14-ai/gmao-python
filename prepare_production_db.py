#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario

def prepare_production_database():
    """Preparar base de datos limpia para producción con usuario administrador"""
    app = create_app()
    
    with app.app_context():
        print("=== PREPARACIÓN DE BASE DE DATOS PARA PRODUCCIÓN ===\n")
        
        # 1. Limpiar completamente la base de datos
        print("🧹 Limpiando base de datos...")
        try:
            # Eliminar todas las tablas y recrearlas
            db.drop_all()
            db.create_all()
            print("   ✅ Base de datos limpiada y recreada")
        except Exception as e:
            print(f"   ❌ Error limpiando base de datos: {e}")
            return False
        
        # 2. Crear usuario administrador para producción
        print("\n👤 Creando usuario administrador para producción...")
        try:
            # Verificar si ya existe un admin
            admin_existente = Usuario.query.filter_by(username='admin').first()
            
            if admin_existente:
                print(f"   ⚠️ Usuario administrador ya existe: {admin_existente.username}")
            else:
                # Crear nuevo usuario administrador
                admin_user = Usuario(
                    username='admin',
                    email='admin@gmao.com',
                    nombre='Administrador Sistema',
                    rol='Administrador',
                    activo=True
                )
                admin_user.set_password('admin123')  # Cambiar en producción
                
                db.session.add(admin_user)
                db.session.commit()
                
                print(f"   ✅ Usuario administrador creado:")
                print(f"      - Username: {admin_user.username}")
                print(f"      - Email: {admin_user.email}")
                print(f"      - Rol: {admin_user.rol}")
                print(f"      - Password: admin123 (CAMBIAR EN PRODUCCIÓN)")
        
        except Exception as e:
            print(f"   ❌ Error creando usuario administrador: {e}")
            db.session.rollback()
            return False
        
        # 3. Verificar estado final
        print("\n📊 Estado final de la base de datos:")
        usuarios_count = Usuario.query.count()
        print(f"   - Usuarios: {usuarios_count}")
        
        if usuarios_count == 1:
            admin = Usuario.query.first()
            print(f"   - Admin: {admin.username} ({admin.email})")
        
        print("\n✅ Base de datos preparada para producción.")
        print("\n⚠️  IMPORTANTE:")
        print("   1. Cambiar la contraseña del administrador en producción")
        print("   2. Configurar variables de entorno de producción")
        print("   3. Verificar configuración de seguridad")
        
        return True

if __name__ == "__main__":
    try:
        success = prepare_production_database()
        if success:
            print("\n🎉 Preparación completada exitosamente.")
        else:
            print("\n❌ Error en la preparación.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error preparando base de datos para producción: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)