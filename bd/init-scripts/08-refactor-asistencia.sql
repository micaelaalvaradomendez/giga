-- =====================================================
-- Migración: Refactorización del sistema de asistencia
-- Fecha: 2025-11-21
-- Descripción: Mejora el sistema de asistencia para soportar:
--   - Marca de entrada/salida con DNI
--   - Detección de intento de marcación con DNI ajeno
--   - Marcación automática de salida a las 22:00
--   - Correcciones manuales por administrador
-- =====================================================

-- 1. Eliminar tabla asistencia anterior si existe y recrearla
DROP TABLE IF EXISTS asistencia CASCADE;

-- 2. Recrear tabla asistencia con la nueva estructura
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    hora_salida TIME,
    marcacion_entrada_automatica BOOLEAN DEFAULT false,
    marcacion_salida_automatica BOOLEAN DEFAULT false,
    es_correccion BOOLEAN DEFAULT false,
    corregido_por BIGINT,
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_agente BIGINT NOT NULL,
    id_area BIGINT,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE SET NULL,
    FOREIGN KEY (corregido_por) REFERENCES agente(id_agente) ON DELETE SET NULL,
    UNIQUE(id_agente, fecha)
);

-- 3. Crear tabla para registro de intentos de marcación con DNI ajeno
CREATE TABLE IF NOT EXISTS intento_marcacion_fraudulenta (
    id_intento BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    dni_ingresado VARCHAR(20) NOT NULL,
    id_agente_sesion BIGINT NOT NULL,
    id_agente_dni BIGINT,
    tipo_intento VARCHAR(50) NOT NULL, -- 'entrada', 'salida'
    ip_address VARCHAR(45),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_agente_sesion) REFERENCES agente(id_agente) ON DELETE CASCADE,
    FOREIGN KEY (id_agente_dni) REFERENCES agente(id_agente) ON DELETE SET NULL
);

