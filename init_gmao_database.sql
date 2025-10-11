-- Script completo para inicializar la base de datos gmao
-- Este script debe ejecutarse conectado como usuario postgres

-- Conectar a la base de datos gmao
\c gmao

-- Crear todas las tablas en la base de datos gmao
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

-- Otorgar todos los permisos al usuario gmao-user
GRANT ALL PRIVILEGES ON DATABASE gmao TO "gmao-user";
GRANT ALL PRIVILEGES ON SCHEMA public TO "gmao-user";
GRANT USAGE ON SCHEMA public TO "gmao-user";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "gmao-user";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "gmao-user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "gmao-user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "gmao-user";

-- Hacer al usuario gmao-user propietario de todas las tablas
ALTER TABLE usuario OWNER TO "gmao-user";
ALTER TABLE activo OWNER TO "gmao-user";
ALTER TABLE plan_mantenimiento OWNER TO "gmao-user";
ALTER TABLE orden_trabajo OWNER TO "gmao-user";
ALTER TABLE inventario OWNER TO "gmao-user";
ALTER TABLE proveedor OWNER TO "gmao-user";
ALTER TABLE categoria OWNER TO "gmao-user";

-- Insertar el usuario administrador
INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
    'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
    'admin', true)
ON CONFLICT (username) DO NOTHING;

-- Verificar la creación
\dt
SELECT * FROM usuario WHERE username = 'admin';

\echo 'Base de datos gmao inicializada correctamente'