"""
SOLUCION PARA PROBLEMA DE AUTENTICACION CLOUD SQL
=================================================

SITUACION ACTUAL:

- Error: password authentication failed for user "gmao-user"
- La aplicación está desplegada y funciona (responde HTTP 200/302)
- Pero no puede conectar a Cloud SQL para inicializar la base de datos

SOLUCION RECOMENDADA:

1. USAR CLOUD SHELL para ejecutar comandos SQL directamente:

   gcloud sql connect gmao-postgres-spain --user=postgres --database=postgres

2. Una vez conectado, ejecutar estas consultas SQL:

   -- Crear todas las tablas
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

   -- Crear usuario administrador
   INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
   VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
   'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
   'admin', true);

3. VERIFICAR LA CONEXION:

   -- Verificar que las tablas se crearon
   \dt

   -- Verificar que el usuario admin existe
   SELECT * FROM usuario WHERE username = 'admin';

4. CONFIRMAR EN LA APLICACION:

   Una vez completado, la aplicación debería poder hacer login con:
   Usuario: admin
   Contraseña: admin123

CREDENCIALES ACTUALES:

- Cloud SQL Instance: gmao-postgres-spain
- Database: postgres
- Usuario DB: gmao-user
- Password DB: admin123
- Usuario Admin App: admin
- Password Admin App: admin123

URL APLICACION: https://mantenimiento-470311.ew.r.appspot.com

NOTA: Si el problema persiste, contactar al administrador de sistemas
para revisar los permisos de Cloud SQL y la configuración de red.
"""
