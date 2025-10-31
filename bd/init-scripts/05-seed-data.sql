-- =====================================================
-- DATOS REALES DEL SISTEMA GIGA - PROTECCIÓN CIVIL
-- Adaptados a la estructura actual de tablas
-- =====================================================

-- Primero limpiar los datos básicos e insertar los correctos
-- Reemplazar roles básicos con roles reales
DELETE FROM rol WHERE nombre IN ('administrador', 'jefe', 'director', 'agente', 'supervisor');
INSERT INTO rol (nombre, descripcion) VALUES 
    ('Administrador', 'Acceso total al sistema, gestión de usuarios y configuración'),
    ('Director', 'Valida y aprueba cronogramas, accede a reportes globales'),
    ('Jefatura', 'Planifica cronogramas mensuales, gestiona y supervisa equipos'),
    ('Agente Avanzado', 'Carga asistencia y novedades de su equipo, además de funciones de agente'),
    ('Agente', 'Consulta su ficha, parte diario, guardias y plus asignado')
ON CONFLICT (nombre) DO NOTHING;

-- Limpiar tipos de licencia e insertar los reales
DELETE FROM tipo_licencia WHERE codigo IN ('ANUAL', 'ENFERMEDAD', 'MATERNIDAD', 'PATERNIDAD', 'ESPECIAL', 'ESTUDIO', 'FALLECIMIENTO', 'CASAMIENTO');
INSERT INTO tipo_licencia (codigo, descripcion) VALUES 
    ('VAC', 'Vacaciones - Licencia por vacaciones anuales'),
    ('ENF', 'Enfermedad - Licencia por enfermedad o motivos médicos'),
    ('PER', 'Personal - Licencia por motivos personales')
ON CONFLICT (codigo) DO NOTHING;

-- Limpiar área por defecto e insertar área real
DELETE FROM area WHERE nombre = 'General';
INSERT INTO area (nombre, activo) VALUES 
    ('Secretaría de Protección Civil', true)
ON CONFLICT (nombre) DO NOTHING;

-- Insertar datos usando DO block para manejar las referencias correctamente
DO $$
DECLARE
    area_id BIGINT;
    rol_admin_id BIGINT;
    rol_director_id BIGINT;
    rol_jefe_id BIGINT;
    rol_avanzado_id BIGINT;
    rol_agente_id BIGINT;
    tipo_vac_id BIGINT;
    tipo_enf_id BIGINT;
    tipo_per_id BIGINT;
