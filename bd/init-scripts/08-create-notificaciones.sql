-- Tabla para notificaciones (Django App: notificaciones)
CREATE TABLE notificacion (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo VARCHAR(50) DEFAULT 'GENERICO' NOT NULL,
    leida BOOLEAN DEFAULT FALSE NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    link VARCHAR(255),
    id_agente BIGINT NOT NULL REFERENCES agente(id_agente) ON DELETE CASCADE
);

CREATE INDEX idx_notificacion_agente_leida ON notificacion (id_agente, leida);
CREATE INDEX idx_notificacion_fecha ON notificacion (fecha_creacion DESC);
