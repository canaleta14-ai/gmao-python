-- Script para verificar los índices creados en la tabla inventario
-- Ejecutar con: psql -h localhost -U postgres -d gmao -f verificar_indices_inventario.sql

-- Mostrar todos los índices de la tabla inventario
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'inventario'
ORDER BY indexname;

-- Estadísticas de los índices (tamaño y uso)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'inventario'
ORDER BY indexname;
