-- ========================================================================
-- SCRIPT: DATOS HISTÓRICOS SIMPLIFICADOS - Sistema GIGA
-- Fecha: 27 de Noviembre 2025
-- Descripción: Genera datos históricos básicos SIN loops complejos
-- ========================================================================

-- =====================================================
-- CRONOGRAMAS (3 meses de datos fijos)
-- =====================================================

INSERT INTO cronograma (
    id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin,
    estado, fecha_creacion, fecha_aprobacion,
    creado_por_rol, creado_por_id, aprobado_por_id,
    creado_en, actualizado_en
) 
SELECT 
    (SELECT id_agente FROM agente WHERE legajo = '004' LIMIT 1),
    (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1),
    (SELECT id_area FROM area LIMIT 1),
    'regular',
    '08:00'::TIME,
    '16:00'::TIME,
    'publicada',
    mes_fecha,
    mes_fecha + INTERVAL '2 days',
    'jefatura',
    (SELECT id_agente FROM agente WHERE legajo = '004' LIMIT 1),
    (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1),

    NOW(),
    NOW()
FROM (VALUES 
    ('2025-09-01'::DATE),
    ('2025-10-01'::DATE),
    ('2025-11-01'::DATE)
) AS meses(mes_fecha);


-- =====================================================
-- GUARDIAS (algunas guardias de ejemplo)
-- =====================================================

INSERT INTO guardia (
    id_cronograma, id_agente, fecha,
    hora_inicio, hora_fin, tipo, estado, activa,
    horas_planificadas, horas_efectivas,
    observaciones, creado_en, actualizado_en
)
SELECT 
    (SELECT id_cronograma FROM cronograma LIMIT 1),
    a.id_agente,
    fecha_guardia,
    '08:00'::TIME,
    '16:00'::TIME,
    'regular',
    'planificada',
    true,
    8,
    8,
    'Guardia de ejemplo',
    NOW(),
    NOW()
FROM agente a
CROSS JOIN (VALUES 
    ('2025-09-15'::DATE),
    ('2025-10-15'::DATE),
    ('2025-11-15'::DATE)
) AS fechas(fecha_guardia)
WHERE a.activo = true
LIMIT 20;

-- =====================================================
-- ASISTENCIAS (algunas asistencias de ejemplo)
-- =====================================================

INSERT INTO asistencia (
    id_agente, id_area, fecha,
    hora_entrada, hora_salida,
    marcacion_entrada_automatica, marcacion_salida_automatica,
    es_correccion, observaciones,
    creado_en, actualizado_en
)
SELECT 
    a.id_agente,
    a.id_area,
    fecha_asist,
    '08:15'::TIME,
    '17:00'::TIME,
    false,
    false,
    false,
    '',
    NOW(),
    NOW()
FROM agente a
CROSS JOIN (VALUES 
    ('2025-11-01'::DATE),
    ('2025-11-04'::DATE),
    ('2025-11-05'::DATE),
    ('2025-11-06'::DATE),
    ('2025-11-07'::DATE),
    ('2025-11-08'::DATE)
) AS fechas(fecha_asist)
WHERE a.activo = true
LIMIT 30
ON CONFLICT (id_agente, fecha) DO NOTHING;

-- =====================================================
-- LICENCIAS ADICIONALES (fechas fijas correctas)
-- =====================================================

INSERT INTO licencia (
    id_agente, id_tipo_licencia, fecha_desde, fecha_hasta,
    estado, justificacion, solicitada_por,
    creado_en, actualizado_en
)
SELECT 
    a.id_agente,
    (SELECT id_tipo_licencia FROM tipo_licencia WHERE codigo = 'VAC' LIMIT 1),
    '2025-12-15'::DATE,
    '2025-12-20'::DATE,
    'pendiente',
    'Vacaciones fin de año',
    a.id_agente,
    NOW(),
    NOW()
FROM agente a
WHERE a.activo = true
LIMIT 3;

-- =====================================================
-- MENSAJE DE CONFIRMACIÓN
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'DATOS HISTÓRICOS GENERADOS';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Cronogramas: %', (SELECT COUNT(*) FROM cronograma);
    RAISE NOTICE 'Guardias: %', (SELECT COUNT(*) FROM guardia);
    RAISE NOTICE 'Asistencias: %', (SELECT COUNT(*) FROM asistencia);
    RAISE NOTICE 'Licencias: %', (SELECT COUNT(*) FROM licencia);
    RAISE NOTICE '========================================';
END $$;
