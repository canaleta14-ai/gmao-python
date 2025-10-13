-- Agregar columnas faltantes en plan_mantenimiento para alinear con el modelo
-- Ejecutar en PostgreSQL

ALTER TABLE plan_mantenimiento
    ADD COLUMN IF NOT EXISTS tipo_mantenimiento VARCHAR(50);

ALTER TABLE plan_mantenimiento
    ADD COLUMN IF NOT EXISTS tareas TEXT;

ALTER TABLE plan_mantenimiento
    ADD COLUMN IF NOT EXISTS duracion_estimada DOUBLE PRECISION;

-- Nuevo: responsable_id para enlazar técnico responsable (sin constraint explícito)
ALTER TABLE plan_mantenimiento
    ADD COLUMN IF NOT EXISTS responsable_id INTEGER;

-- Ajustar longitud de dias_semana para coincidir con el modelo (200)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'plan_mantenimiento'
          AND column_name = 'dias_semana'
    ) THEN
        BEGIN
            ALTER TABLE plan_mantenimiento
                ALTER COLUMN dias_semana TYPE VARCHAR(200);
        EXCEPTION WHEN others THEN
            -- Ignorar si ya tiene longitud suficiente o si no es posible cambiar
            NULL;
        END;
    END IF;
END $$;

-- Opcional: índice básico para consultas por estado
CREATE INDEX IF NOT EXISTS idx_plan_mantenimiento_estado
    ON plan_mantenimiento (estado);

-- Índice de apoyo para responsable
CREATE INDEX IF NOT EXISTS idx_plan_mantenimiento_responsable
    ON plan_mantenimiento (responsable_id);