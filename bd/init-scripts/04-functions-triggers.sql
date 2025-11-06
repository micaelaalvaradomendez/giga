-- =====================================================
-- FUNCIONES Y TRIGGERS SIMPLIFICADOS PARA SISTEMA GIGA  
-- =====================================================

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER 
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- Triggers para timestamps automáticos
CREATE TRIGGER update_agente_timestamp
    BEFORE UPDATE ON agente
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_cronograma_timestamp
    BEFORE UPDATE ON cronograma
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Función simplificada para validar fechas de licencia
CREATE OR REPLACE FUNCTION validar_fechas_licencia()
    RETURNS TRIGGER 
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.fecha_hasta < NEW.fecha_desde THEN
        RAISE EXCEPTION 'La fecha de fin no puede ser anterior a la fecha de inicio';
    END IF;
    
    RETURN NEW;
END;
$$;

-- Trigger para validación de licencias
CREATE TRIGGER validate_licencia
    BEFORE INSERT OR UPDATE ON licencia
    FOR EACH ROW
    EXECUTE FUNCTION validar_fechas_licencia();

-- =====================================================
-- FUNCIONES ADICIONALES PARA CRONOGRAMAS Y PLUS
-- =====================================================

-- Función para actualizar timestamp de agrupaciones
CREATE OR REPLACE FUNCTION update_agrupacion_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para agrupaciones
DROP TRIGGER IF EXISTS trigger_update_agrupacion_timestamp ON agrupacion;
CREATE TRIGGER trigger_update_agrupacion_timestamp
    BEFORE UPDATE ON agrupacion
    FOR EACH ROW
    EXECUTE FUNCTION update_agrupacion_timestamp();

-- Función para verificar si una fecha es feriado
CREATE OR REPLACE FUNCTION es_feriado(fecha_consulta DATE)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM feriado 
        WHERE fecha = fecha_consulta 
        AND activo = true
    );
END;
$$ LANGUAGE plpgsql;

-- Función para obtener parámetros de área vigentes
CREATE OR REPLACE FUNCTION obtener_parametros_area(area_id BIGINT, fecha_consulta DATE DEFAULT CURRENT_DATE)
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

-- Función para calcular plus automáticamente
CREATE OR REPLACE FUNCTION calcular_plus_agente(agente_id BIGINT, mes_calc INTEGER, anio_calc INTEGER)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    horas_efectivas DECIMAL(6,2);
    porcentaje_plus DECIMAL(5,2) := 0;
    regla RECORD;
BEGIN
    -- Obtener horas efectivas del agente en el período
    SELECT COALESCE(SUM(horas_efectivas), 0) INTO horas_efectivas
    FROM guardia g
    JOIN cronograma c ON g.id_cronograma = c.id_cronograma
    WHERE g.id_agente = agente_id
    AND EXTRACT(MONTH FROM g.fecha) = mes_calc
    AND EXTRACT(YEAR FROM g.fecha) = anio_calc
    AND g.activa = true;
    
    -- Buscar regla aplicable
    FOR regla IN 
        SELECT * FROM reglas_plus r
        WHERE r.activa = true
        AND (r.vigente_hasta IS NULL OR 
             make_date(anio_calc, mes_calc, 1) <= r.vigente_hasta)
        ORDER BY r.porcentaje_plus DESC
    LOOP
        IF horas_efectivas >= regla.horas_minimas_mensuales THEN
            porcentaje_plus := regla.porcentaje_plus;
            EXIT;
        END IF;
    END LOOP;
    
    RETURN porcentaje_plus;
END;
$$ LANGUAGE plpgsql;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Funciones y triggers del sistema GIGA creados exitosamente';
    RAISE NOTICE 'Funciones adicionales: es_feriado, obtener_parametros_area, calcular_plus_agente';
END $$;