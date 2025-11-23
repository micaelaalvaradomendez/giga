-- ============================================================================
-- Script: 07-actualizar-funcion-plus-compensaciones.sql
-- Descripción: Actualiza la función de cálculo de plus para incluir compensaciones
-- Fecha: 2025-11-22
-- Sistema: GIGA - Gestión de Guardias Policiales
-- ============================================================================

-- Actualizar la función calcular_plus_agente para incluir horas de compensación
CREATE OR REPLACE FUNCTION calcular_plus_agente(
    p_id_agente BIGINT,
    p_mes INT,
    p_anio INT
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_area_nombre TEXT;
    v_es_area_operativa BOOLEAN := FALSE;
    v_total_horas_guardia DECIMAL(6,2) := 0;
    v_total_horas_compensacion DECIMAL(6,2) := 0;
    v_total_horas_completas DECIMAL(6,2) := 0;
    v_tiene_guardias BOOLEAN := FALSE;
    v_tiene_compensaciones BOOLEAN := FALSE;
    v_fecha_inicio DATE;
    v_fecha_fin DATE;
BEGIN
    -- Calcular fechas del mes
    v_fecha_inicio := DATE(p_anio || '-' || LPAD(p_mes::TEXT, 2, '0') || '-01');
    IF p_mes = 12 THEN
        v_fecha_fin := DATE((p_anio + 1) || '-01-01');
    ELSE
        v_fecha_fin := DATE(p_anio || '-' || LPAD((p_mes + 1)::TEXT, 2, '0') || '-01');
    END IF;
    
    -- Obtener área del agente
    SELECT COALESCE(LOWER(a.nombre), '') INTO v_area_nombre
    FROM agente ag
    LEFT JOIN area a ON ag.id_area = a.id_area
    WHERE ag.id_agente = p_id_agente;
    
    -- Determinar si es área operativa
    v_es_area_operativa := (
        v_area_nombre LIKE '%secretaría de protección civil%' OR
        v_area_nombre LIKE '%departamento operativo%' OR
        v_area_nombre LIKE '%operativo%' OR
        v_area_nombre LIKE '%emergencias%' OR
        v_area_nombre LIKE '%rescate%'
    );
    
    -- Obtener horas de guardias regulares
    SELECT 
        COALESCE(SUM(horas_efectivas), 0),
        COUNT(*) > 0
    INTO v_total_horas_guardia, v_tiene_guardias
    FROM guardia
    WHERE id_agente = p_id_agente
        AND fecha >= v_fecha_inicio
        AND fecha < v_fecha_fin
        AND activa = TRUE
        AND estado = 'planificada';
    
    -- *** NUEVA FUNCIONALIDAD: Obtener horas de compensación aprobadas ***
    SELECT 
        COALESCE(SUM(horas_extra), 0),
        COUNT(*) > 0
    INTO v_total_horas_compensacion, v_tiene_compensaciones
    FROM hora_compensacion
    WHERE id_agente = p_id_agente
        AND fecha_servicio >= v_fecha_inicio
        AND fecha_servicio < v_fecha_fin
        AND estado = 'aprobada';
    
    -- Calcular total combinado
    v_total_horas_completas := v_total_horas_guardia + v_total_horas_compensacion;
    
    -- *** REGLAS ACTUALIZADAS: Incluyen compensaciones ***
    -- Aplicar reglas de plus (versión 2.0 con compensaciones)
    IF v_es_area_operativa AND (v_tiene_guardias OR v_tiene_compensaciones) THEN
        -- Regla 1: Área operativa + guardia/compensación = 40%
        RETURN 40.0;
    ELSIF NOT v_es_area_operativa AND v_total_horas_completas >= 32 THEN
        -- Regla 2: Otras áreas + 32+ horas (incluyendo compensaciones) = 40%
        RETURN 40.0;
    ELSIF v_tiene_guardias OR v_tiene_compensaciones THEN
        -- Regla 3: Cualquier caso con guardias/compensaciones = 20%
        RETURN 20.0;
    ELSE
        -- Sin guardias ni compensaciones = sin plus
        RETURN 0.0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Crear función para obtener detalle de cálculo de plus (para debugging)
CREATE OR REPLACE FUNCTION detalle_calculo_plus_agente(
    p_id_agente BIGINT,
    p_mes INT,
    p_anio INT
) RETURNS TABLE (
    agente_nombre TEXT,
    area_nombre TEXT,
    es_area_operativa BOOLEAN,
    total_horas_guardias DECIMAL(6,2),
    cantidad_guardias INT,
    total_horas_compensacion DECIMAL(6,2),
    cantidad_compensaciones INT,
    total_horas_completas DECIMAL(6,2),
    porcentaje_plus DECIMAL(5,2),
    regla_aplicada TEXT
) AS $$
DECLARE
    v_area_nombre TEXT;
    v_es_area_operativa BOOLEAN := FALSE;
    v_total_horas_guardia DECIMAL(6,2) := 0;
    v_cantidad_guardias INT := 0;
    v_total_horas_compensacion DECIMAL(6,2) := 0;
    v_cantidad_compensaciones INT := 0;
    v_total_horas_completas DECIMAL(6,2) := 0;
    v_tiene_guardias BOOLEAN := FALSE;
    v_tiene_compensaciones BOOLEAN := FALSE;
    v_fecha_inicio DATE;
    v_fecha_fin DATE;
    v_porcentaje_plus DECIMAL(5,2);
    v_regla_aplicada TEXT;
    v_agente_nombre TEXT;
BEGIN
    -- Calcular fechas del mes
    v_fecha_inicio := DATE(p_anio || '-' || LPAD(p_mes::TEXT, 2, '0') || '-01');
    IF p_mes = 12 THEN
        v_fecha_fin := DATE((p_anio + 1) || '-01-01');
    ELSE
        v_fecha_fin := DATE(p_anio || '-' || LPAD((p_mes + 1)::TEXT, 2, '0') || '-01');
    END IF;
    
    -- Obtener información del agente
    SELECT 
        ag.nombre || ' ' || ag.apellido,
        COALESCE(a.nombre, 'Sin área')
    INTO v_agente_nombre, v_area_nombre
    FROM agente ag
    LEFT JOIN area a ON ag.id_area = a.id_area
    WHERE ag.id_agente = p_id_agente;
    
    -- Determinar si es área operativa
    v_es_area_operativa := (
        LOWER(v_area_nombre) LIKE '%secretaría de protección civil%' OR
        LOWER(v_area_nombre) LIKE '%departamento operativo%' OR
        LOWER(v_area_nombre) LIKE '%operativo%' OR
        LOWER(v_area_nombre) LIKE '%emergencias%' OR
        LOWER(v_area_nombre) LIKE '%rescate%'
    );
    
    -- Obtener datos de guardias
    SELECT 
        COALESCE(SUM(horas_efectivas), 0),
        COUNT(*)
    INTO v_total_horas_guardia, v_cantidad_guardias
    FROM guardia
    WHERE id_agente = p_id_agente
        AND fecha >= v_fecha_inicio
        AND fecha < v_fecha_fin
        AND activa = TRUE
        AND estado = 'planificada';
    
    v_tiene_guardias := v_cantidad_guardias > 0;
    
    -- Obtener datos de compensaciones
    SELECT 
        COALESCE(SUM(horas_extra), 0),
        COUNT(*)
    INTO v_total_horas_compensacion, v_cantidad_compensaciones
    FROM hora_compensacion
    WHERE id_agente = p_id_agente
        AND fecha_servicio >= v_fecha_inicio
        AND fecha_servicio < v_fecha_fin
        AND estado = 'aprobada';
    
    v_tiene_compensaciones := v_cantidad_compensaciones > 0;
    v_total_horas_completas := v_total_horas_guardia + v_total_horas_compensacion;
    
    -- Aplicar reglas y determinar porcentaje
    IF v_es_area_operativa AND (v_tiene_guardias OR v_tiene_compensaciones) THEN
        v_porcentaje_plus := 40.0;
        v_regla_aplicada := 'Área operativa + guardias/compensaciones = 40%';
    ELSIF NOT v_es_area_operativa AND v_total_horas_completas >= 32 THEN
        v_porcentaje_plus := 40.0;
        v_regla_aplicada := 'Otras áreas + 32+ horas (con compensaciones) = 40%';
    ELSIF v_tiene_guardias OR v_tiene_compensaciones THEN
        v_porcentaje_plus := 20.0;
        v_regla_aplicada := 'Guardias/compensaciones presentes = 20%';
    ELSE
        v_porcentaje_plus := 0.0;
        v_regla_aplicada := 'Sin guardias ni compensaciones = 0%';
    END IF;
    
    -- Retornar resultado
    agente_nombre := v_agente_nombre;
    area_nombre := v_area_nombre;
    es_area_operativa := v_es_area_operativa;
    total_horas_guardias := v_total_horas_guardia;
    cantidad_guardias := v_cantidad_guardias;
    total_horas_compensacion := v_total_horas_compensacion;
    cantidad_compensaciones := v_cantidad_compensaciones;
    total_horas_completas := v_total_horas_completas;
    porcentaje_plus := v_porcentaje_plus;
    regla_aplicada := v_regla_aplicada;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Comentarios actualizados
COMMENT ON FUNCTION calcular_plus_agente(BIGINT, INT, INT) IS 'Calcula el porcentaje de plus para un agente en un mes específico, incluyendo horas de compensación aprobadas (v2.0)';
COMMENT ON FUNCTION detalle_calculo_plus_agente(BIGINT, INT, INT) IS 'Proporciona detalle completo del cálculo de plus incluyendo guardias y compensaciones';

-- Registrar actualización en auditoría
INSERT INTO auditoria (pk_afectada, nombre_tabla, creado_en, valor_previo, valor_nuevo, accion, id_agente)
VALUES (0, 'funciones_plus', CURRENT_TIMESTAMP, 
        '{"version": "1.0", "incluye_compensaciones": false}', 
        '{"version": "2.0", "incluye_compensaciones": true, "fecha_actualizacion": "2025-11-22"}', 
        'ACTUALIZAR_FUNCION_PLUS', NULL);

-- Mensaje de éxito
SELECT 'Función calcular_plus_agente actualizada exitosamente para incluir horas de compensación' as resultado;

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
