-- Agregar columna faltante en la tabla inventario para alinear con el modelo
-- Ejecutar en Cloud SQL (PostgreSQL)

ALTER TABLE public.inventario
    ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);