-- 4. Crear índices para optimización
CREATE INDEX IF NOT EXISTS idx_asistencia_agente_fecha ON asistencia(id_agente, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_asistencia_fecha ON asistencia(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_asistencia_area ON asistencia(id_area);
CREATE INDEX IF NOT EXISTS idx_intento_fraud_agente ON intento_marcacion_fraudulenta(id_agente_sesion);
CREATE INDEX IF NOT EXISTS idx_intento_fraud_fecha ON intento_marcacion_fraudulenta(fecha DESC);

-- 5. Crear función para marcar salida automática a las 22:00
CREATE OR REPLACE FUNCTION marcar_salidas_automaticas()
RETURNS void AS $$
BEGIN
    -- Actualizar asistencias del día anterior sin salida marcada
    UPDATE asistencia
    SET 
        hora_salida = '22:00:00',
        marcacion_salida_automatica = true,
        actualizado_en = CURRENT_TIMESTAMP,
        observaciones = COALESCE(observaciones || ' | ', '') || 'Salida marcada automáticamente por el sistema a las 22:00'
    WHERE 
        fecha = CURRENT_DATE - INTERVAL '1 day'
        AND hora_entrada IS NOT NULL
        AND hora_salida IS NULL
        AND marcacion_salida_automatica = false;
        
    RAISE NOTICE 'Salidas automáticas marcadas para el día %', CURRENT_DATE - INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;

-- 6. Crear función para obtener estado de asistencia de un agente en una fecha
CREATE OR REPLACE FUNCTION obtener_estado_asistencia(
    p_id_agente BIGINT,
    p_fecha DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    tiene_entrada BOOLEAN,
    tiene_salida BOOLEAN,
    hora_entrada TIME,
    hora_salida TIME,
    puede_marcar_entrada BOOLEAN,
    puede_marcar_salida BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.hora_entrada IS NOT NULL as tiene_entrada,
        a.hora_salida IS NOT NULL as tiene_salida,
        a.hora_entrada,
        a.hora_salida,
        a.hora_entrada IS NULL as puede_marcar_entrada,
        (a.hora_entrada IS NOT NULL AND a.hora_salida IS NULL) as puede_marcar_salida
    FROM asistencia a
    WHERE a.id_agente = p_id_agente AND a.fecha = p_fecha
    
    UNION ALL
    
    SELECT 
        false as tiene_entrada,
        false as tiene_salida,
        NULL::TIME as hora_entrada,
        NULL::TIME as hora_salida,
        true as puede_marcar_entrada,
        false as puede_marcar_salida
    WHERE NOT EXISTS (
        SELECT 1 FROM asistencia WHERE id_agente = p_id_agente AND fecha = p_fecha
    )
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- 7. Trigger para auditoría de cambios en asistencia
CREATE OR REPLACE FUNCTION audit_asistencia_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria (
            nombre_tabla,
            pk_afectada,
            accion,
            valor_nuevo,
            id_agente
        ) VALUES (
            'asistencia',
            NEW.id_asistencia,
            'CREAR',
            jsonb_build_object(
                'fecha', NEW.fecha,
                'hora_entrada', NEW.hora_entrada,
                'hora_salida', NEW.hora_salida,
                'id_agente', NEW.id_agente,
                'es_correccion', NEW.es_correccion
            ),
            COALESCE(NEW.corregido_por, NEW.id_agente)
        );
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria (
            nombre_tabla,
            pk_afectada,
            accion,
            valor_previo,
            valor_nuevo,
            id_agente
        ) VALUES (
            'asistencia',
            NEW.id_asistencia,
            'MODIFICAR',
            jsonb_build_object(
                'hora_entrada', OLD.hora_entrada,
                'hora_salida', OLD.hora_salida,
                'es_correccion', OLD.es_correccion,
                'observaciones', OLD.observaciones
            ),
            jsonb_build_object(
                'hora_entrada', NEW.hora_entrada,
                'hora_salida', NEW.hora_salida,
                'es_correccion', NEW.es_correccion,
                'observaciones', NEW.observaciones
            ),
            COALESCE(NEW.corregido_por, NEW.id_agente)
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_audit_asistencia ON asistencia;
CREATE TRIGGER trigger_audit_asistencia
    AFTER INSERT OR UPDATE ON asistencia
    FOR EACH ROW EXECUTE FUNCTION audit_asistencia_changes();

-- 8. Trigger para auditoría de intentos fraudulentos
CREATE OR REPLACE FUNCTION audit_intento_fraudulento()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria (
        nombre_tabla,
        pk_afectada,
        accion,
        valor_nuevo,
        id_agente
    ) VALUES (
        'intento_marcacion_fraudulenta',
        NEW.id_intento,
        'INTENTO_FRAUDULENTO',
        jsonb_build_object(
            'dni_ingresado', NEW.dni_ingresado,
            'tipo_intento', NEW.tipo_intento,
            'id_agente_sesion', NEW.id_agente_sesion,
            'id_agente_dni', NEW.id_agente_dni,
            'ip_address', NEW.ip_address
        ),
        NEW.id_agente_sesion
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_audit_intento_fraud ON intento_marcacion_fraudulenta;
CREATE TRIGGER trigger_audit_intento_fraud
    AFTER INSERT ON intento_marcacion_fraudulenta
    FOR EACH ROW EXECUTE FUNCTION audit_intento_fraudulento();

-- 9. Comentarios en las tablas
COMMENT ON TABLE asistencia IS 'Registro de asistencias diarias de agentes con marcación de entrada/salida';
COMMENT ON COLUMN asistencia.marcacion_entrada_automatica IS 'Indica si la entrada fue marcada automáticamente por el sistema';
COMMENT ON COLUMN asistencia.marcacion_salida_automatica IS 'Indica si la salida fue marcada automáticamente a las 22:00';
COMMENT ON COLUMN asistencia.es_correccion IS 'Indica si la asistencia fue corregida manualmente por un administrador';
COMMENT ON COLUMN asistencia.corregido_por IS 'ID del agente que realizó la corrección';

COMMENT ON TABLE intento_marcacion_fraudulenta IS 'Registro de intentos de marcación con DNI que no corresponde al usuario logueado';
COMMENT ON COLUMN intento_marcacion_fraudulenta.id_agente_sesion IS 'Agente que tiene la sesión activa';
COMMENT ON COLUMN intento_marcacion_fraudulenta.id_agente_dni IS 'Agente al que corresponde el DNI ingresado';

-- Fin de la migración
