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

-- Limpiar área por defecto e insertar estructura jerárquica completa
DELETE FROM area WHERE nombre = 'General';

-- Insertar estructura jerárquica completa de Protección Civil
-- Nivel 1: Secretaría
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Secretaría de Protección Civil', 'Secretaría principal de Protección Civil de Tierra del Fuego', NULL, 1, true);

-- Nivel 2: Subsecretaría
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Subsecretaría de Seguridad Vial', 'Subsecretaría encargada de la seguridad vial provincial', 
     (SELECT id_area FROM area WHERE nombre = 'Secretaría de Protección Civil'), 2, true);

-- Nivel 3: Direcciones Provinciales
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Dirección Provincial de Seguridad Vial', 'Dirección principal de seguridad vial provincial', 
     (SELECT id_area FROM area WHERE nombre = 'Subsecretaría de Seguridad Vial'), 3, true);

-- Nivel 4: Direcciones Generales y Operativas
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    -- Dirección General de Planificación
    ('Dirección General de Planificación de Transporte y Seguridad Vial', 'Planificación estratégica del transporte y seguridad vial', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true),
    
    -- Direcciones Operativas
    ('Dirección Operativa y Seguridad Vial Zona Norte', 'Operaciones de seguridad vial en zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true),
    
    ('Dirección Operativa y Seguridad Vial Zona Sur', 'Operaciones de seguridad vial en zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true),
    
    -- Direcciones de Habilitaciones
    ('Dirección Habilitaciones Zona Norte', 'Habilitaciones y permisos zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true),
    
    ('Dirección Habilitaciones Zona Sur', 'Habilitaciones y permisos zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true),
    
    -- Dirección Administrativa
    ('Dirección Administrativa y Contable', 'Administración y contabilidad general', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true),
    
    -- Dirección Observatorio
    ('Dirección Observatorio Vial', 'Observatorio y estadísticas de seguridad vial', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial'), 4, true);

-- Nivel 5: Subdirecciones y Departamentos principales
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    -- Subdirección bajo Dirección General de Planificación
    ('Subdirección General de Planificación de Transporte y Seguridad Vial', 'Subdirección de planificación operativa', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección General de Planificación de Transporte y Seguridad Vial'), 5, true),
    
    -- Departamentos Operativos
    ('Departamento Operativo Zona Norte', 'Departamento de operaciones zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Operativa y Seguridad Vial Zona Norte'), 5, true),
    
    ('Departamento Operativo Zona Sur', 'Departamento de operaciones zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Operativa y Seguridad Vial Zona Sur'), 5, true),
    
    -- Departamentos de Habilitaciones Zona Norte
    ('Departamento Habilitaciones Zona Norte', 'Departamento de habilitaciones zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Norte'), 5, true),
    
    ('Departamento Inspección Zona Norte', 'Departamento de inspección zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Norte'), 5, true),
    
    -- Departamentos de Habilitaciones Zona Sur
    ('Departamento Habilitaciones Zona Sur', 'Departamento de habilitaciones zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Sur'), 5, true),
    
    ('Departamento Habilitaciones Zona Centro', 'Departamento de habilitaciones zona centro', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Sur'), 5, true),
    
    ('Departamento Inspección Zona Sur', 'Departamento de inspección zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Sur'), 5, true),
    
    ('Departamento Inspección Zona Centro', 'Departamento de inspección zona centro', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Sur'), 5, true),
    
    -- Departamentos Administrativos
    ('Departamento Administrativo y Contable', 'Departamento principal administrativo y contable', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Administrativa y Contable'), 5, true),
    
    ('Departamento Administración y Mesa de Entradas Zona Norte', 'Administración y mesa de entradas zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Administrativa y Contable'), 5, true),
    
    ('Departamento de Recursos Humanos', 'Gestión de recursos humanos', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Administrativa y Contable'), 5, true),
    
    -- Departamentos del Observatorio
    ('Departamento RePAT Zona Norte', 'Registro Provincial de Antecedentes de Tránsito zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Observatorio Vial'), 5, true),
    
    ('Departamento RePAT Zona Sur', 'Registro Provincial de Antecedentes de Tránsito zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Observatorio Vial'), 5, true),
    
    ('Departamento Promoción y Difusión', 'Promoción y difusión de seguridad vial', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Observatorio Vial'), 5, true);

-- Nivel 6: Departamentos bajo Subdirección y Divisiones
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    -- Departamento bajo Subdirección General
    ('Departamento de Planificación', 'Departamento de planificación estratégica', 
     (SELECT id_area FROM area WHERE nombre = 'Subdirección General de Planificación de Transporte y Seguridad Vial'), 6, true),
    
    -- División bajo Departamento RePAT Zona Norte
    ('División RePAT Zona Norte', 'División operativa del RePAT zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Departamento RePAT Zona Norte'), 6, true);

-- Nivel 7: Divisiones bajo Departamento de Planificación
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('División de Planificación', 'División operativa de planificación', 
     (SELECT id_area FROM area WHERE nombre = 'Departamento de Planificación'), 7, true),
    
    ('División de Choferes Zona Norte', 'División de gestión de choferes zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Departamento de Planificación'), 7, true),
    
    ('División de Choferes Zona Sur', 'División de gestión de choferes zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Departamento de Planificación'), 7, true);

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
         'POMYS', true, area_id),
         
        -- Agentes adicionales para diferentes áreas
        ('007', 'Roberto', 'Martinez', 'roberto.martinez@proteccioncivil.tdf.gov.ar', 
         '78901234', '27789012344', 'pbkdf2_sha256$1000000$8B2E7f9Q4R5T6U7V8W9X0Y$1ZaAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTu=', 
         '2964789012', '1987-04-12', 'Tierra del Fuego', 'Ushuaia', 'Prefectura Naval', '234', 
         'EPU', true, (SELECT id_area FROM area WHERE nombre = 'Subsecretaría de Seguridad Vial')),
         
        ('008', 'Sandra', 'Lopez', 'sandra.lopez@proteccioncivil.tdf.gov.ar', 
         '89012345', '27890123454', 'pbkdf2_sha256$1000000$9C3F8g0R5S6T7U8V9W0X1Y$2AbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVw=', 
         '2964890123', '1991-08-25', 'Tierra del Fuego', 'Ushuaia', 'Karukinka', '456', 
         'POMYS', true, (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial')),
         
        ('009', 'Carlos', 'Rodriguez', 'carlos.rodriguez@proteccioncivil.tdf.gov.ar', 
         '90123456', '27901234564', 'pbkdf2_sha256$1000000$0D4G9h1S6T7U8V9W0X1Y2Z$3BcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXy=', 
         '2964901234', '1984-06-18', 'Tierra del Fuego', 'Ushuaia', '25 de Mayo', '789', 
         'PAYT', true, (SELECT id_area FROM area WHERE nombre = 'Departamento Operativo Zona Norte')),
         
        ('010', 'María', 'Fernandez', 'maria.fernandez@proteccioncivil.tdf.gov.ar', 
         '01234567', '27012345674', 'pbkdf2_sha256$1000000$1E5H0i2T7U8V9W0X1Y2Z3A$4CdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXyZa=', 
         '2964012345', '1989-12-03', 'Tierra del Fuego', 'Ushuaia', 'Almirante Brown', '123', 
         'EPU', true, (SELECT id_area FROM area WHERE nombre = 'Departamento Habilitaciones Zona Norte')),
         
        ('011', 'Jorge', 'Gutierrez', 'jorge.gutierrez@proteccioncivil.tdf.gov.ar', 
         '12345670', '27123456704', 'pbkdf2_sha256$1000000$2F6I1j3U8V9W0X1Y2Z3A4B$5DeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXyZaBc=', 
         '2964123450', '1986-02-14', 'Tierra del Fuego', 'Ushuaia', 'Gobernador Paz', '567', 
         'POMYS', true, (SELECT id_area FROM area WHERE nombre = 'Departamento Administrativo y Contable')),
         
        ('012', 'Ana', 'Torres', 'ana.torres@proteccioncivil.tdf.gov.ar', 
         '23456701', '27234567014', 'pbkdf2_sha256$1000000$3G7J2k4V9W0X1Y2Z3A4B5C$6EfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXyZaBcDe=', 
         '2964234501', '1993-10-08', 'Tierra del Fuego', 'Ushuaia', 'Juana Fadul', '890', 
         'PAYT', true, (SELECT id_area FROM area WHERE nombre = 'División de Planificación'))
    ON CONFLICT (legajo) DO NOTHING;
    
    -- Asignar roles usando la tabla agente_rol (estructura actual)
    INSERT INTO agente_rol (id_agente, id_rol) VALUES
        ((SELECT id_agente FROM agente WHERE legajo = '001'), rol_admin_id),    -- Tayra: Administrador
        ((SELECT id_agente FROM agente WHERE legajo = '002'), rol_admin_id),    -- Micaela: Administrador  
        ((SELECT id_agente FROM agente WHERE legajo = '003'), rol_director_id), -- Cristian: Director
        ((SELECT id_agente FROM agente WHERE legajo = '004'), rol_jefe_id),     -- Leandro: Jefatura
        ((SELECT id_agente FROM agente WHERE legajo = '005'), rol_avanzado_id), -- Teresa: Agente Avanzado
        ((SELECT id_agente FROM agente WHERE legajo = '006'), rol_agente_id),   -- Pamela: Agente
        ((SELECT id_agente FROM agente WHERE legajo = '007'), rol_director_id), -- Roberto: Director (Subsecretaría)
        ((SELECT id_agente FROM agente WHERE legajo = '008'), rol_jefe_id),     -- Sandra: Jefatura (Dir. Provincial)
        ((SELECT id_agente FROM agente WHERE legajo = '009'), rol_jefe_id),     -- Carlos: Jefatura (Depto. Norte)
        ((SELECT id_agente FROM agente WHERE legajo = '010'), rol_avanzado_id), -- María: Agente Avanzado
        ((SELECT id_agente FROM agente WHERE legajo = '011'), rol_avanzado_id), -- Jorge: Agente Avanzado
        ((SELECT id_agente FROM agente WHERE legajo = '012'), rol_agente_id)    -- Ana: Agente
    ON CONFLICT (id_agente, id_rol) DO NOTHING;
    
    -- Asignar jefes a las áreas principales
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '001') 
    WHERE nombre = 'Secretaría de Protección Civil';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '007') 
    WHERE nombre = 'Subsecretaría de Seguridad Vial';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '008') 
    WHERE nombre = 'Dirección Provincial de Seguridad Vial';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '003') 
    WHERE nombre = 'Dirección General de Planificación de Transporte y Seguridad Vial';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '009') 
    WHERE nombre = 'Departamento Operativo Zona Norte';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '004') 
    WHERE nombre = 'Departamento Operativo Zona Sur';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '010') 
    WHERE nombre = 'Departamento Habilitaciones Zona Norte';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '011') 
    WHERE nombre = 'Departamento Administrativo y Contable';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '005') 
    WHERE nombre = 'División de Planificación';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '012') 
    WHERE nombre = 'División RePAT Zona Norte';
    
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

