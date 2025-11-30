-- ========================================================================
-- SCRIPT CONSOLIDADO: DATOS INICIALES - Sistema GIGA
-- Fecha: 27 de Noviembre 2025
-- Descripción: Seed data para el sistema GIGA de Protección Civil
-- Incluye: Roles, Licencias, Áreas Jer\u00e1rquicas, Agentes, Feriados, Reglas
-- ========================================================================
-- NOTA: Este script reemplaza el archivo 05-seed-data.sql
-- ========================================================================

-- =====================================================
-- ROLES DEL SISTEMA
-- =====================================================
DELETE FROM rol WHERE nombre IN ('administrador', 'jefe', 'director', 'agente', 'supervisor');
INSERT INTO rol (nombre, descripcion) VALUES 
    ('Administrador', 'Acceso total al sistema, gestión de usuarios y configuración'),
    ('Director', 'Valida y aprueba cronogramas, accede a reportes globales'),
    ('Jefatura', 'Planifica cronogramas mensuales, gestiona y supervisa equipos'),
    ('Agente Avanzado', 'Carga asistencia y novedades de su equipo, además de funciones de agente'),
    ('Agente', 'Consulta su ficha, parte diario, guardias y plus asignado')
ON CONFLICT (nombre) DO NOTHING;

-- =====================================================
-- TIPOS DE LICENCIA
-- =====================================================
DELETE FROM tipo_licencia WHERE codigo IN ('ANUAL', 'ENFERMEDAD', 'MATERNIDAD', 'PATERNIDAD', 'ESPECIAL', 'ESTUDIO', 'FALLECIMIENTO', 'CASAMIENTO');
INSERT INTO tipo_licencia (codigo, descripcion) VALUES 
    ('VAC', 'Vacaciones - Licencia por vacaciones anuales'),
    ('ENF', 'Enfermedad - Licencia por enfermedad o motivos médicos'),
    ('PER', 'Personal - Licencia por motivos personales')
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- ESTRUCTURA JERÁRQUICA DE ÁREAS
-- =====================================================
DELETE FROM area WHERE nombre = 'General';

-- Nivel 1: Secretaría Principal
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Secretaría de Protección Civil', 'Secretaría principal de Protección Civil de Tierra del Fuego', NULL, 1, true) 
ON CONFLICT (nombre, id_area_padre) DO NOTHING;

-- Nivel 2: Subsecretaría
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Subsecretaría de Seguridad Vial', 'Subsecretaría encargada de la seguridad vial provincial', 
     (SELECT id_area FROM area WHERE nombre = 'Secretaría de Protección Civil' LIMIT 1), 2, true) 
ON CONFLICT (nombre, id_area_padre) DO NOTHING;

-- Nivel 3: Dirección Provincial
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Dirección Provincial de Seguridad Vial', 'Dirección principal de seguridad vial provincial', 
     (SELECT id_area FROM area WHERE nombre = 'Subsecretaría de Seguridad Vial' LIMIT 1), 3, true) 
ON CONFLICT (nombre, id_area_padre) DO NOTHING;

