-- Migration: Add approval tracking to cronograma table
-- Purpose: Track who created the cronograma and who approved it for hierarchical workflow
-- Date: 2025

-- Add approval tracking fields to cronograma
ALTER TABLE cronograma 
    ADD COLUMN IF NOT EXISTS creado_por_rol VARCHAR(50),
    ADD COLUMN IF NOT EXISTS creado_por_id BIGINT,
    ADD COLUMN IF NOT EXISTS aprobado_por_id BIGINT;

-- Add foreign key constraints
ALTER TABLE cronograma 
    ADD CONSTRAINT fk_cronograma_creado_por 
    FOREIGN KEY (creado_por_id) REFERENCES agente(id_agente) 
    ON DELETE SET NULL;

ALTER TABLE cronograma 
    ADD CONSTRAINT fk_cronograma_aprobado_por 
    FOREIGN KEY (aprobado_por_id) REFERENCES agente(id_agente) 
    ON DELETE SET NULL;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_cronograma_estado ON cronograma(estado);
CREATE INDEX IF NOT EXISTS idx_cronograma_creado_por_rol ON cronograma(creado_por_rol);
CREATE INDEX IF NOT EXISTS idx_cronograma_creado_por_id ON cronograma(creado_por_id);
CREATE INDEX IF NOT EXISTS idx_cronograma_aprobado_por_id ON cronograma(aprobado_por_id);

-- Add comments
COMMENT ON COLUMN cronograma.creado_por_rol IS 'Rol del agente que creó el cronograma (jefatura, director, administrador)';
COMMENT ON COLUMN cronograma.creado_por_id IS 'ID del agente que creó el cronograma';
COMMENT ON COLUMN cronograma.aprobado_por_id IS 'ID del agente que aprobó el cronograma';

-- Update estado values documentation
COMMENT ON COLUMN cronograma.estado IS 'Estados: generada (inicial), pendiente (esperando aprobación), aprobada (aprobada por superior), publicada (visible para todos), rechazada, cancelada';
