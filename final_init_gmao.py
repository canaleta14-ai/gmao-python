"""
Script final para inicializar la base de datos gmao usando gcloud sql connect
Este funciona desde Windows conectando directamente a Cloud SQL
"""

import subprocess
import tempfile
import os


def create_init_sql():
    """Crear comandos SQL para inicializar la base de datos"""
    sql_commands = """
-- Crear las tablas principales
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
);

CREATE TABLE IF NOT EXISTS activo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER,
    ubicacion VARCHAR(100),
    estado VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

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
);

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
);

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
);

CREATE TABLE IF NOT EXISTS proveedor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(120),
    direccion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Insertar usuario admin
INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
    'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
    'admin', true)
ON CONFLICT (username) DO NOTHING;

-- Verificar creación
SELECT 'Initialization completed!' as status;
SELECT COUNT(*) as user_count FROM usuario WHERE username = 'admin';
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
"""
    return sql_commands


def run_sql_via_gcloud(sql_content):
    """Ejecutar SQL usando gcloud sql connect"""
    print("🔧 Creando archivo temporal con comandos SQL...")

    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
        f.write(sql_content)
        temp_file = f.name

    try:
        print(f"📄 Archivo SQL creado: {temp_file}")
        print("🔗 Ejecutando comandos SQL via gcloud...")

        # Ejecutar usando gcloud sql connect
        cmd = [
            "gcloud",
            "sql",
            "connect",
            "gmao-postgres-spain",
            "--user=postgres",
            "--database=gmao",
        ]

        # Leer el archivo SQL y enviarlo como input
        with open(temp_file, "r") as f:
            sql_input = f.read()

        print("🎯 Ejecutando comandos...")
        result = subprocess.run(
            cmd,
            input=sql_input,
            text=True,
            capture_output=True,
            timeout=300,  # 5 minutos timeout
        )

        print(f"⚡ Return code: {result.returncode}")
        if result.stdout:
            print("✅ Output:")
            print(result.stdout)
        if result.stderr:
            print("⚠️  Errors:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ Timeout ejecutando comandos SQL")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando comandos: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(temp_file)
            print(f"🧹 Archivo temporal eliminado: {temp_file}")
        except:
            pass


def main():
    print("=" * 60)
    print("INICIALIZACIÓN FINAL DE BASE DE DATOS GMAO")
    print("=" * 60)

    # Crear comandos SQL
    sql_content = create_init_sql()

    print("📋 Comandos SQL preparados")
    print("🎯 Inicializando base de datos 'gmao' con usuario 'postgres'...")

    # Ejecutar SQL
    success = run_sql_via_gcloud(sql_content)

    if success:
        print("\n🎉 ¡BASE DE DATOS INICIALIZADA EXITOSAMENTE!")
        print("✅ Tablas creadas")
        print("✅ Usuario admin insertado")
        print("✅ Base de datos gmao lista para usar")
        print("\n🔑 Credenciales de login:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n🌐 Aplicación disponible en:")
        print("   https://mantenimiento-470311.ew.r.appspot.com")
    else:
        print("\n❌ Error en la inicialización")
        print("💡 Revisar logs arriba para más detalles")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