-- Nivel 4: Direcciones Generales y Operativas
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Dirección General de Planificación de Transporte y Seguridad Vial', 'Planificación estratégica del transporte y seguridad vial', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true),
    ('Dirección Operativa y Seguridad Vial Zona Norte', 'Operaciones de seguridad vial en zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true),
    ('Dirección Operativa y Seguridad Vial Zona Sur', 'Operaciones de seguridad vial en zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true),
    ('Dirección Habilitaciones Zona Norte', 'Habilitaciones y permisos zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true),
    ('Dirección Habilitaciones Zona Sur', 'Habilitaciones y permisos zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true),
    ('Dirección Administrativa y Contable', 'Administración y contabilidad general', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true),
    ('Dirección Observatorio Vial', 'Observatorio y estadísticas de seguridad vial', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1), 4, true) 
ON CONFLICT (nombre, id_area_padre) DO NOTHING;

-- Nivel 5+: Subdirecciones y Departamentos (consolidados)
INSERT INTO area (nombre, descripcion, id_area_padre, nivel, activo) VALUES 
    ('Subdirección General de Planificación de Transporte y Seguridad Vial', 'Subdirección de planificación operativa', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección General de Planificación de Transporte y Seguridad Vial' LIMIT 1), 5, true),
    ('Departamento Operativo Zona Norte', 'Departamento de operaciones zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Operativa y Seguridad Vial Zona Norte' LIMIT 1), 5, true),
    ('Departamento Operativo Zona Sur', 'Departamento de operaciones zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Operativa y Seguridad Vial Zona Sur' LIMIT 1), 5, true),
    ('Departamento Habilitaciones Zona Norte', 'Departamento de habilitaciones zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Norte' LIMIT 1), 5, true),
    ('Departamento Habilitaciones Zona Sur', 'Departamento de habilitaciones zona sur', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Habilitaciones Zona Sur' LIMIT 1), 5, true),
    ('Departamento Administrativo y Contable', 'Departamento principal administrativo y contable', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Administrativa y Contable' LIMIT 1), 5, true),
    ('Departamento RePAT Zona Norte', 'Registro Provincial de Antecedentes de Tránsito zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Dirección Observatorio Vial' LIMIT 1), 5, true),
    ('Departamento de Planificación', 'Departamento de planificación estratégica', 
     (SELECT id_area FROM area WHERE nombre = 'Subdirección General de Planificación de Transporte y Seguridad Vial' LIMIT 1), 6, true),
    ('División de Planificación', 'División operativa de planificación', 
     (SELECT id_area FROM area WHERE nombre = 'Departamento de Planificación' LIMIT 1), 7, true),
    ('División RePAT Zona Norte', 'División operativa del RePAT zona norte', 
     (SELECT id_area FROM area WHERE nombre = 'Departamento RePAT Zona Norte' LIMIT 1), 6, true) 
ON CONFLICT (nombre, id_area_padre) DO NOTHING;

-- =====================================================
-- AGENTES Y ASIGNACIÓN DE ROLES
-- =====================================================
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
    
    -- Insertar agentes
    INSERT INTO agente (
        legajo, nombre, apellido, email, dni, cuil, password_hash, telefono, 
        fecha_nacimiento, provincia, ciudad, calle, numero, agrupacion, activo, id_area
    ) VALUES 
        ('001', 'Tayra', 'Aguila', 'tayra.aguila@proteccioncivil.tdf.gov.ar', 
         '12345678', '27123456784','pbkdf2_sha256$1000000$TDYqnUwElaDks7JCXRHmjZ$DognNfhfOXm6tCZJ/BRJrez+cteBVqiH1DIal5dMeiU=', 
         '2964123456', '1990-01-15', 'Tierra del Fuego', 'Ushuaia', 'San Martín', '123', 'EPU', true, area_id),
        ('002', 'Micaela', 'Alvarado', 'micaela.alvarado@proteccioncivil.tdf.gov.ar', 
         '23456789', '27234567894','pbkdf2_sha256$1000000$9ZD1gGhiDBST9A5HUZQsd9$8owfKPCKi7nRbvvZGfSARgBZoLDmX0bfh5Bwf92SryE=', 
         '2964234567', '1985-03-22', 'Tierra del Fuego', 'Ushuaia', 'Belgrano', '456', 'EPU', true, area_id),
        ('003', 'Cristian', 'Garcia', 'cristian.garcia@proteccioncivil.tdf.gov.ar', 
         '34567890', '27345678904','pbkdf2_sha256$1000000$3MNefVZa2AIQDYGyaSLQcT$EtkU+jh7MbxVbQhQj73YuWu+qQhRVCsCwIJKyd6dtXc=', 
         '2964345678', '1988-07-10', 'Tierra del Fuego', 'Ushuaia', 'Rivadavia', '789', 'POMYS', true, area_id),
        ('004','Leandro', 'Gomez', 'leandro.gomez@proteccioncivil.tdf.gov.ar', 
         '45678901', '27456789014','pbkdf2_sha256$1000000$P8Buwpis9Cm8HLGxW0ndoX$qJxR0ex+s9TPGy76d2OsOf2uPKMz3Wk1NYSppuhdr1I=', 
         '2964456789', '1992-11-05', 'Tierra del Fuego', 'Ushuaia', 'Maipú', '321', 'PAYT', true, area_id),
        ('005', 'Teresa', 'Criniti', 'teresa.criniti@proteccioncivil.tdf.gov.ar', 
         '56789012','27567890124', 'pbkdf2_sha256$1000000$cY78hNwJKXCLijREgLFggk$AkHqFVGitqHl/orwTLr74pqEeU+JN2kAAJk7r0TsN7k=', 
         '2964567890', '1980-09-18', 'Tierra del Fuego', 'Ushuaia', 'Yaganes', '654', 'EPU', true, area_id),
        ('006', 'Pamela', 'Frers', 'pamela.frers@proteccioncivil.tdf.gov.ar', 
         '67890123', '27678901234', 'pbkdf2_sha256$1000000$PR3R1yPZeUhy1a1oY3Vj0W$WxsEWCjKX8nEMFmJ7wBsUXZkRFrvox0x4UBoc/b0BAk=', 
         '2964678901', '1995-12-30', 'Tierra del Fuego', 'Ushuaia', 'Onashaga', '987', 'POMYS', true, area_id),
        ('007', 'Roberto', 'Martinez', 'roberto.martinez@proteccioncivil.tdf.gov.ar', 
         '78901234', '27789012344', 'pbkdf2_sha256$1000000$8B2E7f9Q4R5T6U7V8W9X0Y$1ZaAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTu=', 
         '2964789012', '1987-04-12', 'Tierra del Fuego', 'Ushuaia', 'Prefectura Naval', '234', 'EPU', true, (SELECT id_area FROM area WHERE nombre = 'Subsecretaría de Seguridad Vial' LIMIT 1)),
        ('008', 'Sandra', 'Lopez', 'sandra.lopez@proteccioncivil.tdf.gov.ar', 
         '89012345', '27890123454', 'pbkdf2_sha256$1000000$9C3F8g0R5S6T7U8V9W0X1Y$2AbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVw=', 
         '2964890123', '1991-08-25', 'Tierra del Fuego', 'Ushuaia', 'Karukinka', '456', 'POMYS', true, (SELECT id_area FROM area WHERE nombre = 'Dirección Provincial de Seguridad Vial' LIMIT 1)),
        ('009', 'Carlos', 'Rodriguez', 'carlos.rodriguez@proteccioncivil.tdf.gov.ar', 
         '90123456', '27901234564', 'pbkdf2_sha256$1000000$0D4G9h1S6T7U8V9W0X1Y2Z$3BcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXy=', 
         '2964901234', '1984-06-18', 'Tierra del Fuego', 'Ushuaia', '25 de Mayo', '789', 'PAYT', true, (SELECT id_area FROM area WHERE nombre = 'Departamento Operativo Zona Norte' LIMIT 1)),
        ('010', 'María', 'Fernandez', 'maria.fernandez@proteccioncivil.tdf.gov.ar', 
         '01234567', '27012345674', 'pbkdf2_sha256$1000000$1E5H0i2T7U8V9W0X1Y2Z3A$4CdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXyZa=', 
         '2964012345', '1989-12-03', 'Tierra del Fuego', 'Ushuaia', 'Almirante Brown', '123', 'EPU', true, (SELECT id_area FROM area WHERE nombre = 'Departamento Habilitaciones Zona Norte' LIMIT 1)),
        ('011', 'Jorge', 'Gutierrez', 'jorge.gutierrez@proteccioncivil.tdf.gov.ar', 
         '12345670', '27123456704', 'pbkdf2_sha256$1000000$2F6I1j3U8V9W0X1Y2Z3A4B$5DeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXyZaBc=', 
         '2964123450', '1986-02-14', 'Tierra del Fuego', 'Ushuaia', 'Gobernador Paz', '567', 'POMYS', true, (SELECT id_area FROM area WHERE nombre = 'Departamento Administrativo y Contable' LIMIT 1)),
        ('012', 'Ana', 'Torres', 'ana.torres@proteccioncivil.tdf.gov.ar', 
         '23456701', '27234567014', 'pbkdf2_sha256$1000000$3G7J2k4V9W0X1Y2Z3A4B5C$6EfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuVwXyZaBcDe=', 
         '2964234501', '1993-10-08', 'Tierra del Fuego', 'Ushuaia', 'Juana Fadul', '890', 'PAYT', true, (SELECT id_area FROM area WHERE nombre = 'División de Planificación' LIMIT 1))
    ON CONFLICT (legajo) DO NOTHING;
    
    -- Asignar roles a agentes
    INSERT INTO agente_rol (id_agente, id_rol) VALUES
        ((SELECT id_agente FROM agente WHERE legajo = '001'), rol_admin_id),
        ((SELECT id_agente FROM agente WHERE legajo = '002'), rol_admin_id),
        ((SELECT id_agente FROM agente WHERE legajo = '003'), rol_director_id),
        ((SELECT id_agente FROM agente WHERE legajo = '004'), rol_jefe_id),
        ((SELECT id_agente FROM agente WHERE legajo = '005'), rol_avanzado_id),
        ((SELECT id_agente FROM agente WHERE legajo = '006'), rol_agente_id),
        ((SELECT id_agente FROM agente WHERE legajo = '007'), rol_director_id),
        ((SELECT id_agente FROM agente WHERE legajo = '008'), rol_jefe_id),
        ((SELECT id_agente FROM agente WHERE legajo = '009'), rol_jefe_id),
        ((SELECT id_agente FROM agente WHERE legajo = '010'), rol_avanzado_id),
        ((SELECT id_agente FROM agente WHERE legajo = '011'), rol_avanzado_id),
        ((SELECT id_agente FROM agente WHERE legajo = '012'), rol_agente_id)
    ON CONFLICT (id_agente, id_rol) DO NOTHING;
    
    -- Asignar jefes a las áreas
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '001') 
    WHERE nombre = 'Secretaría de Protección Civil';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '007') 
    WHERE nombre = 'Subsecretaría de Seguridad Vial';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '008') 
    WHERE nombre = 'Dirección Provincial de Seguridad Vial';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '009') 
    WHERE nombre = 'Departamento Operativo Zona Norte';
    
    UPDATE area SET jefe_area = (SELECT id_agente FROM agente WHERE legajo = '010') 
    WHERE nombre = 'Departamento Habilitaciones Zona Norte';
    
    -- Insertar licencias de ejemplo
    INSERT INTO licencia (id_agente, id_tipo_licencia, fecha_desde, fecha_hasta, estado) VALUES 
        ((SELECT id_agente FROM agente WHERE legajo = '001'), tipo_vac_id, '2025-02-15', '2025-02-17', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '002'), tipo_vac_id, '2025-06-20', '2025-06-24', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '003'), tipo_vac_id, '2025-05-12', '2025-05-16', 'pendiente'),
        ((SELECT id_agente FROM agente WHERE legajo = '004'), tipo_per_id, '2025-02-28', '2025-02-28', 'aprobada'),
        ((SELECT id_agente FROM agente WHERE legajo = '005'), tipo_enf_id, '2025-03-15', '2025-03-17', 'aprobada');
        
