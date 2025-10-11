-- Comandos SQL para ejecutar como superusuario postgres
-- para otorgar todos los permisos necesarios a gmao-user

-- Conectar a la base de datos postgres
\c postgres

-- Otorgar permisos en la base de datos
GRANT ALL PRIVILEGES ON DATABASE postgres TO "gmao-user";

-- Otorgar permisos en el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO "gmao-user";
GRANT USAGE ON SCHEMA public TO "gmao-user";

-- Otorgar permisos en todas las tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "gmao-user";

-- Otorgar permisos en todas las secuencias existentes
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "gmao-user";

-- Otorgar permisos por defecto para futuras tablas y secuencias
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "gmao-user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "gmao-user";

-- Hacer a gmao-user propietario de todas las tablas existentes
ALTER TABLE usuario OWNER TO "gmao-user";
ALTER TABLE activo OWNER TO "gmao-user";
ALTER TABLE plan_mantenimiento OWNER TO "gmao-user";
ALTER TABLE orden_trabajo OWNER TO "gmao-user";
ALTER TABLE inventario OWNER TO "gmao-user";
ALTER TABLE proveedor OWNER TO "gmao-user";
ALTER TABLE categoria OWNER TO "gmao-user";

-- Verificar los permisos
\dp