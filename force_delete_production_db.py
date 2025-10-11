#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

# Configurar variables de entorno para producción
os.environ['SECRET_KEY'] = 'gmao-production-delete-key-temp-2025'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'mantenimiento-470311'

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from sqlalchemy import text

def force_delete_production_database():
    """Forzar la eliminación completa de la base de datos de producción"""
    
    print("=== ELIMINACIÓN FORZADA DE BASE DE DATOS DE PRODUCCIÓN ===\n")
    
    try:
        # Crear la aplicación para conectar a la BD
        print("🏗️ Conectando a la aplicación de producción...")
        app = create_app()
        
        with app.app_context():
            print("🔌 Terminando todas las conexiones activas...")
            
            try:
                # Terminar todas las conexiones activas a la base de datos gmao
                result = db.session.execute(text("""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = 'gmao' AND pid <> pg_backend_pid()
                """))
                
                terminated_connections = result.fetchall()
                print(f"   ✅ Terminadas {len(terminated_connections)} conexiones activas")
                
            except Exception as e:
                print(f"   ⚠️ Error terminando conexiones: {e}")
                print("   🔄 Continuando con la eliminación...")
            
            # Cerrar la conexión actual
            db.session.close()
            db.engine.dispose()
            
        print("🗑️ Eliminando base de datos de producción...")
        
        # Intentar eliminar la base de datos usando gcloud
        try:
            result = subprocess.run([
                'gcloud', 'sql', 'databases', 'delete', 'gmao',
                '--instance=gmao-postgres',
                '--quiet'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("   ✅ Base de datos eliminada exitosamente")
                return True
            else:
                print(f"   ❌ Error eliminando BD: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout eliminando base de datos")
            return False
        except Exception as e:
            print(f"   ❌ Error ejecutando gcloud: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la eliminación: {e}")
        import traceback
        traceback.print_exc()
        return False

def recreate_clean_database():
    """Recrear la base de datos completamente limpia"""
    
    print("\n=== RECREANDO BASE DE DATOS LIMPIA ===\n")
    
    try:
        print("🏗️ Creando nueva base de datos gmao...")
        
        # Crear la nueva base de datos
        result = subprocess.run([
            'gcloud', 'sql', 'databases', 'create', 'gmao',
            '--instance=gmao-postgres',
            '--charset=UTF8',
            '--collation=en_US.UTF8'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ Nueva base de datos creada exitosamente")
            
            # Esperar un momento para que la BD esté lista
            print("   ⏳ Esperando que la base de datos esté lista...")
            time.sleep(5)
            
            return True
        else:
            print(f"   ❌ Error creando BD: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error recreando base de datos: {e}")
        return False

def initialize_clean_database():
    """Inicializar la base de datos limpia con solo el usuario admin"""
    
    print("\n=== INICIALIZANDO BASE DE DATOS LIMPIA ===\n")
    
    try:
        # Crear la aplicación con la nueva BD
        print("🏗️ Conectando a la nueva base de datos...")
        app = create_app()
        
        with app.app_context():
            print("📋 Creando estructura de tablas...")
            db.create_all()
            
            print("👤 Creando usuario administrador...")
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
            
            # Verificar que solo hay 1 registro
            total_users = Usuario.query.count()
            print(f"   📊 Total de usuarios: {total_users}")
            
            if total_users == 1:
                print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
                return True
            else:
                print(f"❌ Error: Se esperaba 1 usuario, pero hay {total_users}")
                return False
                
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("🚨 ADVERTENCIA: Este proceso eliminará COMPLETAMENTE la base de datos de producción")
        print("🔄 Presiona Ctrl+C para cancelar o Enter para continuar...")
        input()
        
        # Paso 1: Eliminar base de datos actual
        if force_delete_production_database():
            print("\n✅ Base de datos eliminada exitosamente")
            
            # Paso 2: Recrear base de datos limpia
            if recreate_clean_database():
                print("\n✅ Base de datos recreada exitosamente")
                
                # Paso 3: Inicializar con datos limpios
                if initialize_clean_database():
                    print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
                    print("\n🌐 Base de datos de producción completamente limpia:")
                    print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
                    print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
                    print("\n🔐 Credenciales únicas de administrador:")
                    print("   Usuario: admin")
                    print("   Contraseña: admin123")
                    print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente")
                else:
                    print("\n❌ Error en la inicialización")
            else:
                print("\n❌ Error recreando la base de datos")
        else:
            print("\n❌ Error eliminando la base de datos")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()