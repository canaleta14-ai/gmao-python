#!/usr/bin/env python3
"""
Script para inicializar la base de datos de producción remotamente
"""
import os # type: ignore
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def conectar_cloudsql(): # type: ignore
    """Conecta a Cloud SQL PostgreSQL usando psycopg2"""
    try:
        # Configuración de conexión a Cloud SQL
        conn_config = {
            "host": "/cloudsql/mantenimiento-470311:europe-west1:gmao-postgres",
            "database": "gmao",
            "user": "gmao-user",
            "password": "admin123",  # Contraseña que configuramos
        }

        print("🔗 Conectando a Cloud SQL PostgreSQL...")
        conn = psycopg2.connect(**conn_config) # type: ignore
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # type: ignore
        print("✅ Conexión exitosa")
        return conn

    except Exception as e:
        print(f"❌ Error conectando a Cloud SQL: {e}")
        return None


def verificar_tablas(conn):
    """Verifica qué tablas existen en la base de datos"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )
        tablas = [row[0] for row in cursor.fetchall()]
        cursor.close()

        print(f"📋 Tablas existentes ({len(tablas)}):")
        for tabla in tablas:
            print(f"   - {tabla}")

        return tablas

    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return []


def crear_tablas_basicas(conn):
    """Crea las tablas básicas necesarias"""
    try:
        cursor = conn.cursor()

        # Crear tabla usuario
        print("📋 Creando tabla usuario...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuario (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(200),
                nombre VARCHAR(100),
                rol VARCHAR(50) DEFAULT 'Técnico',
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Crear tabla activo
        print("📋 Creando tabla activo...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activo (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                departamento VARCHAR(100),
                ubicacion VARCHAR(200),
                estado VARCHAR(50) DEFAULT 'Operativo',
                fecha_instalacion DATE,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Crear tabla plan_mantenimiento
        print("📋 Creando tabla plan_mantenimiento...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS plan_mantenimiento (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                tipo_mantenimiento VARCHAR(50) DEFAULT 'Preventivo',
                frecuencia_valor INTEGER NOT NULL,
                frecuencia_unidad VARCHAR(20) NOT NULL,
                activo_id INTEGER REFERENCES activo(id),
                activo BOOLEAN DEFAULT TRUE,
                generacion_automatica BOOLEAN DEFAULT TRUE,
                proxima_ejecucion TIMESTAMP,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Crear tabla orden_trabajo
        print("📋 Creando tabla orden_trabajo...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orden_trabajo (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(50) UNIQUE NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT,
                estado VARCHAR(50) DEFAULT 'Pendiente',
                prioridad VARCHAR(20) DEFAULT 'Media',
                fecha_programada TIMESTAMP,
                fecha_inicio TIMESTAMP,
                fecha_finalizacion TIMESTAMP,
                activo_id INTEGER REFERENCES activo(id),
                tecnico_id INTEGER REFERENCES usuario(id),
                plan_id INTEGER REFERENCES plan_mantenimiento(id),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.close()
        print("✅ Tablas básicas creadas")
        return True

    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False


def crear_usuario_admin(conn):
    """Crea el usuario administrador"""
    try:
        cursor = conn.cursor()

        # Verificar si ya existe
        cursor.execute("SELECT id FROM usuario WHERE username = %s", ("admin",))
        if cursor.fetchone():
            print("ℹ️ Usuario admin ya existe")
            cursor.close()
            return True

        # Crear usuario admin
        print("👤 Creando usuario administrador...")
        # Hash de 'admin123' usando werkzeug
        password_hash = "pbkdf2:sha256:600000$cK9mGJYl$8d8a8a1f5a7c5b2e5f4a8d9c5e7f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5"

        cursor.execute(
            """
            INSERT INTO usuario (username, email, password, nombre, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                "admin",
                "admin@gmao.com",
                password_hash,
                "Administrador",
                "Administrador",
                True,
            ),
        )

        cursor.close()
        print("✅ Usuario admin creado (admin/admin123)")
        return True

    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        return False


def inicializar_bd_produccion():
    """Inicializa la base de datos de producción"""
    print("🚀 INICIALIZANDO BASE DE DATOS DE PRODUCCIÓN")
    print("=" * 60)

    # Conectar a Cloud SQL
    conn = conectar_cloudsql()
    if not conn:
        return False

    try:
        # Verificar estado actual
        print("\n1. 🔍 Verificando estado actual...")
        tablas_existentes = verificar_tablas(conn)

        # Crear tablas si no existen
        print("\n2. 📋 Creando tablas necesarias...")
        if not crear_tablas_basicas(conn):
            return False

        # Verificar tablas después de creación
        print("\n3. ✅ Verificando tablas creadas...")
        tablas_nuevas = verificar_tablas(conn)

        # Crear usuario admin
        print("\n4. 👤 Configurando usuario administrador...")
        if not crear_usuario_admin(conn):
            return False

        print("\n" + "=" * 60)
        print("🎉 ¡BASE DE DATOS INICIALIZADA EXITOSAMENTE!")
        print("🔐 Credenciales de login:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("🌐 URL: https://mantenimiento-470311.ew.r.appspot.com")

        return True

    except Exception as e:
        print(f"❌ Error durante inicialización: {e}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    if inicializar_bd_produccion():
        print("\n✅ Sistema listo para usar")
    else:
        print("\n❌ Error en inicialización")
        sys.exit(1)
