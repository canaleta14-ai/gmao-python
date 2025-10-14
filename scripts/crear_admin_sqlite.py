import os
import sqlite3
from werkzeug.security import generate_password_hash

# Ruta de la base de datos SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), "../instance/database.db")

# Datos del usuario admin
username = "admin"
email = "admin@gmao.com"
password = "admin"
nombre = "Administrador"
rol = "Administrador"
activo = True

hashed_password = generate_password_hash(password)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Crear todas las tablas principales si no existen

# Tabla usuario
c.execute("""
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    nombre TEXT,
    rol TEXT DEFAULT 'Técnico',
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla activo
c.execute("""
CREATE TABLE IF NOT EXISTS activo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    ubicacion TEXT,
    categoria_id INTEGER,
    proveedor_id INTEGER
)
""")

# Tabla solicitud_servicio
c.execute("""
CREATE TABLE IF NOT EXISTS solicitud_servicio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_solicitud TEXT UNIQUE NOT NULL,
    fecha_creacion DATETIME,
    fecha_actualizacion DATETIME,
    nombre_solicitante TEXT NOT NULL,
    email_solicitante TEXT NOT NULL,
    telefono_solicitante TEXT,
    empresa_solicitante TEXT,
    tipo_servicio TEXT NOT NULL,
    prioridad TEXT DEFAULT 'normal',
    estado TEXT DEFAULT 'pendiente',
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    ubicacion TEXT,
    activo_afectado TEXT,
    costo_estimado REAL,
    tiempo_estimado TEXT,
    observaciones_internas TEXT,
    activo_id INTEGER,
    asignado_a_id INTEGER
)
""")

# Tabla orden_trabajo
c.execute("""
CREATE TABLE IF NOT EXISTS orden_trabajo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT,
    fecha_creacion DATETIME,
    estado TEXT,
    activo_id INTEGER,
    usuario_id INTEGER
)
""")

# Tabla plan_mantenimiento
c.execute("""
CREATE TABLE IF NOT EXISTS plan_mantenimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    descripcion TEXT,
    activo_id INTEGER
)
""")

# Tabla proveedor
c.execute("""
CREATE TABLE IF NOT EXISTS proveedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    contacto TEXT,
    telefono TEXT,
    email TEXT
)
""")

# Tabla categoria
c.execute("""
CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    descripcion TEXT
)
""")

# Tabla manual
c.execute("""
CREATE TABLE IF NOT EXISTS manual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    archivo TEXT,
    activo_id INTEGER
)
""")

# Tabla movimiento_inventario
c.execute("""
CREATE TABLE IF NOT EXISTS movimiento_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    cantidad INTEGER,
    fecha DATETIME,
    inventario_id INTEGER
)
""")

# Tabla lote_inventario
c.execute("""
CREATE TABLE IF NOT EXISTS lote_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    cantidad INTEGER,
    inventario_id INTEGER
)
""")

# Tabla archivo_adjunto
c.execute("""
CREATE TABLE IF NOT EXISTS archivo_adjunto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    ruta TEXT,
    usuario_id INTEGER
)
""")
# Crear usuario admin si no existe
c.execute(
    """
INSERT OR REPLACE INTO usuario (id, username, email, password, nombre, rol, activo, fecha_creacion)
VALUES (
    (SELECT id FROM usuario WHERE username = ?),
    ?, ?, ?, ?, ?, ?, datetime('now')
)
""",
    (username, username, email, hashed_password, nombre, rol, int(activo)),
)

conn.commit()
conn.close()

print("Usuario admin creado o actualizado correctamente.")
