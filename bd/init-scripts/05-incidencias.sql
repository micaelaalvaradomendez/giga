-- ========================================================================
-- TABLA: incidencia - Sistema de Incidencias/Reclamos
-- Fecha: 04 de Diciembre 2025
-- Descripción: Tabla para gestión de incidencias relacionadas con guardias
-- ========================================================================

CREATE TABLE IF NOT EXISTS incidencia (
    id BIGSERIAL PRIMARY KEY,
    numero VARCHAR(20) UNIQUE NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    
    -- Estado y prioridad (lowercase para consistencia)
    estado VARCHAR(25) NOT NULL DEFAULT 'abierta',
    prioridad VARCHAR(10) NOT NULL DEFAULT 'media',
    
    -- Relaciones con personas
    creado_por BIGINT NOT NULL,
    asignado_a BIGINT,
    area_involucrada BIGINT NOT NULL,
    
    -- Fechas importantes
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_asignacion TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    
    -- Resolución y seguimiento
    resolucion TEXT,
    comentarios_seguimiento JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (creado_por) REFERENCES agente(id_agente) ON DELETE CASCADE,
    FOREIGN KEY (asignado_a) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (area_involucrada) REFERENCES area(id_area) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_estado_valido CHECK (estado IN ('abierta', 'en_proceso', 'pendiente_informacion', 'resuelta', 'cerrada')),
    CONSTRAINT chk_prioridad_valida CHECK (prioridad IN ('baja', 'media', 'alta', 'critica'))
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_incidencia_creado_por ON incidencia(creado_por);
CREATE INDEX IF NOT EXISTS idx_incidencia_asignado_a ON incidencia(asignado_a);
CREATE INDEX IF NOT EXISTS idx_incidencia_area_involucrada ON incidencia(area_involucrada);
CREATE INDEX IF NOT EXISTS idx_incidencia_fecha_creacion ON incidencia(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_incidencia_estado ON incidencia(estado);
CREATE INDEX IF NOT EXISTS idx_incidencia_numero ON incidencia(numero);

-- Comentarios para documentación
COMMENT ON TABLE incidencia IS 'Registro de incidencias/reclamos relacionados con guardias y operaciones';
COMMENT ON COLUMN incidencia.numero IS 'Número único de incidencia formato INC-YYYY-###';
COMMENT ON COLUMN incidencia.estado IS 'Estados: abierta, en_proceso, pendiente_informacion, resuelta, cerrada';
COMMENT ON COLUMN incidencia.prioridad IS 'Prioridades: baja, media, alta, critica';
COMMENT ON COLUMN incidencia.comentarios_seguimiento IS 'Array JSON con historial de comentarios y cambios';

-- ========================================================================
-- FIN DEL SCRIPT DE TABLA INCIDENCIA
-- ========================================================================
