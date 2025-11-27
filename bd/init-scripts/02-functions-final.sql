-- ========================================================================
-- SCRIPT CONSOLIDADO: FUNCIONES Y TRIGGERS FINALES - Sistema GIGA
-- Fecha: 27 de Noviembre 2025
-- Descripción: Definición consolidada de TODAS las funciones y triggers
-- Incluye funciones de scripts 02, 04, 06, 07, 08, 11, 12
-- ========================================================================
-- NOTA: Este script reemplaza los archivos 02, 04, 06, 07, 08, 11, 12
-- ========================================================================

-- =====================================================
-- FUNCIONES BÁSICAS DE UTILIDAD
-- =====================================================

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- =====================================================
-- TRIGGERS DE TIMESTAMP AUTOMÁTICOS
-- =====================================================

-- Trigger para agente
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_agente_timestamp') THEN
        CREATE TRIGGER update_agente_timestamp
            BEFORE UPDATE ON agente
            FOR EACH ROW EXECUTE FUNCTION update_timestamp();
    END IF;
END $$;

-- Trigger para cronograma
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_cronograma_timestamp') THEN
        CREATE TRIGGER update_cronograma_timestamp
            BEFORE UPDATE ON cronograma
            FOR EACH ROW EXECUTE FUNCTION update_timestamp();
    END IF;
END $$;

-- Trigger para agrupación
DROP TRIGGER IF EXISTS trigger_update_agrupacion_timestamp ON agrupacion;
CREATE TRIGGER trigger_update_agrupacion_timestamp
    BEFORE UPDATE ON agrupacion
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Trigger para licencia (del script 12)
DO $$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_trigger WHERE tgname = 'update_licencia_actualizado_en') THEN
        CREATE OR REPLACE FUNCTION update_licencia_actualizado_en()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.actualizado_en = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        CREATE TRIGGER update_licencia_actualizado_en
            BEFORE UPDATE ON licencia
            FOR EACH ROW EXECUTE FUNCTION update_licencia_actualizado_en();
    END IF;
END $$;

-- Trigger para feriado (del script 11)
CREATE OR REPLACE FUNCTION actualizar_feriado_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_feriado_actualizado ON feriado;
CREATE TRIGGER tr_feriado_actualizado
    BEFORE UPDATE ON feriado
    FOR EACH ROW EXECUTE FUNCTION actualizar_feriado_timestamp();

-- =====================================================
-- FUNCIONES DE VALIDACIÓN
-- =====================================================

-- Validar fechas de licencia
CREATE OR REPLACE FUNCTION validar_fechas_licencia()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.fecha_hasta < NEW.fecha_desde THEN
        RAISE EXCEPTION 'La fecha de fin no puede ser anterior a la fecha de inicio';
    END IF;
    RETURN NEW;
END;
$$;

-- Trigger para validación de licencias
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'validate_licencia') THEN
        CREATE TRIGGER validate_licencia
            BEFORE INSERT OR UPDATE ON licencia
            FOR EACH ROW EXECUTE FUNCTION validar_fechas_licencia();
    END IF;
END $$;

-- =====================================================
-- FUNCIONES PARA FERIADOS (del script 11)
-- =====================================================

-- Verificar si una fecha es feriado (ACTUALIZADA para rangos)
CREATE OR REPLACE FUNCTION es_fecha_feriado(fecha_consulta DATE)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM feriado 
        WHERE fecha_consulta BETWEEN fecha_inicio AND fecha_fin 
        AND activo = true
    );
END;
$$ LANGUAGE plpgsql;