END $$;

-- =====================================================
-- DATOS ADICIONALES
-- =====================================================

-- Agrupaciones desde datos de agentes
INSERT INTO agrupacion (nombre, descripcion) 
SELECT DISTINCT 
    agrupacion as nombre,
    'Agrupación ' || agrupacion as descripcion
FROM agente 
WHERE agrupacion IS NOT NULL AND agrupacion != ''
AND NOT EXISTS (SELECT 1 FROM agrupacion WHERE nombre = agente.agrupacion);

-- Feriados nacionales 2025 (ACTUALIZADO para nueva estructura con rangos)
INSERT INTO feriado (nombre, fecha_inicio, fecha_fin, descripcion, es_nacional) VALUES 
    ('Año Nuevo', '2025-01-01', '2025-01-01', 'Celebración de Año Nuevo', true),
    ('Día del Trabajador', '2025-05-01', '2025-05-01', 'Día Internacional del Trabajador', true),
    ('Día de la Independencia', '2025-07-09', '2025-07-09', 'Declaración de Independencia Argentina', true),
    ('Navidad', '2025-12-25', '2025-12-25', 'Celebración de Navidad', true)
ON CONFLICT DO NOTHING;

-- Parámetros de área
INSERT INTO parametros_area (id_area, ventana_entrada_inicio, ventana_entrada_fin, ventana_salida_inicio, ventana_salida_fin, vigente_desde)
SELECT 
    id_area, '07:30:00'::TIME, '09:00:00'::TIME, '16:00:00'::TIME, '18:30:00'::TIME, '2025-01-01'::DATE
