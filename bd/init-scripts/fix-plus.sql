-- ========================================================================
-- MIGRACIÓN: Corrección de Lógica de Plus Salarial
-- Fecha: 30 de noviembre de 2025
-- Descripción: Corrige la lógica de cálculo del plus para que diferencie
--              correctamente entre áreas operativas y administrativas según
--              las horas trabajadas.
-- ========================================================================

\echo '=================================='
\echo 'CORRIGIENDO LÓGICA DE PLUS SALARIAL'
\echo '=================================='

-- Backup de la función anterior (por si acaso)
DO $$
BEGIN
    RAISE NOTICE 'Aplicando corrección a funciones de cálculo de plus...';
END $$;

-- =====================================================
-- FUNCIÓN PRINCIPAL CORREGIDA
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
    SELECT COALESCE(SUM(horas_efectivas), 0)
    INTO v_total_horas_guardia
    FROM guardia
    WHERE id_agente = p_id_agente
        AND fecha >= v_fecha_inicio
        AND fecha < v_fecha_fin
        AND activa = TRUE
        AND estado = 'planificada';
    
    -- INCLUIR horas de compensación aprobadas
    SELECT COALESCE(SUM(horas_extra), 0)
    INTO v_total_horas_compensacion
    FROM hora_compensacion
    WHERE id_agente = p_id_agente
        AND fecha_servicio >= v_fecha_inicio
        AND fecha_servicio < v_fecha_fin
        AND estado = 'aprobada';
    
    -- Calcular total combinado
    v_total_horas_completas := v_total_horas_guardia + v_total_horas_compensacion;
    
    -- LÓGICA CORREGIDA: Diferenciar por tipo de área y horas trabajadas
    IF v_es_area_operativa THEN
        -- ÁREA OPERATIVA
        IF v_total_horas_completas >= 8 THEN
            RETURN 40.0;  -- Plus 40% si >= 8 horas
        ELSIF v_total_horas_completas > 0 THEN
            RETURN 20.0;  -- Plus 20% si 1-7 horas
        ELSE
            RETURN 0.0;   -- Sin plus si 0 horas
        END IF;
    ELSE
        -- ÁREA ADMINISTRATIVA (O CUALQUIER OTRA)
        IF v_total_horas_completas >= 32 THEN
            RETURN 40.0;  -- Plus 40% si >= 32 horas
        ELSIF v_total_horas_completas > 0 THEN
            RETURN 20.0;  -- Plus 20% si 1-31 horas
        ELSE
            RETURN 0.0;   -- Sin plus si 0 horas
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calcular_plus_agente(BIGINT, INT, INT) IS 'Calcula el porcentaje de plus para un agente. CORREGIDO v3.0: Operativos >=8h=40%, 1-7h=20%. Administrativos >=32h=40%, 1-31h=20%.';

-- =====================================================
-- FUNCIÓN DE DETALLE CORREGIDA
-- =====================================================

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
    
    -- LÓGICA CORREGIDA
    IF v_es_area_operativa THEN
        -- ÁREA OPERATIVA
        IF v_total_horas_completas >= 8 THEN
            v_porcentaje_plus := 40.0;
            v_regla_aplicada := 'Área operativa + >= 8 horas = 40%';
        ELSIF v_total_horas_completas > 0 THEN
            v_porcentaje_plus := 20.0;
            v_regla_aplicada := 'Área operativa + 1-7 horas = 20%';
        ELSE
            v_porcentaje_plus := 0.0;
            v_regla_aplicada := 'Sin horas trabajadas = 0%';
        END IF;
    ELSE
        -- ÁREA ADMINISTRATIVA
        IF v_total_horas_completas >= 32 THEN
            v_porcentaje_plus := 40.0;
            v_regla_aplicada := 'Área administrativa + >= 32 horas = 40%';
        ELSIF v_total_horas_completas > 0 THEN
            v_porcentaje_plus := 20.0;
            v_regla_aplicada := 'Área administrativa + 1-31 horas = 20%';
        ELSE
            v_porcentaje_plus := 0.0;
            v_regla_aplicada := 'Sin horas trabajadas = 0%';
        END IF;
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

COMMENT ON FUNCTION detalle_calculo_plus_agente(BIGINT, INT, INT) IS 'Proporciona detalle completo del cálculo de plus CORREGIDO v3.0';

-- ========================================================================
-- CONFIRMACIÓN
-- ========================================================================

DO $$
BEGIN
    RAISE NOTICE '==================================';
    RAISE NOTICE 'MIGRACIÓN COMPLETADA EXITOSAMENTE';
    RAISE NOTICE '==================================';
    RAISE NOTICE 'Funciones actualizadas:';
    RAISE NOTICE '✓ calcular_plus_agente() CORREGIDA';
    RAISE NOTICE '✓ detalle_calculo_plus_agente() CORREGIDA';
    RAISE NOTICE 'Nuevas reglas aplicadas:';
    RAISE NOTICE 'OPERATIVOS:';
    RAISE NOTICE '  >= 8 horas  → 40%% plus';
    RAISE NOTICE '  1-7 horas   → 20%% plus';
    RAISE NOTICE '  0 horas     → 0%% plus';
    RAISE NOTICE 'ADMINISTRATIVOS:';
    RAISE NOTICE '  >= 32 horas → 40%% plus';
    RAISE NOTICE '  1-31 horas  → 20%% plus';
    RAISE NOTICE '  0 horas     → 0%% plus';
    RAISE NOTICE 'IMPORTANTE: Ejecute recálculo del mes actual';
    RAISE NOTICE 'desde el backend Django para actualizar registros.';
    RAISE NOTICE '==================================';
END $$;

-- ========================================================================
-- FIN DE LA MIGRACIÓN
-- ========================================================================