BEGIN
    -- Obtener IDs necesarios
    SELECT id_area INTO area_id FROM area WHERE nombre = 'Secretaría de Protección Civil' LIMIT 1;
    SELECT id_rol INTO rol_admin_id FROM rol WHERE nombre = 'Administrador' LIMIT 1;
    SELECT id_rol INTO rol_director_id FROM rol WHERE nombre = 'Director' LIMIT 1;
    SELECT id_rol INTO rol_jefe_id FROM rol WHERE nombre = 'Jefatura' LIMIT 1;
    SELECT id_rol INTO rol_avanzado_id FROM rol WHERE nombre = 'Agente Avanzado' LIMIT 1;
    SELECT id_rol INTO rol_agente_id FROM rol WHERE nombre = 'Agente' LIMIT 1;
    
    SELECT id_tipo_licencia INTO tipo_vac_id FROM tipo_licencia WHERE codigo = 'VAC' LIMIT 1;
    SELECT id_tipo_licencia INTO tipo_enf_id FROM tipo_licencia WHERE codigo = 'ENF' LIMIT 1;
    SELECT id_tipo_licencia INTO tipo_per_id FROM tipo_licencia WHERE codigo = 'PER' LIMIT 1;
    
    -- Insertar agentes reales adaptados a la estructura actual
    INSERT INTO agente (
        legajo, nombre, apellido, email, dni, cuil, password_hash, telefono, 
        fecha_nacimiento, provincia, ciudad, calle, numero, 
        agrupacion, activo, id_area
    ) VALUES 
        ('001', 'Tayra', 'Aguila', 'tayra.aguila@proteccioncivil.tdf.gov.ar', 
         '12345678', '27123456784','pbkdf2_sha256$1000000$TDYqnUwElaDks7JCXRHmjZ$DognNfhfOXm6tCZJ/BRJrez+cteBVqiH1DIal5dMeiU=', 
         '2964123456', '1990-01-15', 'Tierra del Fuego', 'Ushuaia', 'San Martín', '123', 
         'EPU', true, area_id),
        
        ('002', 'Micaela', 'Alvarado', 'micaela.alvarado@proteccioncivil.tdf.gov.ar', 
         '23456789', '27234567894','pbkdf2_sha256$1000000$9ZD1gGhiDBST9A5HUZQsd9$8owfKPCKi7nRbvvZGfSARgBZoLDmX0bfh5Bwf92SryE=', 
         '2964234567', '1985-03-22', 'Tierra del Fuego', 'Ushuaia', 'Belgrano', '456', 
         'EPU', true, area_id),
         
        ('003', 'Cristian', 'Garcia', 'cristian.garcia@proteccioncivil.tdf.gov.ar', 
         '34567890', '27345678904','pbkdf2_sha256$1000000$3MNefVZa2AIQDYGyaSLQcT$EtkU+jh7MbxVbQhQj73YuWu+qQhRVCsCwIJKyd6dtXc=', 
         '2964345678', '1988-07-10', 'Tierra del Fuego', 'Ushuaia', 'Rivadavia', '789', 
         'POMYS', true, area_id),
         
        ('004', 'Leandro', 'Gomez', 'leandro.gomez@proteccioncivil.tdf.gov.ar', 
         '45678901', '27456789014','pbkdf2_sha256$1000000$P8Buwpis9Cm8HLGxW0ndoX$qJxR0ex+s9TPGy76d2OsOf2uPKMz3Wk1NYSppuhdr1I=', 
         '2964456789', '1992-11-05', 'Tierra del Fuego', 'Ushuaia', 'Maipú', '321', 
         'PAYT', true, area_id),
         
        ('005', 'Teresa', 'Criniti', 'teresa.criniti@proteccioncivil.tdf.gov.ar', 
         '56789012','27567890124', 'pbkdf2_sha256$1000000$cY78hNwJKXCLijREgLFggk$AkHqFVGitqHl/orwTLr74pqEeU+JN2kAAJk7r0TsN7k=', 
         '2964567890', '1980-09-18', 'Tierra del Fuego', 'Ushuaia', 'Yaganes', '654', 
         'EPU', true, area_id),
         
        ('006', 'Pamela', 'Frers', 'pamela.frers@proteccioncivil.tdf.gov.ar', 
         '67890123', '27678901234', 'pbkdf2_sha256$1000000$PR3R1yPZeUhy1a1oY3Vj0W$WxsEWCjKX8nEMFmJ7wBsUXZkRFrvox0x4UBoc/b0BAk=', 
         '2964678901', '1995-12-30', 'Tierra del Fuego', 'Ushuaia', 'Onashaga', '987', 
         'POMYS', true, area_id)
    ON CONFLICT (legajo) DO NOTHING;
    
    -- Asignar roles usando la tabla agente_rol (estructura actual)
    INSERT INTO agente_rol (id_agente, id_rol) VALUES
        ((SELECT id_agente FROM agente WHERE legajo = '001'), rol_admin_id),    -- Tayra: Administrador
        ((SELECT id_agente FROM agente WHERE legajo = '002'), rol_admin_id),    -- Micaela: Administrador  
        ((SELECT id_agente FROM agente WHERE legajo = '003'), rol_director_id), -- Cristian: Director
        ((SELECT id_agente FROM agente WHERE legajo = '004'), rol_jefe_id),     -- Leandro: Jefatura
        ((SELECT id_agente FROM agente WHERE legajo = '005'), rol_avanzado_id), -- Teresa: Agente Avanzado
        ((SELECT id_agente FROM agente WHERE legajo = '006'), rol_agente_id)    -- Pamela: Agente
    ON CONFLICT (id_agente, id_rol) DO NOTHING;
    
    -- Insertar licencias adaptadas a estructura actual (campos: id_licencia, estado, id_tipo_licencia, fecha_desde, fecha_hasta, id_agente)
    INSERT INTO licencia (id_agente, id_tipo_licencia, fecha_desde, fecha_hasta, estado) VALUES 
        -- Licencias de Tayra Aguila 
        ((SELECT id_agente FROM agente WHERE legajo = '001'), tipo_vac_id, '2025-02-15', '2025-02-17', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '001'), tipo_enf_id, '2025-04-10', '2025-04-10', 'aprobada'),
         
        -- Licencias de Micaela Alvarado
        ((SELECT id_agente FROM agente WHERE legajo = '002'), tipo_per_id, '2025-03-05', '2025-03-05', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '002'), tipo_vac_id, '2025-06-20', '2025-06-24', 'aprobada'),
         
        -- Licencias de Cristian Garcia
        ((SELECT id_agente FROM agente WHERE legajo = '003'), tipo_enf_id, '2025-01-25', '2025-01-25', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '003'), tipo_vac_id, '2025-05-12', '2025-05-16', 'pendiente'),
         
        -- Licencias de Leandro Gomez
        ((SELECT id_agente FROM agente WHERE legajo = '004'), tipo_per_id, '2025-02-28', '2025-02-28', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '004'), tipo_vac_id, '2025-08-01', '2025-08-03', 'pendiente'),
         
        -- Licencias de Teresa Criniti
        ((SELECT id_agente FROM agente WHERE legajo = '005'), tipo_enf_id, '2025-03-15', '2025-03-17', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '005'), tipo_vac_id, '2025-07-07', '2025-07-11', 'pendiente'),
         
        -- Licencias de Pamela Frers
        ((SELECT id_agente FROM agente WHERE legajo = '006'), tipo_enf_id, '2025-04-22', '2025-04-22', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '006'), tipo_vac_id, '2025-09-01', '2025-09-05', 'pendiente');
    
