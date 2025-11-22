-- Script CORREGIDO para generar guardias históricas para desarrollo y testing de reportes
-- Sistema GIGA - Datos de prueba realistas

-- Verificar estructura de datos existente
DO $$
BEGIN
    RAISE NOTICE 'Iniciando generación de guardias históricas...';
    RAISE NOTICE 'Agentes disponibles: %', (SELECT COUNT(*) FROM agente WHERE activo = true);
    RAISE NOTICE 'Áreas disponibles: %', (SELECT COUNT(*) FROM area WHERE activo = true);
END $$;

-- 1. CRONOGRAMAS BASE (uno por mes y tipo)
INSERT INTO cronograma (
    id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin, 
    estado, fecha_creacion, fecha_aprobacion, creado_por_rol, creado_por_id, aprobado_por_id,
    creado_en, actualizado_en
) VALUES 
-- Cronogramas Junio 2025
(1, 1, 1, 'regular', '08:00', '16:00', 'publicada', '2025-06-01', '2025-06-02', 'administrador', 1, 1, NOW(), NOW()),
(7, 7, 2, 'especial', '06:00', '14:00', 'publicada', '2025-06-01', '2025-06-02', 'jefatura', 7, 1, NOW(), NOW()),
(8, 8, 3, 'emergencia', '14:00', '22:00', 'publicada', '2025-06-01', '2025-06-02', 'jefatura', 8, 1, NOW(), NOW()),

-- Cronogramas Julio 2025  
(1, 1, 1, 'regular', '08:00', '16:00', 'publicada', '2025-07-01', '2025-07-02', 'administrador', 1, 1, NOW(), NOW()),
(7, 7, 2, 'nocturna', '22:00', '06:00', 'publicada', '2025-07-01', '2025-07-02', 'jefatura', 7, 1, NOW(), NOW()),
(9, 9, 4, 'especial', '10:00', '18:00', 'publicada', '2025-07-01', '2025-07-02', 'jefatura', 9, 1, NOW(), NOW()),

-- Cronogramas Agosto 2025
(1, 1, 1, 'regular', '08:00', '16:00', 'publicada', '2025-08-01', '2025-08-02', 'administrador', 1, 1, NOW(), NOW()),
(11, 11, 9, 'administrativa', '09:00', '17:00', 'publicada', '2025-08-01', '2025-08-02', 'jefatura', 11, 1, NOW(), NOW()),
(10, 10, 5, 'operativa', '07:00', '15:00', 'publicada', '2025-08-01', '2025-08-02', 'jefatura', 10, 1, NOW(), NOW()),

-- Cronogramas Septiembre 2025
(1, 1, 1, 'regular', '08:00', '16:00', 'publicada', '2025-09-01', '2025-09-02', 'administrador', 1, 1, NOW(), NOW()),
(2, 2, 1, 'especial', '16:00', '00:00', 'publicada', '2025-09-01', '2025-09-02', 'jefatura', 2, 1, NOW(), NOW()),
(7, 7, 2, 'regular', '08:00', '16:00', 'publicada', '2025-09-01', '2025-09-02', 'jefatura', 7, 1, NOW(), NOW()),

-- Cronogramas Octubre 2025
(1, 1, 1, 'regular', '08:00', '16:00', 'publicada', '2025-10-01', '2025-10-02', 'administrador', 1, 1, NOW(), NOW()),
(8, 8, 3, 'emergencia', '12:00', '20:00', 'publicada', '2025-10-01', '2025-10-02', 'jefatura', 8, 1, NOW(), NOW()),
(12, 12, 6, 'especial', '06:00', '14:00', 'publicada', '2025-10-01', '2025-10-02', 'jefatura', 12, 1, NOW(), NOW());

-- 2. GUARDIAS HISTÓRICAS 

-- JUNIO 2025 - Secretaría de Protección Civil
INSERT INTO guardia (id_cronograma, id_agente, fecha, hora_inicio, hora_fin, tipo, estado, activa, 
                     horas_planificadas, horas_efectivas, observaciones, creado_en, actualizado_en) VALUES
