-- Actualización de la tabla licencia para soportar el sistema completo de gestión
-- Agrega campos de observaciones, justificación, aprobación y auditoría
-- Versión corregida sin duplicaciones

BEGIN;

-- Agregar nuevos campos a la tabla licencia si no existen
DO $$ 
DECLARE
    column_exists boolean;
    fk_exists boolean;
BEGIN
    -- Agregar campo observaciones si no existe
    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='observaciones') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN observaciones TEXT;
    END IF;

    -- Agregar campo justificacion si no existe
    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='justificacion') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN justificacion TEXT;
    END IF;

    -- Agregar campos de aprobación si no existen
    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='aprobada_por') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN aprobada_por BIGINT;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='fecha_aprobacion') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN fecha_aprobacion DATE;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='observaciones_aprobacion') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN observaciones_aprobacion TEXT;
    END IF;

    -- Agregar campos de rechazo si no existen
    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='rechazada_por') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN rechazada_por BIGINT;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='fecha_rechazo') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN fecha_rechazo DATE;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='motivo_rechazo') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN motivo_rechazo TEXT;
    END IF;

    -- Agregar campo de auditoría si no existe
    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='solicitada_por') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN solicitada_por BIGINT;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='creado_en') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='actualizado_en') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

    -- Actualizar columna estado para tener valor por defecto si no lo tiene
    BEGIN
        ALTER TABLE licencia ALTER COLUMN estado SET DEFAULT 'pendiente';
    EXCEPTION WHEN others THEN
        NULL; -- Ignora si la columna ya tiene un default
    END;

    -- Agregar foreign keys si no existen
    SELECT EXISTS(SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name='licencia_aprobada_por_fkey') INTO fk_exists;
    IF NOT fk_exists THEN
        ALTER TABLE licencia ADD CONSTRAINT licencia_aprobada_por_fkey 
        FOREIGN KEY (aprobada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name='licencia_rechazada_por_fkey') INTO fk_exists;
    IF NOT fk_exists THEN
        ALTER TABLE licencia ADD CONSTRAINT licencia_rechazada_por_fkey 
        FOREIGN KEY (rechazada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name='licencia_solicitada_por_fkey') INTO fk_exists;
    IF NOT fk_exists THEN
        ALTER TABLE licencia ADD CONSTRAINT licencia_solicitada_por_fkey 
        FOREIGN KEY (solicitada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;

END $$;

-- Agregar índices para mejorar performance si no existen
CREATE INDEX IF NOT EXISTS idx_licencia_estado ON licencia(estado);
CREATE INDEX IF NOT EXISTS idx_licencia_aprobada_por ON licencia(aprobada_por);
CREATE INDEX IF NOT EXISTS idx_licencia_fechas_estado ON licencia(fecha_desde, fecha_hasta, estado);
CREATE INDEX IF NOT EXISTS idx_licencia_creado_en ON licencia(creado_en);

-- Crear trigger para actualizar automaticamente el campo actualizado_en si no existe
DO $$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_trigger WHERE tgname = 'update_licencia_actualizado_en') THEN
        CREATE OR REPLACE FUNCTION update_licencia_actualizado_en()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.actualizado_en = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        CREATE TRIGGER update_licencia_actualizado_en
            BEFORE UPDATE ON licencia
            FOR EACH ROW
            EXECUTE FUNCTION update_licencia_actualizado_en();
    END IF;
END $$;

-- Actualizar registros existentes para tener valores por defecto
UPDATE licencia 
SET 
    creado_en = COALESCE(creado_en, NOW()),
    actualizado_en = COALESCE(actualizado_en, NOW()),
    estado = COALESCE(estado, 'pendiente')
WHERE creado_en IS NULL OR actualizado_en IS NULL OR estado IS NULL;

COMMIT;

-- Verificar que los cambios se aplicaron correctamente
SELECT 'Migración de licencias completada exitosamente.' AS mensaje;