-- =====================================================
-- DATOS ADICIONALES PARA CRONOGRAMAS Y PLUS
-- =====================================================

-- Insertar agrupaciones desde datos existentes de agentes
INSERT INTO agrupacion (nombre, descripcion) 
SELECT DISTINCT 
    agrupacion as nombre,
    'Agrupación ' || agrupacion as descripcion
FROM agente 
WHERE agrupacion IS NOT NULL 
AND agrupacion != ''
AND NOT EXISTS (
    SELECT 1 FROM agrupacion WHERE nombre = agente.agrupacion
)
ORDER BY agrupacion;

-- Feriados básicos 2024-2025
INSERT INTO feriado (fecha, descripcion, es_nacional) VALUES 
    ('2024-12-25', 'Navidad', true),
    ('2025-01-01', 'Año Nuevo', true),
    ('2025-05-01', 'Día del Trabajador', true),
    ('2025-07-09', 'Día de la Independencia', true),
    ('2025-12-25', 'Navidad', true)
ON CONFLICT (fecha) DO NOTHING;

-- Parámetros por defecto para área de Protección Civil
INSERT INTO parametros_area (id_area, ventana_entrada_inicio, ventana_entrada_fin, ventana_salida_inicio, ventana_salida_fin)
SELECT 
    id_area, 
    '07:30:00'::TIME, 
    '09:00:00'::TIME, 
    '16:00:00'::TIME, 
    '18:30:00'::TIME
FROM area 
WHERE nombre = 'Secretaría de Protección Civil'
AND NOT EXISTS (
    SELECT 1 FROM parametros_area WHERE id_area = area.id_area
);

-- Reglas plus por defecto 
INSERT INTO reglas_plus (nombre, horas_minimas_diarias, horas_minimas_mensuales, porcentaje_plus)
VALUES 
    ('Plus 20% Guardias', 8.0, 160.0, 20.0),
    ('Plus 40% Guardias Especiales', 12.0, 200.0, 40.0)
ON CONFLICT DO NOTHING;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'MIGRACIÓN DE DATOS COMPLETADA EXITOSAMENTE - Sistema GIGA Protección Civil';
    RAISE NOTICE 'Datos adicionales: agrupaciones, feriados, parámetros de área, reglas plus';
END $$;