-- Guardias regulares junio (70% con presentismo)
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 1, '2025-06-02', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 2, '2025-06-05', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, 'Salió temprano', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 3, '2025-06-08', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 4, '2025-06-11', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 5, '2025-06-14', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 6, '2025-06-17', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 1, '2025-06-20', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 2, '2025-06-23', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 3, '2025-06-26', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-06-01' AND id_area = 1 LIMIT 1), 4, '2025-06-29', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),

-- Guardias especiales área 2
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-06-01' AND id_area = 2 LIMIT 1), 7, '2025-06-05', '06:00', '14:00', 'especial', 'planificada', true, 8, 8, 'Operativo especial', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-06-01' AND id_area = 2 LIMIT 1), 7, '2025-06-12', '06:00', '14:00', 'especial', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-06-01' AND id_area = 2 LIMIT 1), 7, '2025-06-19', '06:00', '14:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW()),

-- Emergencias área 3
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-06-01' AND id_area = 3 LIMIT 1), 8, '2025-06-03', '14:00', '22:00', 'emergencia', 'planificada', true, 8, NULL, 'Emergencia vial', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-06-01' AND id_area = 3 LIMIT 1), 8, '2025-06-17', '14:00', '22:00', 'emergencia', 'planificada', true, 8, 8, '', NOW(), NOW());

-- JULIO 2025 - Más guardias (80% con presentismo)
INSERT INTO guardia (id_cronograma, id_agente, fecha, hora_inicio, hora_fin, tipo, estado, activa, 
                     horas_planificadas, horas_efectivas, observaciones, creado_en, actualizado_en) VALUES
-- Regulares julio
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 1, '2025-07-01', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 2, '2025-07-03', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 3, '2025-07-05', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 4, '2025-07-08', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 5, '2025-07-10', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 6, '2025-07-12', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 1, '2025-07-15', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 2, '2025-07-17', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 3, '2025-07-19', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 4, '2025-07-22', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 5, '2025-07-24', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 6, '2025-07-26', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 1, '2025-07-29', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-07-01' AND id_area = 1 LIMIT 1), 2, '2025-07-31', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),

-- Nocturnas julio
((SELECT id_cronograma FROM cronograma WHERE tipo = 'nocturna' AND fecha_creacion = '2025-07-01' AND id_area = 2 LIMIT 1), 7, '2025-07-02', '22:00', '06:00', 'nocturna', 'planificada', true, 8, 8, 'Guardia nocturna completa', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'nocturna' AND fecha_creacion = '2025-07-01' AND id_area = 2 LIMIT 1), 7, '2025-07-09', '22:00', '06:00', 'nocturna', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'nocturna' AND fecha_creacion = '2025-07-01' AND id_area = 2 LIMIT 1), 7, '2025-07-16', '22:00', '06:00', 'nocturna', 'planificada', true, 8, 7, 'Salida anticipada', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'nocturna' AND fecha_creacion = '2025-07-01' AND id_area = 2 LIMIT 1), 7, '2025-07-23', '22:00', '06:00', 'nocturna', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'nocturna' AND fecha_creacion = '2025-07-01' AND id_area = 2 LIMIT 1), 7, '2025-07-30', '22:00', '06:00', 'nocturna', 'planificada', true, 8, 8, '', NOW(), NOW()),

-- Especiales área 4
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-07-01' AND id_area = 4 LIMIT 1), 9, '2025-07-06', '10:00', '18:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-07-01' AND id_area = 4 LIMIT 1), 9, '2025-07-13', '10:00', '18:00', 'especial', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-07-01' AND id_area = 4 LIMIT 1), 9, '2025-07-20', '10:00', '18:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-07-01' AND id_area = 4 LIMIT 1), 9, '2025-07-27', '10:00', '18:00', 'especial', 'planificada', true, 8, NULL, '', NOW(), NOW());

-- AGOSTO 2025 - Múltiples áreas (60% presentismo)
INSERT INTO guardia (id_cronograma, id_agente, fecha, hora_inicio, hora_fin, tipo, estado, activa, 
                     horas_planificadas, horas_efectivas, observaciones, creado_en, actualizado_en) VALUES
-- Regulares agosto área 1
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 1, '2025-08-01', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 2, '2025-08-05', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 3, '2025-08-09', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 4, '2025-08-13', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 5, '2025-08-17', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 6, '2025-08-21', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 1, '2025-08-25', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-08-01' AND id_area = 1 LIMIT 1), 2, '2025-08-29', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),

