#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_to_production():
    """Migrar base de datos limpia a producción"""
    print("=== MIGRACIÓN A PRODUCCIÓN ===\n")
    
    print("🔧 Configurando variables de entorno para producción...")
    
    # Configurar variables de entorno para producción
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:admin123@/mantenimiento?host=/cloudsql/mantenimiento-470311:europe-west1:mantenimiento-db'
    
    print("   ✅ Variables de entorno configuradas")
    
    # Importar después de configurar las variables de entorno
    from app.factory import create_app
    from app.extensions import db
    from app.models.usuario import Usuario
    
    app = create_app()
    
    with app.app_context():
        print("\n🗄️ Conectando a base de datos de producción...")
        
        try:
            # Verificar conexión
            db.engine.execute('SELECT 1')
            print("   ✅ Conexión a base de datos establecida")
        except Exception as e:
            print(f"   ❌ Error conectando a base de datos: {e}")
            return False
        
        print("\n🧹 Limpiando base de datos de producción...")
        try:
            # Limpiar y recrear todas las tablas
            db.drop_all()
            db.create_all()
            print("   ✅ Base de datos de producción limpiada y recreada")
        except Exception as e:
            print(f"   ❌ Error limpiando base de datos: {e}")
            return False
        
        print("\n👤 Creando usuario administrador en producción...")
        try:
            # Crear usuario administrador
            admin_user = Usuario(
                username='admin',
                email='admin@gmao.com',
                nombre='Administrador Sistema',
                rol='Administrador',
                activo=True
            )
            admin_user.set_password('admin123')  # Cambiar inmediatamente en producción
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"   ✅ Usuario administrador creado en producción:")
            print(f"      - Username: {admin_user.username}")
            print(f"      - Email: {admin_user.email}")
            print(f"      - Rol: {admin_user.rol}")
            
        except Exception as e:
            print(f"   ❌ Error creando usuario administrador: {e}")
            db.session.rollback()
            return False
        
        print("\n📊 Verificando estado de la base de datos de producción...")
        usuarios_count = Usuario.query.count()
        print(f"   - Usuarios en producción: {usuarios_count}")
        
        if usuarios_count == 1:
            admin = Usuario.query.first()
            print(f"   - Admin: {admin.username} ({admin.email})")
        
        print("\n✅ Migración a producción completada exitosamente.")
        print("\n🚨 ACCIONES REQUERIDAS INMEDIATAMENTE:")
        print("   1. Cambiar contraseña del administrador")
        print("   2. Configurar SECRET_KEY de producción")
        print("   3. Verificar configuración de seguridad")
        print("   4. Probar funcionalidad en producción")
        
        return True

if __name__ == "__main__":
    try:
        success = migrate_to_production()
        if success:
            print("\n🎉 Migración completada exitosamente.")
            print("\n🌐 Aplicación disponible en:")
            print("   https://mantenimiento-470311.ew.r.appspot.com")
        else:
            print("\n❌ Error en la migración.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error migrando a producción: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)