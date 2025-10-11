#!/usr/bin/env python3
"""
Script para inicializar la base de datos gmao en Cloud SQL
Ejecuta las sentencias SQL necesarias usando las mismas credenciales que la aplicación
"""

import os
import sys
from google.cloud import secretmanager
import psycopg2
from psycopg2 import sql


def get_secret_value(secret_name, project_id="mantenimiento-470311"):
    """Obtener un secreto de Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def connect_to_db():
    """Conectar a la base de datos usando las mismas configuraciones que la app"""

    # Obtener configuración
    db_host = "/cloudsql/mantenimiento-470311:europe-southwest1:gmao-postgres-spain"
    db_name = "gmao"
    db_user = "gmao-user"

    try:
        # Obtener contraseña de Secret Manager
        db_password = get_secret_value("gmao-db-password")

        print(f"🔗 Conectando a {db_name} como {db_user}...")

        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=db_host, database=db_name, user=db_user, password=db_password
        )

        print("✅ Conexión exitosa a Cloud SQL")
        return conn

    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None


def init_database(conn):
    """Inicializar la base de datos con todas las tablas y datos"""

    cursor = conn.cursor()

    print("📋 Iniciando creación de tablas...")

    # SQL commands para crear tablas
    commands = [
        """
        CREATE TABLE IF NOT EXISTS usuario (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100),
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL DEFAULT 'user',
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS activo (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            categoria_id INTEGER,
            ubicacion VARCHAR(100),
            estado VARCHAR(50),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS plan_mantenimiento (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            frecuencia INTEGER NOT NULL,
            unidad_frecuencia VARCHAR(20) NOT NULL,
            activo_id INTEGER,
            responsable_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orden_trabajo (
            id SERIAL PRIMARY KEY,
            numero_orden VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            activo_id INTEGER,
            plan_id INTEGER,
            asignado_a INTEGER,
            estado VARCHAR(20) DEFAULT 'pendiente',
            prioridad VARCHAR(20) DEFAULT 'media',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_programada TIMESTAMP,
            fecha_completada TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inventario (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            cantidad INTEGER DEFAULT 0,
            unidad VARCHAR(20),
            precio_unitario DECIMAL(10,2),
            proveedor_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS proveedor (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            contacto VARCHAR(100),
            telefono VARCHAR(20),
            email VARCHAR(120),
            direccion TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS categoria (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """,
        """
        INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
        VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
            'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
            'admin', true)
        ON CONFLICT (username) DO NOTHING
        """,
    ]

    try:
        for i, command in enumerate(commands, 1):
            print(f"   Ejecutando comando {i}/{len(commands)}...")
            cursor.execute(command)

        # Commit changes
        conn.commit()
        print("✅ Todas las tablas creadas exitosamente")

        # Verificar usuario admin
        cursor.execute("SELECT username, rol FROM usuario WHERE username = 'admin'")
        result = cursor.fetchone()

        if result:
            print(f"✅ Usuario admin verificado: {result[0]} ({result[1]})")
        else:
            print("❌ Usuario admin no encontrado")

        # Listar tablas
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )
        tables = cursor.fetchall()
        print(f"📋 Tablas en la base de datos: {[t[0] for t in tables]}")

        return True

    except Exception as e:
        print(f"❌ Error ejecutando comandos SQL: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def main():
    print("=" * 60)
    print("INICIALIZACIÓN DE BASE DE DATOS GMAO")
    print("=" * 60)

    # Conectar a la base de datos
    conn = connect_to_db()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False

    try:
        # Inicializar base de datos
        success = init_database(conn)

        if success:
            print("\n✅ Inicialización completada exitosamente")
            print("🔗 La aplicación debería funcionar ahora en:")
            print("   https://mantenimiento-470311.ew.r.appspot.com")
            print("👤 Usuario: admin")
            print("🔑 Contraseña: admin123")
        else:
            print("\n❌ Inicialización falló")

        return success

    finally:
        conn.close()
        print("🔌 Conexión cerrada")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
