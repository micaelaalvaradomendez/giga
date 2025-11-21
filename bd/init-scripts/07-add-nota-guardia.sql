-- Migration: Add nota_guardia table for personal notes on guardias
-- Purpose: Allow agents to add personal notes to their assigned guardias
-- Date: 2025-11-21

-- Create nota_guardia table
CREATE TABLE IF NOT EXISTS nota_guardia (
    id_nota BIGSERIAL PRIMARY KEY,
    id_guardia BIGINT NOT NULL,
    id_agente BIGINT NOT NULL,
    nota TEXT,
    fecha_nota TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    CONSTRAINT fk_nota_guardia_guardia FOREIGN KEY (id_guardia) 
        REFERENCES guardia(id_guardia) ON DELETE CASCADE,
    CONSTRAINT fk_nota_guardia_agente FOREIGN KEY (id_agente) 
        REFERENCES agente(id_agente) ON DELETE CASCADE,
    
    -- Only one note per agent per guardia
    CONSTRAINT unique_nota_per_agente_guardia UNIQUE (id_guardia, id_agente)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_nota_guardia_id_guardia ON nota_guardia(id_guardia);
CREATE INDEX IF NOT EXISTS idx_nota_guardia_id_agente ON nota_guardia(id_agente);
CREATE INDEX IF NOT EXISTS idx_nota_guardia_fecha ON nota_guardia(fecha_nota);

-- Add comments
COMMENT ON TABLE nota_guardia IS 'Notas personales de agentes sobre sus guardias asignadas';
COMMENT ON COLUMN nota_guardia.id_nota IS 'ID único de la nota';
COMMENT ON COLUMN nota_guardia.id_guardia IS 'ID de la guardia asociada';
COMMENT ON COLUMN nota_guardia.id_agente IS 'ID del agente que escribe la nota';
COMMENT ON COLUMN nota_guardia.nota IS 'Contenido de la nota personal';
COMMENT ON COLUMN nota_guardia.fecha_nota IS 'Fecha y hora de la nota';

-- Add update trigger for actualizado_en
CREATE OR REPLACE FUNCTION actualizar_timestamp_nota_guardia()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_nota_guardia
    BEFORE UPDATE ON nota_guardia
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp_nota_guardia();
