#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def clean_production_database():
    """Limpiar la base de datos de producción usando Flask directamente"""
    
    print("=== LIMPIEZA FINAL DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    # Configurar variables de entorno para FORZAR PostgreSQL
    os.environ['SECRET_KEY'] = 'temp-clean-key-2025-production-database-cleanup-script-very-long-secret-key'
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_USER'] = 'gmao-user'
    os.environ['DB_NAME'] = 'gmao'
    os.environ['DB_HOST'] = '/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres'
    
    # Agregar directorio actual al path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        print("🔄 Importando módulos de Flask...")
        from app.factory import create_app
        from app.extensions import db
        from sqlalchemy import text, inspect
        
        print("🏗️ Creando aplicación Flask...")
        app = create_app()
        
        with app.app_context():
            print("🔍 Verificando conexión a base de datos...")
            
            # Verificar que estamos conectados a PostgreSQL
            try:
                result = db.session.execute(text("SELECT version()"))
                version_info = result.scalar()
                print(f"   📊 Conectado a: {version_info[:50]}...")
                
                if 'PostgreSQL' not in version_info:
                    print("   ❌ Error: No está conectado a PostgreSQL")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error verificando conexión: {e}")
                return False
            
            print("🗄️ Obteniendo lista de tablas existentes...")
            
            # Usar inspector para obtener tablas
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"   📋 Tablas encontradas: {len(tables)}")
            if tables:
                print(f"   📄 Lista: {', '.join(tables)}")
            
            if not tables:
                print("   ℹ️ No hay tablas para eliminar")
            else:
                print("\n🗑️ Eliminando todas las tablas...")
                
                # Desactivar restricciones de clave foránea
                print("   🔓 Desactivando restricciones...")
                db.session.execute(text("SET session_replication_role = replica;"))
                
                # Eliminar cada tabla
                for table in tables:
                    try:
                        print(f"   🗑️ Eliminando: {table}")
                        db.session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                    except Exception as e:
                        print(f"   ⚠️ Error eliminando {table}: {e}")
                
                # Reactivar restricciones
                print("   🔒 Reactivando restricciones...")
                db.session.execute(text("SET session_replication_role = DEFAULT;"))
                
                # Confirmar cambios
                db.session.commit()
                print("   ✅ Todas las tablas eliminadas")
            
            print("\n🏗️ Recreando estructura de tablas...")
            db.create_all()
            
            # Verificar tablas creadas
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            print(f"   📋 Tablas creadas: {len(new_tables)}")
            print(f"   📄 Lista: {', '.join(new_tables)}")
            
            print("\n👤 Creando usuario administrador único...")
            from app.models.usuario import Usuario
            from werkzeug.security import generate_password_hash
            
            # Verificar que no hay usuarios
            existing_users = Usuario.query.count()
            if existing_users > 0:
                print(f"   ⚠️ Advertencia: Ya existen {existing_users} usuarios")
                # Eliminar todos los usuarios existentes
                Usuario.query.delete()
                db.session.commit()
                print("   🗑️ Usuarios existentes eliminados")
            
            # Crear nuevo usuario admin
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
            
            print("   ✅ Usuario administrador creado")
            
            # Verificación final
            print("\n📊 Verificación final...")
            total_users = Usuario.query.count()
            print(f"   👥 Total usuarios: {total_users}")
            
            # Contar registros en todas las tablas
            total_records = 0
            for table in new_tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    total_records += count
                    if count > 0:
                        print(f"   📋 {table}: {count} registros")
                except Exception as e:
                    print(f"   ⚠️ Error contando {table}: {e}")
            
            print(f"\n📊 RESUMEN: {total_records} registros totales en {len(new_tables)} tablas")
            
            if total_users == 1 and total_records == 1:
                print("\n✅ BASE DE DATOS COMPLETAMENTE LIMPIA Y LISTA")
                return True
            else:
                print(f"\n⚠️ Advertencia: Se esperaba 1 usuario y 1 registro")
                print(f"   Encontrado: {total_users} usuarios, {total_records} registros")
                return total_users == 1  # Aceptar si al menos hay 1 usuario admin
                
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("🚨 ADVERTENCIA: Este script eliminará TODAS las tablas de PostgreSQL de producción")
        print("🔄 Presiona Ctrl+C para cancelar o Enter para continuar...")
        input()
        
        success = clean_production_database()
        
        if success:
            print("\n🎉 LIMPIEZA DE PRODUCCIÓN COMPLETADA EXITOSAMENTE")
            print("\n🌐 Aplicación de producción completamente limpia:")
            print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
            print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
            print("\n🔐 Credenciales únicas de administrador:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("\n🚨 IMPORTANTE:")
            print("   1. Cambiar la contraseña inmediatamente")
            print("   2. Verificar que la aplicación funciona correctamente")
            print("   3. Crear usuarios adicionales según sea necesario")
        else:
            print("\n❌ Error en la limpieza de la base de datos de producción")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()