-- Administrativas área 9
((SELECT id_cronograma FROM cronograma WHERE tipo = 'administrativa' AND fecha_creacion = '2025-08-01' AND id_area = 9 LIMIT 1), 11, '2025-08-02', '09:00', '17:00', 'administrativa', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'administrativa' AND fecha_creacion = '2025-08-01' AND id_area = 9 LIMIT 1), 11, '2025-08-09', '09:00', '17:00', 'administrativa', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'administrativa' AND fecha_creacion = '2025-08-01' AND id_area = 9 LIMIT 1), 11, '2025-08-16', '09:00', '17:00', 'administrativa', 'planificada', true, 8, NULL, 'Faltó marcar salida', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'administrativa' AND fecha_creacion = '2025-08-01' AND id_area = 9 LIMIT 1), 11, '2025-08-23', '09:00', '17:00', 'administrativa', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'administrativa' AND fecha_creacion = '2025-08-01' AND id_area = 9 LIMIT 1), 11, '2025-08-30', '09:00', '17:00', 'administrativa', 'planificada', true, 8, 7, '', NOW(), NOW()),

-- Operativas área 5  
((SELECT id_cronograma FROM cronograma WHERE tipo = 'operativa' AND fecha_creacion = '2025-08-01' AND id_area = 5 LIMIT 1), 10, '2025-08-03', '07:00', '15:00', 'operativa', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'operativa' AND fecha_creacion = '2025-08-01' AND id_area = 5 LIMIT 1), 10, '2025-08-10', '07:00', '15:00', 'operativa', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'operativa' AND fecha_creacion = '2025-08-01' AND id_area = 5 LIMIT 1), 10, '2025-08-17', '07:00', '15:00', 'operativa', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'operativa' AND fecha_creacion = '2025-08-01' AND id_area = 5 LIMIT 1), 10, '2025-08-24', '07:00', '15:00', 'operativa', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'operativa' AND fecha_creacion = '2025-08-01' AND id_area = 5 LIMIT 1), 10, '2025-08-31', '07:00', '15:00', 'operativa', 'planificada', true, 8, 7, '', NOW(), NOW());

-- SEPTIEMBRE 2025 - Temporada alta (85% presentismo)
INSERT INTO guardia (id_cronograma, id_agente, fecha, hora_inicio, hora_fin, tipo, estado, activa, 
                     horas_planificadas, horas_efectivas, observaciones, creado_en, actualizado_en) VALUES
-- Regulares septiembre área 1
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 1, '2025-09-02', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 2, '2025-09-05', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 3, '2025-09-09', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 4, '2025-09-12', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 5, '2025-09-16', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 6, '2025-09-19', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 1, '2025-09-23', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 2, '2025-09-26', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 3, '2025-09-30', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),

-- Especiales nocturnas área 1
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 2, '2025-09-07', '16:00', '00:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 2, '2025-09-14', '16:00', '00:00', 'especial', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 2, '2025-09-21', '16:00', '00:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-09-01' AND id_area = 1 LIMIT 1), 2, '2025-09-28', '16:00', '00:00', 'especial', 'planificada', true, 8, NULL, '', NOW(), NOW()),

-- Área 2 regulares
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 2 LIMIT 1), 7, '2025-09-03', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 2 LIMIT 1), 7, '2025-09-10', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 2 LIMIT 1), 7, '2025-09-17', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-09-01' AND id_area = 2 LIMIT 1), 7, '2025-09-24', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW());

-- OCTUBRE 2025 - Variedad completa (75% presentismo)
INSERT INTO guardia (id_cronograma, id_agente, fecha, hora_inicio, hora_fin, tipo, estado, activa, 
                     horas_planificadas, horas_efectivas, observaciones, creado_en, actualizado_en) VALUES
-- Área 1 regulares octubre
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 1, '2025-10-01', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 2, '2025-10-03', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 3, '2025-10-07', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 4, '2025-10-10', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 5, '2025-10-14', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 6, '2025-10-17', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 1, '2025-10-21', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 2, '2025-10-24', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 3, '2025-10-28', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion = '2025-10-01' AND id_area = 1 LIMIT 1), 4, '2025-10-31', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),

