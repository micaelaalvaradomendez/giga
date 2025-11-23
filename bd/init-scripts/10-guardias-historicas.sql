-- Script CORREGIDO para generar guardias históricas para desarrollo y testing de reportes
-- Sistema GIGA - Datos de prueba realistas

-- Ejecutar solo si no hay guardias históricas ya creadas (con manejo de errores)
DO $$
DECLARE
    v_guardias_count INT;
BEGIN
    SELECT COUNT(*) INTO v_guardias_count FROM guardia WHERE fecha >= '2025-06-01' AND fecha <= '2025-11-30';
    
    IF v_guardias_count > 0 THEN
        RAISE NOTICE 'Guardias históricas ya existen (%). Saltando generación.', v_guardias_count;
        RETURN;
    END IF;
    
    -- Verificar que hay datos mínimos requeridos
    IF (SELECT COUNT(*) FROM agente WHERE activo = true) < 3 THEN
        RAISE NOTICE 'Faltan agentes para generar datos de prueba. Saltando.';
        RETURN;
    END IF;
    
    IF (SELECT COUNT(*) FROM area WHERE activo = true) < 2 THEN
        RAISE NOTICE 'Faltan áreas para generar datos de prueba. Saltando.';
        RETURN;
    END IF;
    
    RAISE NOTICE 'Generando guardias históricas con datos válidos...';
    RAISE NOTICE 'Agentes disponibles: %', (SELECT COUNT(*) FROM agente WHERE activo = true);
    RAISE NOTICE 'Áreas disponibles: %', (SELECT COUNT(*) FROM area WHERE activo = true);

    -- 1. CRONOGRAMAS BASE usando IDs válidos de agentes y áreas reales
    INSERT INTO cronograma (
        id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin, 
        estado, fecha_creacion, fecha_aprobacion, creado_por_rol, creado_por_id, aprobado_por_id,
        creado_en, actualizado_en
    ) 
    SELECT 
        a1.id_agente as id_jefe,
        a2.id_agente as id_director, 
        ar.id_area,
        'regular' as tipo,
        '08:00'::TIME as hora_inicio,
        '16:00'::TIME as hora_fin,
        'publicada' as estado,
        ('2025-06-0' || (row_number() over() % 9 + 1))::DATE as fecha_creacion,
        ('2025-06-0' || (row_number() over() % 9 + 2))::DATE as fecha_aprobacion,
        'administrador' as creado_por_rol,
        a1.id_agente as creado_por_id,
        a2.id_agente as aprobado_por_id,
        NOW() as creado_en,
        NOW() as actualizado_en
    FROM 
        (SELECT id_agente FROM agente WHERE activo = true LIMIT 1) a1,
        (SELECT id_agente FROM agente WHERE activo = true LIMIT 1) a2,
        (SELECT id_area FROM area WHERE activo = true LIMIT 3) ar
    LIMIT 6;

    -- 2. GUARDIAS HISTÓRICAS usando los cronogramas recién creados
    INSERT INTO guardia (
        id_cronograma, id_agente, fecha, hora_inicio, hora_fin, 
        tipo, estado, activa, horas_planificadas, horas_efectivas, 
        observaciones, creado_en, actualizado_en
    )
    SELECT 
        c.id_cronograma,
        a.id_agente,
        ('2025-06-' || LPAD((row_number() over() % 28 + 1)::TEXT, 2, '0'))::DATE as fecha,
        '08:00'::TIME as hora_inicio,
        '16:00'::TIME as hora_fin,
        'regular' as tipo,
        'planificada' as estado,
        true as activa,
        8 as horas_planificadas,
        8 as horas_efectivas,
        '' as observaciones,
        NOW() as creado_en,
        NOW() as actualizado_en
    FROM 
        cronograma c,
        (SELECT id_agente FROM agente WHERE activo = true LIMIT 5) a
    WHERE c.fecha_creacion >= '2025-06-01'
    LIMIT 20;

    -- Resumen final
    RAISE NOTICE '=== GUARDIAS HISTÓRICAS GENERADAS ===';
    RAISE NOTICE 'Cronogramas creados: %', (SELECT COUNT(*) FROM cronograma WHERE fecha_creacion >= '2025-06-01');
    RAISE NOTICE 'Guardias generadas: %', (SELECT COUNT(*) FROM guardia WHERE fecha >= '2025-06-01');
    RAISE NOTICE '====================================';

END $$;
