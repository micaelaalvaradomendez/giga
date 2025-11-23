-- Actualización de la tabla licencia para soportar el sistema completo de gestión
-- Agrega campos de observaciones, justificación, aprobación y auditoría

DO $$ 
DECLARE
    column_exists boolean;
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
        ALTER TABLE licencia ADD COLUMN creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;

    SELECT EXISTS(SELECT 1 FROM information_schema.columns 
                 WHERE table_name='licencia' AND column_name='actualizado_en') INTO column_exists;
    IF NOT column_exists THEN
        ALTER TABLE licencia ADD COLUMN actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Agregar foreign keys si no existen
DO $$
DECLARE
    fk_exists boolean;
BEGIN
    -- Foreign key para aprobada_por
    SELECT EXISTS(SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name='licencia_aprobada_por_fkey') INTO fk_exists;
    IF NOT fk_exists THEN
        ALTER TABLE licencia ADD CONSTRAINT licencia_aprobada_por_fkey 
        FOREIGN KEY (aprobada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;

    -- Foreign key para rechazada_por
    SELECT EXISTS(SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name='licencia_rechazada_por_fkey') INTO fk_exists;
    IF NOT fk_exists THEN
        ALTER TABLE licencia ADD CONSTRAINT licencia_rechazada_por_fkey 
        FOREIGN KEY (rechazada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;

    -- Foreign key para solicitada_por
    SELECT EXISTS(SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name='licencia_solicitada_por_fkey') INTO fk_exists;
    IF NOT fk_exists THEN
        ALTER TABLE licencia ADD CONSTRAINT licencia_solicitada_por_fkey 
        FOREIGN KEY (solicitada_por) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;
END $$;

-- Crear trigger para actualizar automatizado_en si no existe
DO $$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_trigger WHERE tgname = 'update_licencia_actualizado_en') THEN
        CREATE OR REPLACE FUNCTION update_licencia_actualizado_en()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.actualizado_en = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        CREATE TRIGGER update_licencia_actualizado_en
            BEFORE UPDATE ON licencia
            FOR EACH ROW
            EXECUTE FUNCTION update_licencia_actualizado_en();
    END IF;
END $$;

-- Agregar valor por defecto a estado si es NULL
UPDATE licencia SET estado = 'pendiente' WHERE estado IS NULL;

-- Agregar algunos datos de prueba para licencias si la tabla está vacía
DO $$
DECLARE
    licencia_count INTEGER;
    agente_test_id BIGINT;
    tipo_licencia_test_id BIGINT;
BEGIN
    -- Contar licencias existentes
    SELECT COUNT(*) INTO licencia_count FROM licencia;
    
    -- Solo agregar datos si no hay licencias
    IF licencia_count = 0 THEN
        -- Obtener el primer agente disponible
        SELECT id_agente INTO agente_test_id FROM agente LIMIT 1;
        
        -- Obtener el primer tipo de licencia disponible
        SELECT id_tipo_licencia INTO tipo_licencia_test_id FROM tipo_licencia LIMIT 1;
        
        -- Insertar algunas licencias de prueba si tenemos agentes y tipos
        IF agente_test_id IS NOT NULL AND tipo_licencia_test_id IS NOT NULL THEN
            INSERT INTO licencia (estado, id_tipo_licencia, fecha_desde, fecha_hasta, id_agente, justificacion, solicitada_por, creado_en, actualizado_en)
            VALUES 
            ('pendiente', tipo_licencia_test_id, '2025-12-01', '2025-12-05', agente_test_id, 'Licencia de prueba pendiente', agente_test_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('aprobada', tipo_licencia_test_id, '2025-11-15', '2025-11-20', agente_test_id, 'Licencia de prueba aprobada', agente_test_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('rechazada', tipo_licencia_test_id, '2025-10-10', '2025-10-12', agente_test_id, 'Licencia de prueba rechazada', agente_test_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING;
            
            -- Actualizar las licencias con datos de aprobación/rechazo
            UPDATE licencia SET 
                aprobada_por = agente_test_id, 
                fecha_aprobacion = '2025-11-14',
                observaciones_aprobacion = 'Licencia aprobada automáticamente para pruebas'
            WHERE estado = 'aprobada' AND aprobada_por IS NULL;
            
            UPDATE licencia SET 
                rechazada_por = agente_test_id, 
                fecha_rechazo = '2025-10-09',
                motivo_rechazo = 'Licencia rechazada para pruebas del sistema'
            WHERE estado = 'rechazada' AND rechazada_por IS NULL;
        END IF;
    END IF;
END $$;

COMMIT;