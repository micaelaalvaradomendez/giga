-- ========================================================================
-- SCRIPT: DATOS HISTÓRICOS COMPLETOS - Sistema GIGA
-- Fecha: 27 de Noviembre 2025
-- Descripción: Genera datos históricos realistas para testing y desarrollo
-- Incluye: Cronogramas, Guardias, Asistencias, Licencias, Compensaciones
-- ========================================================================
-- EJECUTAR DESPUÉS DE: 01-tables, 02-functions, 03-seed-data
-- ========================================================================

DO $$
DECLARE
    v_count_cronogramas INT;
    v_count_guardias INT;
    v_agente RECORD;
    v_area_operativa_id BIGINT;
    v_area_admin_id BIGINT;
    v_cronograma_id BIGINT;
    v_mes INT;
    v_anio INT := 2025;
    v_fecha DATE;
    v_guardia_id BIGINT;
BEGIN
    -- Verificar si ya hay datos históricos
    SELECT COUNT(*) INTO v_count_cronogramas FROM cronograma WHERE fecha_creacion >= '2025-01-01';
    
    IF v_count_cronogramas > 20 THEN
        RAISE NOTICE 'Ya existen datos históricos (% cronogramas). Saltando generación.', v_count_cronogramas;
        RETURN;
    END IF;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'GENERANDO DATOS HISTÓRICOS COMPLETOS';
    RAISE NOTICE '========================================';
    
    -- Obtener áreas de referencia
    SELECT id_area INTO v_area_operativa_id FROM area WHERE nombre LIKE '%Operativo%' LIMIT 1;
    SELECT id_area INTO v_area_admin_id FROM area WHERE nombre LIKE '%Administrativa%' LIMIT 1;
    
    -- =====================================================
    -- 1. CRONOGRAMAS MENSUALES (Enero - Noviembre 2025)
    -- =====================================================
    RAISE NOTICE 'Generando cronogramas mensuales...';
    
    FOR v_mes IN 1..11 LOOP
        -- Cronograma turno mañana
        INSERT INTO cronograma (
            id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin,
            estado, fecha_creacion, fecha_aprobacion,
            creado_por_rol, creado_por_id, aprobado_por_id,
            creado_en, actualizado_en
        ) VALUES (
            (SELECT id_agente FROM agente WHERE legajo = '004' LIMIT 1),
            (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1),
            COALESCE(v_area_operativa_id, 1),
            'regular',
            '08:00'::TIME,
            '16:00'::TIME,
            'publicada',
            DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01'),
            DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-03'),
            'jefatura',
            (SELECT id_agente FROM agente WHERE legajo = '004' LIMIT 1),
            (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1),
            NOW(),
            NOW()
        ) RETURNING id_cronograma INTO v_cronograma_id;
        
        -- Cronograma turno tarde
        INSERT INTO cronograma (
            id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin,
            estado, fecha_creacion, fecha_aprobacion,
            creado_por_rol, creado_por_id, aprobado_por_id,
            creado_en, actualizado_en
        ) VALUES (
            (SELECT id_agente FROM agente WHERE legajo = '009' LIMIT 1),
            (SELECT id_agente FROM agente WHERE legajo = '007' LIMIT 1),
            COALESCE(v_area_operativa_id, 1),
            'regular',
            '16:00'::TIME,
            '00:00'::TIME,
            'publicada',
            DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01'),
            DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-03'),
            'jefatura',
            (SELECT id_agente FROM agente WHERE legajo = '009' LIMIT 1),
            (SELECT id_agente FROM agente WHERE legajo = '007' LIMIT 1),
            NOW(),
            NOW()
        );
        
        -- Cronograma turno noche (fines de semana)
        INSERT INTO cronograma (
            id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin,
            estado, fecha_creacion, fecha_aprobacion,
            creado_por_rol, creado_por_id, aprobado_por_id,
            creado_en, actualizado_en
        ) VALUES (
            (SELECT id_agente FROM agente WHERE legajo = '008' LIMIT 1),
            (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1),
            COALESCE(v_area_operativa_id, 1),
            'nocturno',
            '00:00'::TIME,
            '08:00'::TIME,
            'publicada',
            DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01'),
            DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-04'),
            'jefatura',
            (SELECT id_agente FROM agente WHERE legajo = '008' LIMIT 1),
            (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1),
            NOW(),
            NOW()
        );
    END LOOP;
    
    -- =====================================================
    -- 2. GUARDIAS DISTRIBUIDAS (6 meses de historia)
    -- =====================================================
    RAISE NOTICE 'Generando guardias históricas...';
    
    FOR v_mes IN 6..11 LOOP -- Junio a Noviembre
        -- Obtener cronogramas del mes
        FOR v_cronograma_id IN 
            SELECT id_cronograma FROM cronograma 
            WHERE EXTRACT(MONTH FROM fecha_creacion) = v_mes 
            AND EXTRACT(YEAR FROM fecha_creacion) = v_anio
            AND estado = 'publicada'
            LIMIT 3
        LOOP
            -- Generar guardias para cada día del mes (solo días laborables)
            FOR v_fecha IN 
                SELECT generate_series(
                    DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01'),
                    DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-' || 
                         EXTRACT(DAY FROM (DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01') + INTERVAL '1 month' - INTERVAL '1 day'))::TEXT),
                    '1 day'::INTERVAL
                )::DATE
                WHERE EXTRACT(ISODOW FROM generate_series) <= 5 -- Solo lunes a viernes
            LOOP
                -- Asignar guardia a 2-3 agentes por día rotando
                FOR v_agente IN 
                    SELECT id_agente FROM agente 
                    WHERE activo = true 
                    ORDER BY RANDOM() 
                    LIMIT 2 + (RANDOM() * 1)::INT
                LOOP
                    INSERT INTO guardia (
                        id_cronograma, id_agente, fecha,
                        hora_inicio, hora_fin, tipo, estado, activa,
                        horas_planificadas, horas_efectivas,
                        observaciones, creado_en, actualizado_en
                    ) VALUES (
                        v_cronograma_id,
                        v_agente.id_agente,
                        v_fecha,
                        '08:00'::TIME + (RANDOM() * INTERVAL '4 hours'),
                        '16:00'::TIME + (RANDOM() * INTERVAL '2 hours'),
                        CASE WHEN RANDOM() > 0.8 THEN 'refuerzo' ELSE 'regular' END,
                        'planificada',
                        true,
                        8,
                        7 + (RANDOM() * 2)::INT,  -- Entre 7-9 horas
                        '',
                        NOW(),
                        NOW()
                    ) RETURNING id_guardia INTO v_guardia_id;
                END LOOP;
            END LOOP;
        END LOOP;
    END LOOP;
    
    -- =====================================================
    -- 3. ASISTENCIAS (últimos 3 meses)
    -- =====================================================
    RAISE NOTICE 'Generando asistencias...';
    
    FOR v_mes IN 9..11 LOOP -- Septiembre a Noviembre
        FOR v_agente IN SELECT id_agente, id_area FROM agente WHERE activo = true LOOP
            -- Generar asistencia para cada día laborable
            FOR v_fecha IN 
                SELECT generate_series(
                    DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01'),
                    DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-' || 
                         EXTRACT(DAY FROM (DATE(v_anio || '-' || LPAD(v_mes::TEXT, 2, '0') || '-01') + INTERVAL '1 month' - INTERVAL '1 day'))::TEXT),
                    '1 day'::INTERVAL
                )::DATE
                WHERE EXTRACT(ISODOW FROM generate_series) <= 5
            LOOP
                -- 90% de asistencias normales, 10% con irregularidades
                IF RANDOM() > 0.1 THEN
                    INSERT INTO asistencia (
                        id_agente, id_area, fecha,
                        hora_entrada, hora_salida,
                        marcacion_entrada_automatica, marcacion_salida_automatica,
                        es_correccion, observaciones,
                        creado_en, actualizado_en
                    ) VALUES (
                        v_agente.id_agente,
                        v_agente.id_area,
                        v_fecha,
                        '08:00'::TIME + (RANDOM() * INTERVAL '30 minutes'),
                        '17:00'::TIME + (RANDOM() * INTERVAL '1 hour'),
                        false,
                        false,
                        false,
                        '',
                        NOW(),
                        NOW()
                    ) ON CONFLICT (id_agente, fecha) DO NOTHING;
                ELSE
                    -- Asistencia con marcación tardía o automática
                    INSERT INTO asistencia (
                        id_agente, id_area, fecha,
                        hora_entrada, hora_salida,
                        marcacion_entrada_automatica, marcacion_salida_automatica,
                        es_correccion, observaciones,
                        creado_en, actualizado_en
                    ) VALUES (
                        v_agente.id_agente,
                        v_agente.id_area,
                        v_fecha,
                        '09:30'::TIME,
                        '22:00'::TIME,
                        false,
                        true,  -- Marcación automática de salida
                        false,
                        'Salida marcada automáticamente',
                        NOW(),
                        NOW()
                    ) ON CONFLICT (id_agente, fecha) DO NOTHING;
                END IF;
            END LOOP;
        END LOOP;
    END LOOP;
    
    -- =====================================================
    -- 4. LICENCIAS ADICIONALES
    -- =====================================================
    RAISE NOTICE 'Generando licencias adicionales...';
    
    FOR v_agente IN SELECT id_agente FROM agente WHERE activo = true LIMIT 8 LOOP
        -- Licencias de vacaciones
        INSERT INTO licencia (
            id_agente, id_tipo_licencia, fecha_desde, fecha_hasta,
            estado, justificacion, solicitada_por,
            creado_en, actualizado_en
        ) VALUES (
            v_agente.id_agente,
            (SELECT id_tipo_licencia FROM tipo_licencia WHERE codigo = 'VAC' LIMIT 1),
            DATE('2025-07-15') + (RANDOM() * 60)::INT,
            DATE('2025-07-15') + (RANDOM() * 60)::INT + (3 + (RANDOM() * 4)::INT),
            CASE WHEN RANDOM() > 0.3 THEN 'aprobada' ELSE 'pendiente' END,
            'Vacaciones de verano',
            v_agente.id_agente,
            NOW(),
            NOW()
        );
        
        -- Algunas licencias por enfermedad
        IF RANDOM() > 0.6 THEN
            INSERT INTO licencia (
                id_agente, id_tipo_licencia, fecha_desde, fecha_hasta,
                estado, justificacion, solicitada_por,
                creado_en, actualizado_en
            ) VALUES (
                v_agente.id_agente,
                (SELECT id_tipo_licencia FROM tipo_licencia WHERE codigo = 'ENF' LIMIT 1),
                DATE('2025-09-01') + (RANDOM() * 60)::INT,
                DATE('2025-09-01') + (RANDOM() * 60)::INT + (1 + (RANDOM() * 2)::INT),
                'aprobada',
                'Reposo médico',
                v_agente.id_agente,
                NOW(),
                NOW()
            );
        END IF;
    END LOOP;
    
    -- =====================================================
    -- 5. COMPENSACIONES POR HORAS EXTRA
    -- =====================================================
    RAISE NOTICE 'Generando compensaciones...';
    
    -- Compensaciones para algunos agentes con guardias extendidas
    FOR v_agente IN 
        SELECT DISTINCT g.id_agente, g.id_guardia, g.id_cronograma, g.fecha
        FROM guardia g
        WHERE g.horas_efectivas >= 9
        AND RANDOM() > 0.5
        LIMIT 15
    LOOP
        INSERT INTO hora_compensacion (
            id_agente, id_guardia, id_cronograma,
            fecha_servicio,
            hora_inicio_programada, hora_fin_programada, hora_fin_real,
            horas_programadas, horas_efectivas, horas_extra,
            motivo, descripcion_motivo, numero_acta,
            estado, tipo_compensacion,
            solicitado_por, aprobado_por, fecha_solicitud, fecha_aprobacion,
            creado_en, actualizado_en
        ) VALUES (
            v_agente.id_agente,
            v_agente.id_guardia,
            v_agente.id_cronograma,
            v_agente.fecha,
            '08:00'::TIME,
            '16:00'::TIME,
            '20:00'::TIME + (RANDOM() * INTERVAL '3 hours'),
            8.0,
            12.0 + (RANDOM() * 4)::NUMERIC(4,2),
            4.0 + (RANDOM() * 3)::NUMERIC(4,2),
            CASE (RANDOM() * 4)::INT
                WHEN 0 THEN 'emergencia'
                WHEN 1 THEN 'operativo'
                WHEN 2 THEN 'siniestro'
                ELSE 'refuerzo'
            END,
            'Extensión de guardia por ' || 
            CASE (RANDOM() * 3)::INT
                WHEN 0 THEN 'emergencia vial'
                WHEN 1 THEN 'operativo de control'
                ELSE 'siniestro en ruta'
            END,
            'ACTA-' || TO_CHAR(v_agente.fecha, 'YYYYMMDD') || '-' || LPAD((RANDOM() * 1000)::INT::TEXT, 4, '0'),
            CASE WHEN RANDOM() > 0.2 THEN 'aprobada' ELSE 'pendiente' END,
            CASE (RANDOM() * 2)::INT
                WHEN 0 THEN 'plus'
                WHEN 1 THEN 'pago'
                ELSE 'franco'
            END,
            v_agente.id_agente,
            (SELECT id_agente FROM agente WHERE legajo IN ('003', '007', '008') ORDER BY RANDOM() LIMIT 1),
            v_agente.fecha + INTERVAL '1 day',
            CASE WHEN RANDOM() > 0.2 THEN v_agente.fecha + INTERVAL '3 days' ELSE NULL END,
            NOW(),
            NOW()
        ) ON CONFLICT (id_agente, fecha_servicio, id_cronograma) DO NOTHING;
    END LOOP;
    
    -- =====================================================
    -- 6. NOTAS EN GUARDIAS
    -- =====================================================
    RAISE NOTICE 'Generando notas de guardias...';
    
    FOR v_guardia_id IN 
        SELECT id_guardia, id_agente FROM guardia 
        ORDER BY RANDOM() 
        LIMIT 25
    LOOP
        INSERT INTO nota_guardia (
            id_guardia, contenido, creado_por, fecha_creacion, creado_en, actualizado_en
        ) VALUES (
            v_guardia_id.id_guardia,
            CASE (RANDOM() * 5)::INT
                WHEN 0 THEN 'Operativo de control vehicular en RN3'
                WHEN 1 THEN 'Inspección de habilitaciones en zona centro'
                WHEN 2 THEN 'Coordinación con bomberos para simulacro'
                WHEN 3 THEN 'Atención de accidente en km 25'
                ELSE 'Guardia sin novedades'
            END,
            v_guardia_id.id_agente,
            NOW(),
            NOW(),
            NOW()
        );
    END LOOP;
    
    -- =====================================================
    -- 7. RESUMEN MENSUAL DE PLUS (para algunos meses)
    -- =====================================================
    RAISE NOTICE 'Generando resúmenes mensuales de plus...';
    
    FOR v_mes IN 6..10 LOOP
        FOR v_agente IN SELECT id_agente FROM agente WHERE activo = true LIMIT 10 LOOP
            -- Calcular horas del mes
            DECLARE
                v_horas DECIMAL(6,2);
                v_plus DECIMAL(5,2);
            BEGIN
                SELECT COALESCE(SUM(horas_efectivas), 0) INTO v_horas
                FROM guardia
                WHERE id_agente = v_agente.id_agente
                AND EXTRACT(MONTH FROM fecha) = v_mes
                AND EXTRACT(YEAR FROM fecha) = v_anio;
                
                -- Calcular plus basado en horas
                IF v_horas >= 32 THEN
                    v_plus := 40.0;
                ELSIF v_horas > 0 THEN
                    v_plus := 20.0;
                ELSE
                    v_plus := 0.0;
                END IF;
                
                IF v_horas > 0 THEN
                    INSERT INTO resumen_guardia_mes (
                        id_agente, mes, anio,
                        horas_efectivas, porcentaje_plus, estado_plus,
                        fecha_calculo, aprobado_por, fecha_aprobacion,
                        creado_en, actualizado_en
                    ) VALUES (
                        v_agente.id_agente,
                        v_mes,
                        v_anio,
                        v_horas,
                        v_plus,
                        CASE WHEN v_mes < 10 THEN 'aprobado' ELSE 'pendiente' END,
                        DATE(v_anio || '-' || LPAD((v_mes + 1)::TEXT, 2, '0') || '-05'),
                        CASE WHEN v_mes < 10 THEN (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1) ELSE NULL END,
                        CASE WHEN v_mes < 10 THEN DATE(v_anio || '-' || LPAD((v_mes + 1)::TEXT, 2, '0') || '-10') ELSE NULL END,
                        NOW(),
                        NOW()
                    ) ON CONFLICT (id_agente, mes, anio) DO NOTHING;
                END IF;
            END;
        END LOOP;
    END LOOP;
    
    -- =====================================================
    -- ESTADÍSTICAS FINALES
    -- =====================================================
    SELECT COUNT(*) INTO v_count_cronogramas FROM cronograma;
    SELECT COUNT(*) INTO v_count_guardias FROM guardia;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'DATOS HISTÓRICOS GENERADOS EXITOSAMENTE';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Cronogramas: %', v_count_cronogramas;
    RAISE NOTICE 'Guardias: %', v_count_guardias;
    RAISE NOTICE 'Asistencias: %', (SELECT COUNT(*) FROM asistencia);
    RAISE NOTICE 'Licencias: %', (SELECT COUNT(*) FROM licencia);
    RAISE NOTICE 'Compensaciones: %', (SELECT COUNT(*) FROM hora_compensacion);
    RAISE NOTICE 'Notas: %', (SELECT COUNT(*) FROM nota_guardia);
    RAISE NOTICE 'Resúmenes plus: %', (SELECT COUNT(*) FROM resumen_guardia_mes);
    RAISE NOTICE '========================================';
    
END $$;
