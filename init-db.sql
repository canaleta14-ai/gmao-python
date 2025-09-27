-- Script de inicialización de base de datos PostgreSQL para GMAO
-- Ejecutar este script después de crear la base de datos

-- Crear usuario para la aplicación (opcional)
-- CREATE USER gmao_user WITH PASSWORD 'gmao_password';
-- GRANT ALL PRIVILEGES ON DATABASE gmao_db TO gmao_user;

-- Crear extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas de texto

-- Configurar permisos para el usuario de la aplicación
-- GRANT USAGE ON SCHEMA public TO gmao_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gmao_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gmao_user;

-- Configurar búsqueda de texto completo en español
-- ALTER TEXT SEARCH CONFIGURATION spanish SET stem TO 'spanish_stem';

-- Crear índices para búsquedas eficientes (ejemplos)
-- CREATE INDEX CONCURRENTLY idx_activos_codigo ON activos USING gin (codigo gin_trgm_ops);
-- CREATE INDEX CONCURRENTLY idx_activos_descripcion ON activos USING gin (descripcion gin_trgm_ops);
-- CREATE INDEX CONCURRENTLY idx_ordenes_descripcion ON ordenes_trabajo USING gin (descripcion gin_trgm_ops);

-- Configurar límites de conexión
-- ALTER DATABASE gmao_db SET shared_preload_libraries = 'pg_stat_statements';
-- ALTER DATABASE gmao_db SET pg_stat_statements.max = 10000;
-- ALTER DATABASE gmao_db SET pg_stat_statements.track = 'all';