FROM area 
WHERE nombre = 'Secretaría de Protección Civil'
AND NOT EXISTS (SELECT 1 FROM parametros_area WHERE id_area = area.id_area);

-- Reglas de plus
INSERT INTO reglas_plus (horas_minimas_mensuales, porcentaje_plus, vigente_desde) 
VALUES 
    (32, 20.0, NOW()),
    (40, 40.0, NOW())
ON CONFLICT DO NOTHING;

-- Actualizar secuencias
SELECT setval('area_id_area_seq', COALESCE((SELECT MAX(id_area) FROM area), 1), true);
SELECT setval('rol_id_rol_seq', COALESCE((SELECT MAX(id_rol) FROM rol), 1), true);
SELECT setval('tipo_licencia_id_tipo_licencia_seq', COALESCE((SELECT MAX(id_tipo_licencia) FROM tipo_licencia), 1), true);
SELECT setval('agente_id_agente_seq', COALESCE((SELECT MAX(id_agente) FROM agente), 1), true);
SELECT setval('agente_rol_id_agente_rol_seq', COALESCE((SELECT MAX(id_agente_rol) FROM agente_rol), 1), true);
SELECT setval('licencia_id_licencia_seq', COALESCE((SELECT MAX(id_licencia) FROM licencia), 1), true);

-- ========================================================================
-- MENSAJE DE CONFIRMACIÓN
-- ========================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'SCRIPT CONSOLIDADO DE DATOS COMPLETADO';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Datos insertados:';
    RAISE NOTICE '- % roles', (SELECT COUNT(*) FROM rol);
    RAISE NOTICE '- % tipos de licencia', (SELECT COUNT(*) FROM tipo_licencia);
    RAISE NOTICE '- % áreas jerárquicas', (SELECT COUNT(*) FROM area);
    RAISE NOTICE '- % agentes', (SELECT COUNT(*) FROM agente);
    RAISE NOTICE '- % asignaciones de rol', (SELECT COUNT(*) FROM agente_rol);
    RAISE NOTICE '- % licencias', (SELECT COUNT(*) FROM licencia);
    RAISE NOTICE '- % agrupaciones', (SELECT COUNT(*) FROM agrupacion);
    RAISE NOTICE '- % feriados', (SELECT COUNT(*) FROM feriado);
    RAISE NOTICE '========================================';
END $$;

-- ========================================================================
-- FIN DEL SCRIPT CONSOLIDADO DE DATOS
-- ========================================================================
