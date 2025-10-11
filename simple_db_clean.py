#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import sys
from werkzeug.security import generate_password_hash

def clean_production_database():
    """Limpiar la base de datos de producción usando psycopg2 directamente"""
    
    print("=== LIMPIEZA DIRECTA CON PSYCOPG2 ===\n")
    
    # Parámetros de conexión (usando socket Unix para Cloud SQL)
    connection_params = {
        'host': '/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres',
        'database': 'gmao',
        'user': 'gmao-user',
        'password': '',  # Se obtiene automáticamente en App Engine
    }
    
    try:
        print("🔄 Conectando a PostgreSQL de producción...")
        print(f"   📊 Host: {connection_params['host']}")
        print(f"   🗄️ Base de datos: {connection_params['database']}")
        print(f"   👤 Usuario: {connection_params['user']}")
        
        # Intentar conexión
        conn = psycopg2.connect(**connection_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("   ✅ Conexión establecida exitosamente")
        
        # Verificar que estamos en PostgreSQL
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   📊 Versión: {version[:50]}...")
        
        if 'PostgreSQL' not in version:
            print("   ❌ Error: No está conectado a PostgreSQL")
            return False
        
        print("\n🗄️ Obteniendo lista de tablas...")
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   📋 Tablas encontradas: {len(tables)}")
        if tables:
            print(f"   📄 Lista: {', '.join(tables)}")
        
        if not tables:
            print("   ℹ️ No hay tablas para eliminar")
        else:
            print("\n🗑️ Eliminando todas las tablas...")
            
            # Desactivar restricciones de clave foránea
            print("   🔓 Desactivando restricciones...")
            cursor.execute("SET session_replication_role = replica;")
            
            # Eliminar cada tabla
            for table in tables:
                try:
                    print(f"   🗑️ Eliminando: {table}")
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                except Exception as e:
                    print(f"   ⚠️ Error eliminando {table}: {e}")
            
            # Reactivar restricciones
            print("   🔒 Reactivando restricciones...")
            cursor.execute("SET session_replication_role = DEFAULT;")
            
            print("   ✅ Todas las tablas eliminadas")
        
        # Verificar que no quedan tablas
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        remaining_tables = [row[0] for row in cursor.fetchall()]
        
        if remaining_tables:
            print(f"   ⚠️ Aún quedan {len(remaining_tables)} tablas: {', '.join(remaining_tables)}")
        else:
            print("   ✅ Base de datos completamente limpia")
        
        print("\n🏗️ Creando estructura básica de tablas...")
        
        # Crear tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                rol VARCHAR(50) NOT NULL DEFAULT 'Usuario',
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP
            );
        """)
        
        print("   ✅ Tabla de usuarios creada")
        
        print("\n👤 Creando usuario administrador único...")
        
        # Verificar que no hay usuarios
        cursor.execute("SELECT COUNT(*) FROM usuario")
        existing_users = cursor.fetchone()[0]
        
        if existing_users > 0:
            print(f"   ⚠️ Advertencia: Ya existen {existing_users} usuarios")
            cursor.execute("DELETE FROM usuario")
            print("   🗑️ Usuarios existentes eliminados")
        
        # Crear usuario admin
        password_hash = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO usuario (username, email, password, nombre, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('admin', 'admin@gmao.com', password_hash, 'Administrador Sistema', 'Administrador', True))
        
        print("   ✅ Usuario administrador creado")
        
        # Verificación final
        print("\n📊 Verificación final...")
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_users = cursor.fetchone()[0]
        print(f"   👥 Total usuarios: {total_users}")
        
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        final_tables = [row[0] for row in cursor.fetchall()]
        print(f"   📋 Tablas finales: {len(final_tables)}")
        
        if total_users == 1:
            print("\n✅ BASE DE DATOS COMPLETAMENTE LIMPIA Y LISTA")
            return True
        else:
            print(f"\n⚠️ Advertencia: Se esperaba 1 usuario, encontrado: {total_users}")
            return False
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            print("🔌 Conexión cerrada")
        except:
            pass

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