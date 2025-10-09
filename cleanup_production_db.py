#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Configurar variables de entorno para producción
os.environ['SECRET_KEY'] = 'gmao-production-cleanup-key-temp-2025'  # Clave temporal para limpieza
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

def cleanup_production_database():
    """Limpiar completamente la base de datos de producción"""
    
    print("=== LIMPIEZA COMPLETA DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    try:
        # Crear la aplicación
        print("🏗️ Conectando a la aplicación de producción...")
        app = create_app()
        
        with app.app_context():
            print("🗄️ Limpiando base de datos de producción...")
            
            # Mostrar estado actual
            print("\n📊 Estado actual de la base de datos:")
            try:
                usuarios_count = Usuario.query.count()
                print(f"   👥 Usuarios actuales: {usuarios_count}")
                
                # Mostrar algunos usuarios existentes
                usuarios = Usuario.query.limit(5).all()
                for user in usuarios:
                    print(f"   - {user.username} ({user.email}) - {user.rol}")
                    
            except Exception as e:
                print(f"   ⚠️ Error consultando estado actual: {e}")
            
            # Confirmar limpieza
            print("\n🧹 INICIANDO LIMPIEZA COMPLETA...")
            print("   ⚠️ ADVERTENCIA: Esto eliminará TODOS los datos existentes")
            
            # Eliminar todas las tablas existentes
            print("   🗑️ Eliminando todas las tablas...")
            db.drop_all()
            
            # Crear todas las tablas nuevamente
            print("   🏗️ Recreando estructura de tablas...")
            db.create_all()
            
            # Crear usuario administrador limpio
            print("\n👤 Creando usuario administrador limpio...")
            
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
            
            # Verificar el estado final
            print("\n📊 Estado final de la base de datos:")
            usuarios_count = Usuario.query.count()
            print(f"   👥 Total de usuarios: {usuarios_count}")
            
            if usuarios_count == 1:
                admin = Usuario.query.filter_by(username='admin').first()
                if admin:
                    print(f"   ✅ Usuario admin: {admin.email}")
                    print(f"   👤 Nombre: {admin.nombre}")
                    print(f"   🔑 Rol: {admin.rol}")
                    print(f"   🟢 Activo: {admin.activo}")
                else:
                    print("   ❌ Error: Usuario admin no encontrado")
                    return False
            else:
                print(f"   ❌ Error: Se esperaba 1 usuario, pero hay {usuarios_count}")
                return False
            
            print("\n✅ LIMPIEZA DE BASE DE DATOS COMPLETADA EXITOSAMENTE")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🌐 Base de datos de producción limpia y lista:")
    print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
    print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
    print("\n🔐 Credenciales únicas de administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente")
    print("🎯 La base de datos ahora está completamente limpia y lista para uso en producción")
    
    return True

if __name__ == "__main__":
    try:
        print("🚨 ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos de producción")
        print("🔄 Presiona Ctrl+C para cancelar o Enter para continuar...")
        input()
        
        success = cleanup_production_database()
        if success:
            print("\n🎉 Limpieza completada exitosamente.")
        else:
            print("\n❌ Error en la limpieza.")
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()