END $$;

-- =====================================================
-- VERIFICACIONES DE INTEGRIDAD
-- =====================================================

-- Verificar conteos de registros
SELECT 'Resumen de datos insertados:' as status;
SELECT 
    (SELECT COUNT(*) FROM area) as total_areas,
    (SELECT COUNT(*) FROM rol) as total_roles,
    (SELECT COUNT(*) FROM tipo_licencia) as total_tipos_licencia,
    (SELECT COUNT(*) FROM agente) as total_agentes,
    (SELECT COUNT(*) FROM agente_rol) as total_asignaciones_rol,
    (SELECT COUNT(*) FROM licencia) as total_licencias;

-- Verificar agentes con sus roles asignados
SELECT 
    a.legajo,
    CONCAT(a.nombre, ' ', a.apellido) as nombre_completo,
    a.email,
    r.nombre as rol,
    COUNT(l.id_licencia) as total_licencias
FROM agente a 
LEFT JOIN agente_rol ar ON a.id_agente = ar.id_agente
LEFT JOIN rol r ON ar.id_rol = r.id_rol
LEFT JOIN licencia l ON a.id_agente = l.id_agente
GROUP BY a.id_agente, a.legajo, a.nombre, a.apellido, a.email, r.nombre
ORDER BY a.legajo;

-- Verificar tipos de licencia utilizados
SELECT 
    tl.codigo,
    tl.descripcion,
    COUNT(l.id_licencia) as licencias_registradas
FROM tipo_licencia tl
LEFT JOIN licencia l ON tl.id_tipo_licencia = l.id_tipo_licencia
GROUP BY tl.id_tipo_licencia, tl.codigo, tl.descripcion
ORDER BY tl.codigo;

-- Actualizar secuencias para próximas inserciones
SELECT setval('area_id_area_seq', COALESCE((SELECT MAX(id_area) FROM area), 1), true);
SELECT setval('rol_id_rol_seq', COALESCE((SELECT MAX(id_rol) FROM rol), 1), true);
SELECT setval('tipo_licencia_id_tipo_licencia_seq', COALESCE((SELECT MAX(id_tipo_licencia) FROM tipo_licencia), 1), true);
SELECT setval('agente_id_agente_seq', COALESCE((SELECT MAX(id_agente) FROM agente), 1), true);
SELECT setval('agente_rol_id_agente_rol_seq', COALESCE((SELECT MAX(id_agente_rol) FROM agente_rol), 1), true);
SELECT setval('licencia_id_licencia_seq', COALESCE((SELECT MAX(id_licencia) FROM licencia), 1), true);

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'MIGRACIÓN DE DATOS COMPLETADA EXITOSAMENTE - Sistema GIGA Protección Civil';
END $$;