-- Migración para agregar nuevos campos al sistema de licencias
-- Archivo: agregar_campos_licencias.sql
-- Fecha: 23 de noviembre de 2025

BEGIN;

-- Agregar nuevos campos a la tabla licencia
ALTER TABLE licencia 
ADD COLUMN IF NOT EXISTS observaciones TEXT,
ADD COLUMN IF NOT EXISTS justificacion TEXT,
ADD COLUMN IF NOT EXISTS aprobada_por BIGINT,
ADD COLUMN IF NOT EXISTS fecha_aprobacion DATE,
ADD COLUMN IF NOT EXISTS observaciones_aprobacion TEXT,
ADD COLUMN IF NOT EXISTS rechazada_por BIGINT,
ADD COLUMN IF NOT EXISTS fecha_rechazo DATE,
ADD COLUMN IF NOT EXISTS motivo_rechazo TEXT,
ADD COLUMN IF NOT EXISTS solicitada_por BIGINT,
ADD COLUMN IF NOT EXISTS creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Actualizar la columna estado para tener un valor por defecto
ALTER TABLE licencia ALTER COLUMN estado SET DEFAULT 'pendiente';

-- Agregar constraints de foreign key para los nuevos campos
-- (Verificar si ya existe antes de crear)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'licencia_aprobada_por_fkey'
    ) THEN
        ALTER TABLE licencia 
        ADD CONSTRAINT licencia_aprobada_por_fkey 
            FOREIGN KEY (aprobada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'licencia_rechazada_por_fkey'
    ) THEN
        ALTER TABLE licencia 
        ADD CONSTRAINT licencia_rechazada_por_fkey 
            FOREIGN KEY (rechazada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'licencia_solicitada_por_fkey'
    ) THEN
        ALTER TABLE licencia 
        ADD CONSTRAINT licencia_solicitada_por_fkey 
            FOREIGN KEY (solicitada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;
END $$;

-- Agregar índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_licencia_estado ON licencia(estado);
CREATE INDEX IF NOT EXISTS idx_licencia_aprobada_por ON licencia(aprobada_por);
CREATE INDEX IF NOT EXISTS idx_licencia_fechas_estado ON licencia(fecha_desde, fecha_hasta, estado);
CREATE INDEX IF NOT EXISTS idx_licencia_creado_en ON licencia(creado_en);

-- Crear trigger para actualizar automatically el campo actualizado_en
CREATE OR REPLACE FUNCTION update_licencia_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_licencia_actualizado_en ON licencia;
CREATE TRIGGER trigger_licencia_actualizado_en
    BEFORE UPDATE ON licencia
    FOR EACH ROW
    EXECUTE FUNCTION update_licencia_actualizado_en();

-- Actualizar registros existentes para tener valores por defecto
UPDATE licencia 
SET 
    creado_en = COALESCE(creado_en, NOW()),
    actualizado_en = COALESCE(actualizado_en, NOW()),
    estado = COALESCE(estado, 'pendiente')
WHERE creado_en IS NULL OR actualizado_en IS NULL OR estado IS NULL;

COMMIT;

-- Verificar que los cambios se aplicaron correctamente
SELECT 'Migración completada exitosamente. Verificando estructura...' AS mensaje;
\d licencia