#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Configurar variables de entorno para producción
os.environ['SECRET_KEY'] = 'gmao-production-init-key-temp-2025'  # Clave temporal para inicialización
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

def init_production_database():
    """Inicializar base de datos de producción directamente"""
    
    print("=== INICIALIZACIÓN SIMPLE DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    try:
        # Crear la aplicación
        print("🏗️ Creando aplicación...")
        app = create_app()
        
        with app.app_context():
            print("🗄️ Inicializando base de datos...")
            
            # Eliminar todas las tablas existentes
            print("   🧹 Eliminando tablas existentes...")
            db.drop_all()
            
            # Crear todas las tablas
            print("   🏗️ Creando nuevas tablas...")
            db.create_all()
            
            # Crear usuario administrador
            print("👤 Creando usuario administrador...")
            
            # Crear nuevo usuario administrador
            admin_user = Usuario(
                username='admin',
                email='admin@gmao.com',
                password=generate_password_hash('admin123'),
                nombre='Administrador Sistema',
                rol='Administrador',
                activo=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("   ✅ Usuario administrador creado exitosamente")
            
            # Verificar la creación
            print("\n📊 Verificando estado de la base de datos...")
            usuarios_count = Usuario.query.count()
            print(f"   👥 Usuarios en la base de datos: {usuarios_count}")
            
            if usuarios_count > 0:
                admin = Usuario.query.filter_by(username='admin').first()
                if admin:
                    print(f"   ✅ Usuario admin encontrado: {admin.email}")
                    print(f"   📧 Email: {admin.email}")
                    print(f"   👤 Nombre: {admin.nombre}")
                    print(f"   🔑 Rol: {admin.rol}")
                else:
                    print("   ❌ Usuario admin no encontrado")
            
            print("\n✅ Inicialización de base de datos completada exitosamente")
            
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🌐 Aplicación disponible en:")
    print("   https://mantenimiento-470311.ew.r.appspot.com")
    print("   https://mantenimiento-470311.ew.r.appspot.com/login")
    print("\n🔐 Credenciales de administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente después del primer login")
    
    return True

if __name__ == "__main__":
    try:
        success = init_production_database()
        if success:
            print("\n🎉 Inicialización completada exitosamente.")
        else:
            print("\n❌ Error en la inicialización.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()