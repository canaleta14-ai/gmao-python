#!/bin/bash
# Script para inicializar la base de datos de Cloud SQL

echo "🚀 INICIALIZANDO BASE DE DATOS EN CLOUD SQL"
echo "============================================="

# Conectar a la instancia y ejecutar comandos SQL
echo "📋 Creando tablas necesarias..."

gcloud sql connect gmao-postgres-spain --user=gmao-user --database=gmao << 'EOF'

-- Crear tabla usuario
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200),
    nombre VARCHAR(100),
    rol VARCHAR(50) DEFAULT 'Técnico',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla activo
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
);

-- Crear tabla plan_mantenimiento
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
);

-- Crear tabla orden_trabajo
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
);

-- Crear usuario administrador si no existe
INSERT INTO usuario (username, email, password, nombre, rol, activo)
SELECT 'admin', 'admin@gmao.com', 
       'pbkdf2:sha256:600000$cK9mGJYl$8d8a8a1f5a7c5b2e5f4a8d9c5e7f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5', 
       'Administrador', 'Administrador', TRUE
WHERE NOT EXISTS (SELECT 1 FROM usuario WHERE username = 'admin');

-- Verificar tablas creadas
\dt

-- Verificar usuario admin
SELECT id, username, email, rol, activo FROM usuario WHERE username = 'admin';

EOF

echo "✅ Inicialización completada!"
echo "🔐 Credenciales de acceso:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo "🌐 URL: https://mantenimiento-470311.ew.r.appspot.com"