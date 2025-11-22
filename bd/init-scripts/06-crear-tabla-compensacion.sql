-- ============================================================================
-- Script: 06-crear-tabla-compensacion.sql
-- Descripción: Crea la tabla para sistema de compensación de horas de emergencia
-- Fecha: 2025-11-22
-- Sistema: GIGA - Gestión de Guardias Policiales
-- ============================================================================

-- Crear tabla para horas de compensación por emergencias
CREATE TABLE IF NOT EXISTS hora_compensacion (
    id_hora_compensacion BIGSERIAL PRIMARY KEY,
    
    -- Relaciones principales
    id_agente BIGINT NOT NULL REFERENCES agente(id_agente) ON DELETE CASCADE,
    id_guardia BIGINT REFERENCES guardia(id_guardia) ON DELETE SET NULL,
    id_cronograma BIGINT NOT NULL REFERENCES cronograma(id_cronograma) ON DELETE CASCADE,
    
    -- Información de la compensación
    fecha_servicio DATE NOT NULL,
    hora_inicio_programada TIME NOT NULL,
    hora_fin_programada TIME NOT NULL,
    hora_fin_real TIME NOT NULL,
    
    horas_programadas DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    horas_efectivas DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    horas_extra DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    
    -- Motivo y justificación
    motivo VARCHAR(20) NOT NULL DEFAULT 'emergencia',
    descripcion_motivo TEXT NOT NULL,
    numero_acta VARCHAR(50),
    
    -- Estado y aprobación
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    tipo_compensacion VARCHAR(20) NOT NULL DEFAULT 'plus',
    
    -- Información de aprobación
    solicitado_por BIGINT NOT NULL REFERENCES agente(id_agente),
    aprobado_por BIGINT REFERENCES agente(id_agente),
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    observaciones_aprobacion TEXT,
    
    -- Cálculos automáticos
    valor_hora_extra DECIMAL(10,2),
    monto_total DECIMAL(10,2),
    
    -- Auditoría
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Restricciones
    CONSTRAINT chk_horas_extra_positivas CHECK (horas_extra > 0),
    CONSTRAINT chk_horas_extra_limite CHECK (horas_extra <= 8),
    CONSTRAINT chk_hora_fin_real_posterior CHECK (hora_fin_real > hora_fin_programada),
    CONSTRAINT chk_estado_valido CHECK (estado IN ('pendiente', 'aprobada', 'rechazada', 'pagada')),
    CONSTRAINT chk_motivo_valido CHECK (motivo IN ('siniestro', 'emergencia', 'operativo', 'refuerzo', 'otro')),
    CONSTRAINT chk_tipo_compensacion_valido CHECK (tipo_compensacion IN ('pago', 'franco', 'plus')),
    
    -- Índice único para evitar duplicados por agente y fecha
    CONSTRAINT uk_compensacion_agente_fecha UNIQUE (id_agente, fecha_servicio, id_cronograma)
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_agente ON hora_compensacion(id_agente);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_fecha ON hora_compensacion(fecha_servicio);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_estado ON hora_compensacion(estado);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_mes_anio ON hora_compensacion(EXTRACT(YEAR FROM fecha_servicio), EXTRACT(MONTH FROM fecha_servicio));
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_solicitado_por ON hora_compensacion(solicitado_por);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_aprobado_por ON hora_compensacion(aprobado_por);

-- Comentarios en la tabla
COMMENT ON TABLE hora_compensacion IS 'Registro de horas de compensación por emergencias que exceden el límite reglamentario de 10 horas';
COMMENT ON COLUMN hora_compensacion.id_hora_compensacion IS 'Identificador único de la compensación';
COMMENT ON COLUMN hora_compensacion.id_agente IS 'Agente que prestó el servicio extendido';
COMMENT ON COLUMN hora_compensacion.id_guardia IS 'Guardia original que se extendió (opcional)';
COMMENT ON COLUMN hora_compensacion.id_cronograma IS 'Cronograma al que pertenece la guardia';
COMMENT ON COLUMN hora_compensacion.fecha_servicio IS 'Fecha en que se prestó el servicio';
COMMENT ON COLUMN hora_compensacion.hora_inicio_programada IS 'Hora de inicio programada de la guardia';
COMMENT ON COLUMN hora_compensacion.hora_fin_programada IS 'Hora de fin programada de la guardia';
COMMENT ON COLUMN hora_compensacion.hora_fin_real IS 'Hora real de finalización del servicio';
COMMENT ON COLUMN hora_compensacion.horas_programadas IS 'Horas programadas originalmente';
COMMENT ON COLUMN hora_compensacion.horas_efectivas IS 'Horas realmente trabajadas';
COMMENT ON COLUMN hora_compensacion.horas_extra IS 'Horas extra trabajadas (diferencia)';
COMMENT ON COLUMN hora_compensacion.motivo IS 'Motivo de la extensión: siniestro, emergencia, operativo, refuerzo, otro';
COMMENT ON COLUMN hora_compensacion.descripcion_motivo IS 'Descripción detallada del motivo';
COMMENT ON COLUMN hora_compensacion.numero_acta IS 'Número de acta o expediente relacionado';
COMMENT ON COLUMN hora_compensacion.estado IS 'Estado: pendiente, aprobada, rechazada, pagada';
COMMENT ON COLUMN hora_compensacion.tipo_compensacion IS 'Tipo: pago, franco, plus';
COMMENT ON COLUMN hora_compensacion.solicitado_por IS 'Agente que solicita la compensación';
COMMENT ON COLUMN hora_compensacion.aprobado_por IS 'Agente que aprueba/rechaza la compensación';
COMMENT ON COLUMN hora_compensacion.valor_hora_extra IS 'Valor monetario por hora extra';
COMMENT ON COLUMN hora_compensacion.monto_total IS 'Monto total de la compensación';

-- Trigger para actualizar automatically horas calculadas
CREATE OR REPLACE FUNCTION actualizar_horas_compensacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcular horas programadas
    NEW.horas_programadas := EXTRACT(EPOCH FROM (NEW.hora_fin_programada - NEW.hora_inicio_programada)) / 3600.0;
    
    -- Calcular horas efectivas (considerando cruce de medianoche)
    IF NEW.hora_fin_real < NEW.hora_inicio_programada THEN
        -- Cruzó medianoche
        NEW.horas_efectivas := EXTRACT(EPOCH FROM (NEW.hora_fin_real + INTERVAL '24 hours' - NEW.hora_inicio_programada)) / 3600.0;
    ELSE
        NEW.horas_efectivas := EXTRACT(EPOCH FROM (NEW.hora_fin_real - NEW.hora_inicio_programada)) / 3600.0;
    END IF;
    
    -- Calcular horas extra
    NEW.horas_extra := NEW.horas_efectivas - NEW.horas_programadas;
    
    -- Actualizar timestamp de actualización
    NEW.actualizado_en := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_horas_compensacion
    BEFORE INSERT OR UPDATE ON hora_compensacion
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_horas_compensacion();

-- Función para obtener resumen mensual de compensaciones de un agente
CREATE OR REPLACE FUNCTION obtener_resumen_compensaciones_agente(
    p_id_agente BIGINT,
    p_mes INT,
    p_anio INT
) RETURNS TABLE (
    total_horas_extra DECIMAL(6,2),
    total_compensaciones INT,
    monto_total DECIMAL(10,2),
    compensaciones_por_motivo JSONB
) AS $$
DECLARE
    v_resultado RECORD;
    v_por_motivo JSONB;
BEGIN
    -- Obtener totales principales
    SELECT 
        COALESCE(SUM(horas_extra), 0) as horas,
        COUNT(*) as cantidad,
        COALESCE(SUM(monto_total), 0) as monto
    INTO v_resultado
    FROM hora_compensacion
    WHERE id_agente = p_id_agente
        AND EXTRACT(MONTH FROM fecha_servicio) = p_mes
        AND EXTRACT(YEAR FROM fecha_servicio) = p_anio
        AND estado = 'aprobada';
    
    -- Obtener agrupación por motivo
    SELECT jsonb_object_agg(motivo, cantidad) INTO v_por_motivo
    FROM (
        SELECT motivo, COUNT(*) as cantidad
        FROM hora_compensacion
        WHERE id_agente = p_id_agente
            AND EXTRACT(MONTH FROM fecha_servicio) = p_mes
            AND EXTRACT(YEAR FROM fecha_servicio) = p_anio
            AND estado = 'aprobada'
        GROUP BY motivo
    ) sub;
    
    -- Retornar resultado
    total_horas_extra := v_resultado.horas;
    total_compensaciones := v_resultado.cantidad;
    monto_total := v_resultado.monto;
    compensaciones_por_motivo := COALESCE(v_por_motivo, '{}'::jsonb);
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Función para validar si se puede crear una compensación
CREATE OR REPLACE FUNCTION validar_compensacion(
    p_id_agente BIGINT,
    p_fecha_servicio DATE,
    p_hora_fin_real TIME,
    p_id_guardia BIGINT DEFAULT NULL
) RETURNS TABLE (
    es_valida BOOLEAN,
    mensaje TEXT,
    horas_extra DECIMAL(4,2)
) AS $$
DECLARE
    v_guardia RECORD;
    v_compensacion_existente BOOLEAN;
    v_horas_extra DECIMAL(4,2);
    v_horas_efectivas DECIMAL(4,2);
    v_dias_transcurridos INT;
BEGIN
    -- Verificar días transcurridos (máximo 30 días)
    v_dias_transcurridos := CURRENT_DATE - p_fecha_servicio;
    IF v_dias_transcurridos > 30 THEN
        es_valida := FALSE;
        mensaje := 'No se puede solicitar compensación después de 30 días';
        horas_extra := 0;
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Verificar si ya existe compensación para esa fecha
    SELECT EXISTS(
        SELECT 1 FROM hora_compensacion 
        WHERE id_agente = p_id_agente 
        AND fecha_servicio = p_fecha_servicio
    ) INTO v_compensacion_existente;
    
    IF v_compensacion_existente THEN
        es_valida := FALSE;
        mensaje := 'Ya existe una compensación para esta fecha';
        horas_extra := 0;
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Obtener información de la guardia
    IF p_id_guardia IS NOT NULL THEN
        SELECT * INTO v_guardia
        FROM guardia 
        WHERE id_guardia = p_id_guardia
        AND id_agente = p_id_agente
        AND fecha = p_fecha_servicio;
    ELSE
        SELECT * INTO v_guardia
        FROM guardia 
        WHERE id_agente = p_id_agente
        AND fecha = p_fecha_servicio
        AND activa = TRUE
        LIMIT 1;
    END IF;
    
    IF v_guardia IS NULL THEN
        es_valida := FALSE;
        mensaje := 'No hay guardia programada para esta fecha';
        horas_extra := 0;
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Validar que hora fin real sea posterior a programada
    IF p_hora_fin_real <= v_guardia.hora_fin THEN
        es_valida := FALSE;
        mensaje := 'La hora fin real debe ser posterior a la programada';
        horas_extra := 0;
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Calcular horas efectivas y extra
    IF p_hora_fin_real < v_guardia.hora_inicio THEN
        -- Cruzó medianoche
        v_horas_efectivas := EXTRACT(EPOCH FROM (p_hora_fin_real + INTERVAL '24 hours' - v_guardia.hora_inicio)) / 3600.0;
    ELSE
        v_horas_efectivas := EXTRACT(EPOCH FROM (p_hora_fin_real - v_guardia.hora_inicio)) / 3600.0;
    END IF;
    
    v_horas_extra := v_horas_efectivas - EXTRACT(EPOCH FROM (v_guardia.hora_fin - v_guardia.hora_inicio)) / 3600.0;
    
    -- Validar límites
    IF v_horas_extra > 8 THEN
        es_valida := FALSE;
        mensaje := 'No se pueden registrar más de 8 horas extra por servicio';
        horas_extra := 0;
        RETURN NEXT;
        RETURN;
    END IF;
    
    IF v_horas_efectivas > 18 THEN
        es_valida := FALSE;
        mensaje := 'El servicio total no puede exceder 18 horas';
        horas_extra := 0;
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Validación exitosa
    es_valida := TRUE;
    mensaje := FORMAT('Compensación válida: %.1f horas extra', v_horas_extra);
    horas_extra := v_horas_extra;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Registrar en auditoria la creación de la tabla
INSERT INTO auditoria (pk_afectada, nombre_tabla, creado_en, valor_previo, valor_nuevo, accion, id_agente)
VALUES (0, 'hora_compensacion', CURRENT_TIMESTAMP, NULL, '{"tabla_creada": true, "version": "1.0", "fecha": "2025-11-22"}', 'CREAR_TABLA', NULL);

-- Mensaje de éxito
SELECT 'Tabla hora_compensacion creada exitosamente con funciones de validación y triggers automáticos' as resultado;