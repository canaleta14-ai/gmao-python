#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Configurar variables de entorno para FORZAR conexión a PostgreSQL de producción
os.environ['SECRET_KEY'] = 'gmao-production-clean-postgres-temp-2025'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'
os.environ['FLASK_ENV'] = 'production'
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_USER'] = 'gmao-user'
os.environ['DB_NAME'] = 'gmao'
os.environ['DB_HOST'] = '/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres'

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clean_production_postgres():
    """Limpiar la base de datos PostgreSQL de producción"""
    
    print("=== LIMPIEZA DE POSTGRESQL DE PRODUCCIÓN ===\n")
    
    try:
        # Importar después de configurar las variables de entorno
        from app.factory import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        # Crear la aplicación con configuración de producción
        print("🏗️ Conectando a PostgreSQL de producción...")
        app = create_app()
        
        # Verificar que estamos conectados a PostgreSQL
        with app.app_context():
            try:
                # Verificar el tipo de base de datos
                result = db.session.execute(text("SELECT version()"))
                version_info = result.scalar()
                print(f"   📊 Base de datos: {version_info}")
                
                if 'PostgreSQL' not in version_info:
                    print("   ❌ Error: No está conectado a PostgreSQL")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error verificando conexión: {e}")
                return False
            
            print("🗄️ Limpiando base de datos PostgreSQL...\n")
            
            # Obtener todas las tablas
            print("📋 Obteniendo lista de tablas...")
            result = db.session.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"   📊 Tablas encontradas: {len(tables)}")
            print(f"   📋 Lista: {', '.join(tables)}")
            
            if not tables:
                print("   ℹ️ No hay tablas para eliminar")
            else:
                # Desactivar restricciones de clave foránea temporalmente
                print("\n🔓 Desactivando restricciones de clave foránea...")
                db.session.execute(text("SET session_replication_role = replica;"))
                
                # Eliminar todas las tablas
                print("\n🗑️ Eliminando todas las tablas...")
                for table in tables:
                    try:
                        print(f"   🗑️ Eliminando tabla: {table}")
                        db.session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                    except Exception as e:
                        print(f"   ⚠️ Error eliminando tabla {table}: {e}")
                
                # Reactivar restricciones de clave foránea
                print("\n🔒 Reactivando restricciones de clave foránea...")
                db.session.execute(text("SET session_replication_role = DEFAULT;"))
                
                # Confirmar cambios
                db.session.commit()
                
                # Verificar que no quedan tablas
                result = db.session.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """))
                remaining_tables = [row[0] for row in result.fetchall()]
                
                if remaining_tables:
                    print(f"   ⚠️ Aún quedan {len(remaining_tables)} tablas: {', '.join(remaining_tables)}")
                else:
                    print("   ✅ Todas las tablas eliminadas exitosamente")
            
            print("\n🏗️ Recreando estructura de tablas...")
            db.create_all()
            
            print("\n👤 Creando usuario administrador único...")
            from app.models.usuario import Usuario
            from werkzeug.security import generate_password_hash
            
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
            
            # Verificar estado final
            print("\n📊 Verificando estado final...")
            
            # Contar usuarios
            total_users = Usuario.query.count()
            print(f"   👥 Total de usuarios: {total_users}")
            
            # Contar registros en todas las tablas
            result = db.session.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            new_tables = [row[0] for row in result.fetchall()]
            
            total_records = 0
            for table in new_tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    total_records += count
                    if count > 0:
                        print(f"   📋 Tabla {table}: {count} registros")
                except Exception as e:
                    print(f"   ⚠️ Error contando tabla {table}: {e}")
            
            print(f"\n📊 RESUMEN FINAL: {total_records} registros totales")
            
            if total_users == 1 and total_records == 1:
                print("\n✅ BASE DE DATOS POSTGRESQL COMPLETAMENTE LIMPIA")
                print("   Solo contiene el usuario administrador")
                return True
            else:
                print(f"\n❌ Error: Se esperaba 1 usuario y 1 registro total")
                print(f"   Encontrado: {total_users} usuarios, {total_records} registros")
                return False
                
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
        
        success = clean_production_postgres()
        if success:
            print("\n🎉 LIMPIEZA DE POSTGRESQL COMPLETADA EXITOSAMENTE")
            print("\n🌐 Base de datos de producción completamente limpia:")
            print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
            print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
            print("\n🔐 Credenciales únicas de administrador:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente")
        else:
            print("\n❌ Error en la limpieza de PostgreSQL.")
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()