#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Configurar variables de entorno para producción
os.environ['SECRET_KEY'] = 'gmao-production-clean-key-temp-2025'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from sqlalchemy import text

def clean_production_database_direct():
    """Limpiar directamente todas las tablas de la base de datos de producción"""
    
    print("=== LIMPIEZA DIRECTA DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    try:
        # Crear la aplicación
        print("🏗️ Conectando a la aplicación de producción...")
        app = create_app()
        
        with app.app_context():
            print("🗄️ Limpiando base de datos de producción directamente...\n")
            
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
                return True
            
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
            from app.models.usuario import Usuario
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
                print("\n✅ BASE DE DATOS COMPLETAMENTE LIMPIA")
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
        print("🚨 ADVERTENCIA: Este script eliminará TODAS las tablas de la base de datos de producción")
        print("🔄 Presiona Ctrl+C para cancelar o Enter para continuar...")
        input()
        
        success = clean_production_database_direct()
        if success:
            print("\n🎉 LIMPIEZA COMPLETADA EXITOSAMENTE")
            print("\n🌐 Base de datos de producción completamente limpia:")
            print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
            print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
            print("\n🔐 Credenciales únicas de administrador:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente")
        else:
            print("\n❌ Error en la limpieza.")
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()