-- Emergencias área 3
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-10-01' AND id_area = 3 LIMIT 1), 8, '2025-10-02', '12:00', '20:00', 'emergencia', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-10-01' AND id_area = 3 LIMIT 1), 8, '2025-10-09', '12:00', '20:00', 'emergencia', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-10-01' AND id_area = 3 LIMIT 1), 8, '2025-10-16', '12:00', '20:00', 'emergencia', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-10-01' AND id_area = 3 LIMIT 1), 8, '2025-10-23', '12:00', '20:00', 'emergencia', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'emergencia' AND fecha_creacion = '2025-10-01' AND id_area = 3 LIMIT 1), 8, '2025-10-30', '12:00', '20:00', 'emergencia', 'planificada', true, 8, 8, '', NOW(), NOW()),

-- Especiales área 6
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-10-01' AND id_area = 6 LIMIT 1), 12, '2025-10-05', '06:00', '14:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-10-01' AND id_area = 6 LIMIT 1), 12, '2025-10-12', '06:00', '14:00', 'especial', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-10-01' AND id_area = 6 LIMIT 1), 12, '2025-10-19', '06:00', '14:00', 'especial', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'especial' AND fecha_creacion = '2025-10-01' AND id_area = 6 LIMIT 1), 12, '2025-10-26', '06:00', '14:00', 'especial', 'planificada', true, 8, 8, '', NOW(), NOW());

-- NOVIEMBRE 2025 - Mes actual (90% presentismo)
-- Las guardias existentes ya están en la base, agregamos más...
INSERT INTO guardia (id_cronograma, id_agente, fecha, hora_inicio, hora_fin, tipo, estado, activa, 
                     horas_planificadas, horas_efectivas, observaciones, creado_en, actualizado_en) VALUES
-- Guardias adicionales noviembre (verificar no duplicar fechas existentes)
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion >= '2025-11-01' AND id_area = 1 LIMIT 1), 4, '2025-11-07', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion >= '2025-11-01' AND id_area = 1 LIMIT 1), 5, '2025-11-12', '08:00', '16:00', 'regular', 'planificada', true, 8, 7, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion >= '2025-11-01' AND id_area = 1 LIMIT 1), 6, '2025-11-14', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion >= '2025-11-01' AND id_area = 1 LIMIT 1), 1, '2025-11-19', '08:00', '16:00', 'regular', 'planificada', true, 8, NULL, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion >= '2025-11-01' AND id_area = 1 LIMIT 1), 2, '2025-11-26', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW()),
((SELECT id_cronograma FROM cronograma WHERE tipo = 'regular' AND fecha_creacion >= '2025-11-01' AND id_area = 1 LIMIT 1), 3, '2025-11-28', '08:00', '16:00', 'regular', 'planificada', true, 8, 8, '', NOW(), NOW());

-- 3. ESTADÍSTICAS FINALES
DO $$
DECLARE
    total_guardias INTEGER;
    guardias_con_presentismo INTEGER;
    total_agentes INTEGER;
    total_areas INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_guardias FROM guardia WHERE fecha >= '2025-06-01';
    SELECT COUNT(*) INTO guardias_con_presentismo FROM guardia WHERE fecha >= '2025-06-01' AND horas_efectivas IS NOT NULL;
    SELECT COUNT(DISTINCT id_agente) INTO total_agentes FROM guardia WHERE fecha >= '2025-06-01';
    SELECT COUNT(DISTINCT c.id_area) INTO total_areas FROM guardia g 
        JOIN cronograma c ON g.id_cronograma = c.id_cronograma WHERE g.fecha >= '2025-06-01';
    
    RAISE NOTICE '=== RESUMEN DE DATOS GENERADOS ===';
    RAISE NOTICE 'Período: Junio 2025 - Noviembre 2025';
    RAISE NOTICE 'Total guardias generadas: %', total_guardias;
    RAISE NOTICE 'Guardias con presentismo: % (% %%)', guardias_con_presentismo, 
                 ROUND((guardias_con_presentismo::numeric / total_guardias * 100), 1);
    RAISE NOTICE 'Agentes involucrados: %', total_agentes;
    RAISE NOTICE 'Áreas con guardias: %', total_areas;
    RAISE NOTICE '==============================';
END $$;