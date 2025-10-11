#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import tempfile
import os

def create_sql_cleanup_script():
    """Crear script SQL para limpiar todas las tablas"""
    
    sql_script = """
-- Script para limpiar completamente la base de datos PostgreSQL
-- Elimina todas las tablas y secuencias

-- Desactivar restricciones de clave foránea temporalmente
SET session_replication_role = replica;

-- Eliminar todas las tablas del esquema public
DO $$ 
DECLARE
    r RECORD;
BEGIN
    -- Eliminar todas las tablas
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
        RAISE NOTICE 'Tabla eliminada: %', r.tablename;
    END LOOP;
    
    -- Eliminar todas las secuencias
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public')
    LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
        RAISE NOTICE 'Secuencia eliminada: %', r.sequence_name;
    END LOOP;
    
    -- Eliminar todas las funciones personalizadas
    FOR r IN (SELECT proname FROM pg_proc WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public'))
    LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS ' || quote_ident(r.proname) || ' CASCADE';
        RAISE NOTICE 'Función eliminada: %', r.proname;
    END LOOP;
END $$;

-- Reactivar restricciones de clave foránea
SET session_replication_role = DEFAULT;

-- Verificar que no quedan tablas
SELECT 'Tablas restantes: ' || COUNT(*) FROM pg_tables WHERE schemaname = 'public';
SELECT 'Secuencias restantes: ' || COUNT(*) FROM information_schema.sequences WHERE sequence_schema = 'public';

-- Mostrar mensaje de confirmación
SELECT 'Base de datos completamente limpia' AS status;
"""
    
    return sql_script

def run_sql_cleanup():
    """Ejecutar limpieza SQL en la base de datos de producción"""
    
    print("=== LIMPIEZA DIRECTA DE TABLAS EN POSTGRESQL ===\n")
    
    # Parámetros de conexión
    instance_connection = "mantenimiento-470311:europe-west1:gmao-postgres"
    database = "gmao"
    user = "gmao-user"
    
    # Crear archivo temporal con el script SQL
    sql_script = create_sql_cleanup_script()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(sql_script)
        sql_file = f.name
    
    try:
        print("🔄 Ejecutando limpieza SQL en la base de datos de producción...")
        print(f"   📊 Instancia: {instance_connection}")
        print(f"   🗄️ Base de datos: {database}")
        print(f"   👤 Usuario: {user}")
        
        # Comando gcloud sql connect con script SQL
        command = [
            "gcloud", "sql", "connect", "gmao-postgres",
            "--user", user,
            "--database", database,
            "--project", "mantenimiento-470311",
            "--quiet"
        ]
        
        print(f"\n🔄 Ejecutando comando: {' '.join(command)}")
        print("📄 Con script SQL de limpieza...")
        
        # Ejecutar el comando con el script SQL como entrada
        with open(sql_file, 'r', encoding='utf-8') as f:
            result = subprocess.run(
                command,
                stdin=f,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
        
        if result.returncode == 0:
            print("✅ Limpieza SQL ejecutada exitosamente")
            if result.stdout.strip():
                print(f"📄 Salida:\n{result.stdout}")
            return True
        else:
            print(f"❌ Error en limpieza SQL (código {result.returncode})")
            if result.stderr.strip():
                print(f"🚨 Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción durante limpieza: {e}")
        return False
        
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(sql_file)
        except:
            pass

def initialize_clean_structure():
    """Inicializar estructura limpia usando Flask-Migrate"""
    
    print("\n=== INICIALIZACIÓN DE ESTRUCTURA LIMPIA ===\n")
    
    # Configurar variables de entorno para producción
    env = os.environ.copy()
    env.update({
        'SECRET_KEY': 'temp-init-key-2025',
        'GOOGLE_CLOUD_PROJECT': 'mantenimiento-470311',
        'FLASK_ENV': 'production',
        'DB_TYPE': 'postgresql',
        'DB_USER': 'gmao-user',
        'DB_NAME': 'gmao',
        'DB_HOST': '/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres'
    })
    
    try:
        print("🔄 Inicializando estructura de base de datos...")
        
        # Usar Flask-Migrate para crear las tablas
        result = subprocess.run(
            ["python", "-c", """
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print('🏗️ Creando estructura de tablas...')
    db.create_all()
    
    print('👤 Creando usuario administrador...')
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
    
    print('✅ Inicialización completada')
    print(f'👥 Total usuarios: {Usuario.query.count()}')
"""],
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ Estructura inicializada exitosamente")
            if result.stdout.strip():
                print(f"📄 Salida:\n{result.stdout}")
            return True
        else:
            print(f"❌ Error en inicialización (código {result.returncode})")
            if result.stderr.strip():
                print(f"🚨 Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción durante inicialización: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🚨 ADVERTENCIA: Este script eliminará TODAS las tablas de la base de datos de producción")
        print("🔄 Presiona Ctrl+C para cancelar o Enter para continuar...")
        input()
        
        # Paso 1: Limpiar todas las tablas
        if run_sql_cleanup():
            print("\n" + "="*60)
            
            # Paso 2: Inicializar estructura limpia
            if initialize_clean_structure():
                print("\n🎉 LIMPIEZA E INICIALIZACIÓN COMPLETADAS EXITOSAMENTE")
                print("\n🌐 Aplicación de producción:")
                print("   URL: https://mantenimiento-470311.ew.r.appspot.com")
                print("   Login: https://mantenimiento-470311.ew.r.appspot.com/login")
                print("\n🔐 Credenciales únicas de administrador:")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                print("\n🚨 IMPORTANTE: Cambiar la contraseña inmediatamente")
            else:
                print("\n❌ Error en la inicialización de la estructura")
        else:
            print("\n❌ Error en la limpieza de tablas")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()