-- Obtener feriados en una fecha específica
CREATE OR REPLACE FUNCTION obtener_feriados_fecha(fecha_consulta DATE)
RETURNS TABLE(
    id_feriado BIGINT,
    nombre VARCHAR(200),
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    es_nacional BOOLEAN,
    es_provincial BOOLEAN,
    es_local BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id_feriado,
        f.nombre,
        f.descripcion,
        f.fecha_inicio,
        f.fecha_fin,
        f.es_nacional,
        f.es_provincial,
        f.es_local
    FROM feriado f
    WHERE fecha_consulta BETWEEN f.fecha_inicio AND f.fecha_fin
    AND f.activo = true
    ORDER BY f.fecha_inicio, f.nombre;
END;
$$ LANGUAGE plpgsql;

-- Obtener feriados en un rango de fechas
CREATE OR REPLACE FUNCTION obtener_feriados_rango(
    fecha_inicio_consulta DATE,
    fecha_fin_consulta DATE
)
RETURNS TABLE(
    id_feriado BIGINT,
    nombre VARCHAR(200),
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    es_nacional BOOLEAN,
    es_provincial BOOLEAN,
    es_local BOOLEAN,
    duracion_dias INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id_feriado,
        f.nombre,
        f.descripcion,
        f.fecha_inicio,
        f.fecha_fin,
        f.es_nacional,
        f.es_provincial,
        f.es_local,
        (f.fecha_fin - f.fecha_inicio + 1)::INTEGER as duracion_dias
    FROM feriado f
    WHERE f.fecha_inicio <= fecha_fin_consulta 
    AND f.fecha_fin >= fecha_inicio_consulta
    AND f.activo = true
    ORDER BY f.fecha_inicio, f.nombre;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCIONES PARA COMPENSACIONES (del script 06)
-- =====================================================

-- Trigger para actualizar horas de compensación automáticamente
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

-- Crear trigger para compensaciones
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_actualizar_horas_compensacion') THEN
        CREATE TRIGGER trigger_actualizar_horas_compensacion
            BEFORE INSERT OR UPDATE ON hora_compensacion
            FOR EACH ROW EXECUTE FUNCTION actualizar_horas_compensacion();
    END IF;
END $$;

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
    
    -- Verificar si ya existe compensación
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

-- =====================================================
-- FUNCIONES PARA ASISTENCIA (del script 08)
-- =====================================================

-- Función para marcar salida automática a las 22:00
CREATE OR REPLACE FUNCTION marcar_salidas_automaticas()
RETURNS void AS $$
BEGIN
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

-- Función para obtener estado de asistencia de un agente
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

-- Trigger para auditoría de cambios en asistencia
CREATE OR REPLACE FUNCTION audit_asistencia_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria (
            nombre_tabla, pk_afectada, accion, valor_nuevo, id_agente
        ) VALUES (
            'asistencia', NEW.id_asistencia, 'CREAR',
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
            nombre_tabla, pk_afectada, accion, valor_previo, valor_nuevo, id_agente
        ) VALUES (
            'asistencia', NEW.id_asistencia, 'MODIFICAR',
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

-- Trigger para auditoría de intentos fraudulentos
CREATE OR REPLACE FUNCTION audit_intento_fraudulento()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria (
        nombre_tabla, pk_afectada, accion, valor_nuevo, id_agente
    ) VALUES (
        'intento_marcacion_fraudulenta', NEW.id_intento, 'INTENTO_FRAUDULENTO',
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

-- =====================================================
-- FUNCIONES PARA PARÁMETROS Y CRONOGRAMAS
-- =====================================================

-- Función para obtener parámetros de área vigentes
CREATE OR REPLACE FUNCTION obtener_parametros_area(
    area_id BIGINT, 
    fecha_consulta DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    ventana_entrada_inicio TIME,
    ventana_entrada_fin TIME,
    ventana_salida_inicio TIME,
    ventana_salida_fin TIME,
    tolerancia_entrada_min INTEGER,
    tolerancia_salida_min INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.ventana_entrada_inicio,
        p.ventana_entrada_fin,
        p.ventana_salida_inicio,
        p.ventana_salida_fin,
        p.tolerancia_entrada_min,
        p.tolerancia_salida_min
    FROM parametros_area p
    WHERE p.id_area = area_id
    AND p.activo = true
    AND p.vigente_desde <= fecha_consulta
    AND (p.vigente_hasta IS NULL OR p.vigente_hasta >= fecha_consulta)
    ORDER BY p.vigente_desde DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCIONES PARA CÁLCULO DE PLUS (ACTUALIZADA - v2.0 del script 07)
-- =====================================================

-- Calcular plus con compensaciones incluidas
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
    
    --  Obtener horas de guardias regulares
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
    
    -- INCLUIR horas de compensación aprobadas (NOVEDAD v2.0)
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
    
    -- Aplicar reglas de plus (ACTUALIZADAS con compensaciones)
    IF v_es_area_operativa AND (v_tiene_guardias OR v_tiene_compensaciones) THEN
        RETURN 40.0;  -- Área operativa con guardias/compensaciones
    ELSIF NOT v_es_area_operativa AND v_total_horas_completas >= 32 THEN
        RETURN 40.0;  -- Otras áreas con 32+ horas (incl. compensaciones)
    ELSIF v_tiene_guardias OR v_tiene_compensaciones THEN
        RETURN 20.0;  -- Cualquier caso con guardias/compensaciones
    ELSE
        RETURN 0.0;   -- Sin guardias ni compensaciones
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calcular_plus_agente(BIGINT, INT, INT) IS 'Calcula el porcentaje de plus para un agente en un mes específico, incluyendo horas de compensación aprobadas (v2.0)';

-- Función de detalle de cálculo de plus (para debugging)
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
    v_fecha_inicio := DATE(p_anio || '-' || LPAD(p_mes::TEXT, 2, '0') || '-01');
    IF p_mes = 12 THEN
        v_fecha_fin := DATE((p_anio + 1) || '-01-01');
    ELSE
        v_fecha_fin := DATE(p_anio || '-' || LPAD((p_mes + 1)::TEXT, 2, '0') || '-01');
    END IF;
    
    SELECT 
        ag.nombre || ' ' || ag.apellido,
        COALESCE(a.nombre, 'Sin área')
    INTO v_agente_nombre, v_area_nombre
    FROM agente ag
    LEFT JOIN area a ON ag.id_area = a.id_area
    WHERE ag.id_agente = p_id_agente;
    
    v_es_area_operativa := (
        LOWER(v_area_nombre) LIKE '%secretaría de protección civil%' OR
        LOWER(v_area_nombre) LIKE '%departamento operativo%' OR
        LOWER(v_area_nombre) LIKE '%operativo%' OR
        LOWER(v_area_nombre) LIKE '%emergencias%' OR
        LOWER(v_area_nombre) LIKE '%rescate%'
    );
    
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

COMMENT ON FUNCTION detalle_calculo_plus_agente(BIGINT, INT, INT) IS 'Proporciona detalle completo del cálculo de plus incluyendo guardias y compensaciones';

-- ========================================================================
-- MENSAJE DE CONFIRMACIÓN
-- ========================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'SCRIPT CONSOLIDADO DE FUNCIONES COMPLETADO';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Funciones consolidadas:';
    RAISE NOTICE '- Timestamps automáticos (10 triggers)';
    RAISE NOTICE '- Validaciones (licencias, compensaciones)';
    RAISE NOTICE '- Feriados (verificación por rango)';
    RAISE NOTICE '- Compensaciones (cálculo automático, validación, resumen)';
    RAISE NOTICE '- Asistencia (marcación automática, estado, auditoría)';
    RAISE NOTICE '- Plus (cálculo v2.0 con compensaciones)';
    RAISE NOTICE '- Parámetros y cronogramas';
    RAISE NOTICE '========================================';
END $$;

-- ========================================================================
-- FIN DEL SCRIPT CONSOLIDADO DE FUNCIONES
-- ========================================================================
