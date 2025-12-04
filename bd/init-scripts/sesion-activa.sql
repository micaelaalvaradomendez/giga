-- Migración: Control de Sesiones Activas
-- Fecha: 2025-12-03

CREATE TABLE sesion_activa (
    id_sesion_activa BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL,
    session_key VARCHAR(40) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    dispositivo VARCHAR(100), -- "Desktop", "Mobile", "Tablet"
    navegador VARCHAR(100),   -- "Chrome", "Firefox", etc.
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ultimo_acceso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activa BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT fk_sesion_agente 
        FOREIGN KEY (id_agente) 
        REFERENCES agente(id_agente) 
        ON DELETE CASCADE
);

-- Índices para optimizar consultas
CREATE INDEX idx_sesion_agente_activa ON sesion_activa(id_agente, activa);
CREATE INDEX idx_sesion_key ON sesion_activa(session_key);
CREATE INDEX idx_sesion_ultimo_acceso ON sesion_activa(ultimo_acceso);

-- Comentarios
COMMENT ON TABLE sesion_activa IS 'Tracking de sesiones activas por usuario para control de concurrencia';
COMMENT ON COLUMN sesion_activa.session_key IS 'Session key de Django (sessionid cookie)';
COMMENT ON COLUMN sesion_activa.ultimo_acceso IS 'Timestamp de la última actividad, actualizado por middleware';
