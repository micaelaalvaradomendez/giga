-- ========================================================================
-- SCRIPT CONSOLIDADO: TABLAS FINALES - Sistema GIGA
-- Fecha: 27 de Noviembre 2025
-- Descripción: Definición consolidada de TODAS las tablas del sistema
-- Incluye todos los ALTER TABLE de scripts 06-12
-- ========================================================================
-- NOTA: Este script reemplaza los archivos 03, 06, 08, 09, 11, 12
-- ========================================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- TABLAS PRINCIPALES DEL DOMINIO
-- =====================================================

-- 1. Tabla: area (soporte jerárquico)
CREATE TABLE IF NOT EXISTS area (
    id_area BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    id_area_padre BIGINT,
    jefe_area BIGINT,
    nivel INTEGER DEFAULT 0,
    orden_visualizacion INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_area_padre) REFERENCES area(id_area) ON DELETE CASCADE,
    UNIQUE NULLS NOT DISTINCT (nombre, id_area_padre)
);

-- 2. Tabla: tipo_licencia
CREATE TABLE IF NOT EXISTS tipo_licencia (
    id_tipo_licencia BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- 3. Tabla: rol
CREATE TABLE IF NOT EXISTS rol (
    id_rol BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla: agente
CREATE TABLE IF NOT EXISTS agente (
    id_agente BIGSERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    cuil VARCHAR(20) UNIQUE NOT NULL,
    legajo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(15),
    fecha_nacimiento DATE,
    provincia VARCHAR(100),
    ciudad VARCHAR(100),
    calle VARCHAR(150),
    numero VARCHAR(10),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    horario_entrada TIME,
    horario_salida TIME,
    agrupacion VARCHAR(100),
    activo BOOLEAN DEFAULT true,
    id_area BIGINT,
    tolerancia_entrada_min INTEGER DEFAULT 10,
    tolerancia_salida_min INTEGER DEFAULT 10,
    horas_trabajo_dia DECIMAL(4,2) DEFAULT 8.0,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT
);

-- Agregar FK de jefe de área después de crear agente
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_area_jefe') THEN
        ALTER TABLE area ADD CONSTRAINT fk_area_jefe 
            FOREIGN KEY (jefe_area) REFERENCES agente(id_agente) ON DELETE SET NULL;
    END IF;
END $$;

-- 5. Tabla: agente_rol
CREATE TABLE IF NOT EXISTS agente_rol (
    id_agente_rol BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL,
    id_rol BIGINT NOT NULL,
    asignado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol) ON DELETE RESTRICT,
    UNIQUE(id_agente, id_rol)
);

-- 6. Tabla: agrupacion (para organización jerárquica)
CREATE TABLE IF NOT EXISTS agrupacion (
    id_agrupacion BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    color VARCHAR(7) DEFAULT '#e79043',
    id_area BIGINT,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE CASCADE
);

-- 6b. Tabla: organigrama (NUEVA - Managed by Django but needed for consistency)
CREATE TABLE IF NOT EXISTS organigrama (
    id_organigrama BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    estructura JSONB NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    activo BOOLEAN DEFAULT true,
    creado_por VARCHAR(100) DEFAULT 'Sistema',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Tabla: cronograma (CON campos de aprobación jerárquica del script 06)
CREATE TABLE IF NOT EXISTS cronograma (
    id_cronograma BIGSERIAL PRIMARY KEY,

    -- NUEVOS CAMPOS (mes completo)
    anio INT NOT NULL,
    mes INT NOT NULL,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NOT NULL,

    fecha_aprobacion DATE,
    tipo VARCHAR(50),
    hora_fin TIME,
    hora_inicio TIME,
    estado VARCHAR(50) DEFAULT 'generada',
    fecha_creacion DATE,
    activa BOOLEAN DEFAULT true,

    id_jefe BIGINT,
    id_director BIGINT,
    id_area BIGINT NOT NULL,

    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Campos de aprobación jerárquica
    creado_por_rol VARCHAR(50),
    creado_por_id BIGINT,
    aprobado_por_id BIGINT,

    FOREIGN KEY (id_jefe) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (id_director) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT,
    FOREIGN KEY (creado_por_id) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (aprobado_por_id) REFERENCES agente(id_agente) ON DELETE SET NULL,

    -- Validaciones básicas
    CONSTRAINT chk_cronograma_mes_valido CHECK (mes BETWEEN 1 AND 12),
    CONSTRAINT chk_cronograma_rango_fechas CHECK (fecha_desde <= fecha_hasta)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_cronograma_estado ON cronograma(estado);
CREATE INDEX IF NOT EXISTS idx_cronograma_creado_por_rol ON cronograma(creado_por_rol);
CREATE INDEX IF NOT EXISTS idx_cronograma_creado_por_id ON cronograma(creado_por_id);
CREATE INDEX IF NOT EXISTS idx_cronograma_aprobado_por_id ON cronograma(aprobado_por_id);

-- NUEVOS (búsqueda por mes/área/estado)
CREATE INDEX IF NOT EXISTS idx_cronograma_anio_mes ON cronograma(anio, mes);
CREATE INDEX IF NOT EXISTS idx_cronograma_area_anio_mes_estado ON cronograma(id_area, anio, mes, estado);

-- EVITA 2 PENDIENTES PARA EL MISMO MES/ÁREA (clave para tu lógica del paso 2)
CREATE UNIQUE INDEX IF NOT EXISTS ux_cronograma_area_anio_mes_pendiente
ON cronograma(id_area, anio, mes)
WHERE estado = 'pendiente';

COMMENT ON COLUMN cronograma.estado IS 'Estados: generada, pendiente, aprobada, publicada, rechazada, cancelada';
COMMENT ON COLUMN cronograma.anio IS 'Año del cronograma';
COMMENT ON COLUMN cronograma.mes IS 'Mes del cronograma (1-12)';
COMMENT ON COLUMN cronograma.fecha_desde IS 'Inicio del período (primer día del mes)';
COMMENT ON COLUMN cronograma.fecha_hasta IS 'Fin del período (último día del mes)';



-- 8. Tabla: guardia
CREATE TABLE IF NOT EXISTS guardia (
    id_guardia BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    tipo VARCHAR(50),
    estado VARCHAR(50),
    activa BOOLEAN DEFAULT true,
    horas_planificadas INTEGER,
    horas_efectivas INTEGER,
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_cronograma BIGINT NOT NULL,
    id_agente BIGINT NOT NULL,
    FOREIGN KEY (id_cronograma) REFERENCES cronograma(id_cronograma) ON DELETE RESTRICT,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_guardia_fecha ON guardia(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_guardia_agente ON guardia(id_agente);
CREATE INDEX IF NOT EXISTS idx_guardia_cronograma ON guardia(id_cronograma);
CREATE INDEX IF NOT EXISTS idx_guardia_estado ON guardia(estado);

-- 9. Tabla: nota_guardia
CREATE TABLE IF NOT EXISTS nota_guardia (
    id_nota BIGSERIAL PRIMARY KEY,
    id_guardia BIGINT NOT NULL,
    id_agente BIGINT NOT NULL,
    nota TEXT,
    fecha_nota TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_guardia) REFERENCES guardia(id_guardia) ON DELETE CASCADE,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE CASCADE,
    UNIQUE(id_guardia, id_agente)
);

-- 10. Tabla: hora_compensacion (del script 06 - COMPLETA)
CREATE TABLE IF NOT EXISTS hora_compensacion (
    id_hora_compensacion BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL,
    id_guardia BIGINT,
    id_cronograma BIGINT NOT NULL,
    fecha_servicio DATE NOT NULL,
    hora_inicio_programada TIME NOT NULL,
    hora_fin_programada TIME NOT NULL,
    hora_fin_real TIME NOT NULL,
    horas_programadas DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    horas_efectivas DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    horas_extra DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    motivo VARCHAR(20) NOT NULL DEFAULT 'emergencia',
    descripcion_motivo TEXT NOT NULL,
    numero_acta VARCHAR(50),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    tipo_compensacion VARCHAR(20) NOT NULL DEFAULT 'plus',
    solicitado_por BIGINT NOT NULL,
    aprobado_por BIGINT,
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    observaciones_aprobacion TEXT,
    valor_hora_extra DECIMAL(10,2),
    monto_total DECIMAL(10,2),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE CASCADE,
    FOREIGN KEY (id_guardia) REFERENCES guardia(id_guardia) ON DELETE SET NULL,
    FOREIGN KEY (id_cronograma) REFERENCES cronograma(id_cronograma) ON DELETE CASCADE,
    FOREIGN KEY (solicitado_por) REFERENCES agente(id_agente),
    FOREIGN KEY (aprobado_por) REFERENCES agente(id_agente),
    CONSTRAINT chk_horas_extra_positivas CHECK (horas_extra > 0),
    CONSTRAINT chk_horas_extra_limite CHECK (horas_extra <= 8),
    CONSTRAINT chk_hora_fin_real_posterior CHECK (hora_fin_real > hora_fin_programada),
    CONSTRAINT chk_estado_valido CHECK (estado IN ('pendiente', 'aprobada', 'rechazada', 'pagada')),
    CONSTRAINT chk_motivo_valido CHECK (motivo IN ('siniestro', 'emergencia', 'operativo', 'refuerzo', 'otro')),
    CONSTRAINT chk_tipo_compensacion_valido CHECK (tipo_compensacion IN ('pago', 'franco', 'plus')),
    CONSTRAINT uk_compensacion_agente_fecha UNIQUE (id_agente, fecha_servicio, id_cronograma)
);

-- Índices para hora_compensacion
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_agente ON hora_compensacion(id_agente);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_fecha ON hora_compensacion(fecha_servicio);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_estado ON hora_compensacion(estado);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_mes_anio ON hora_compensacion(EXTRACT(YEAR FROM fecha_servicio), EXTRACT(MONTH FROM fecha_servicio));
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_solicitado_por ON hora_compensacion(solicitado_por);
CREATE INDEX IF NOT EXISTS idx_hora_compensacion_aprobado_por ON hora_compensacion(aprobado_por);

-- 11. Tabla: feriado (NUEVA ESTRUCTURA del script 11 - con rangos de fecha)
CREATE TABLE IF NOT EXISTS feriado (
    id_feriado BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    es_nacional BOOLEAN DEFAULT false,
    es_provincial BOOLEAN DEFAULT false,
    es_local BOOLEAN DEFAULT false,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fechas_validas CHECK (fecha_fin >= fecha_inicio)
);

-- Índices para feriado
CREATE INDEX IF NOT EXISTS idx_feriado_fecha_inicio ON feriado(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_feriado_fecha_fin ON feriado(fecha_fin);
CREATE INDEX IF NOT EXISTS idx_feriado_rango ON feriado(fecha_inicio, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_feriado_activo ON feriado(activo) WHERE activo = true;

-- 5. Tabla: parametros_area
CREATE TABLE IF NOT EXISTS parametros_area (
    id_parametros_area BIGSERIAL PRIMARY KEY,
    id_area BIGINT NOT NULL,
    ventana_entrada_inicio TIME DEFAULT '07:30:00',
    ventana_entrada_fin TIME DEFAULT '09:00:00',
    ventana_salida_inicio TIME DEFAULT '16:00:00',
    ventana_salida_fin TIME DEFAULT '18:30:00',
    tolerancia_entrada_min INTEGER DEFAULT 15,
    tolerancia_salida_min INTEGER DEFAULT 15,
    horas_trabajo_dia DECIMAL(4,2) DEFAULT 8.0,
    vigente_desde DATE NOT NULL,
    vigente_hasta DATE,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE CASCADE
);

-- 6. Tabla: reglas_plus
CREATE TABLE IF NOT EXISTS reglas_plus (
    id_regla_plus BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL DEFAULT 'Regla General',
    horas_minimas_diarias DECIMAL(5,2) DEFAULT 8.0,
    horas_minimas_mensuales DECIMAL(6,2) DEFAULT 160.0,
    porcentaje_plus DECIMAL(5,2) DEFAULT 20.0,
    aplica_areas_operativas BOOLEAN DEFAULT true,
    aplica_areas_administrativas BOOLEAN DEFAULT false,
    vigente_desde DATE NOT NULL,
    vigente_hasta DATE,
    activa BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Tabla: resumen_guardia_mes
CREATE TABLE IF NOT EXISTS resumen_guardia_mes (
    id_resumen_guardia_mes BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL,
    mes INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    plus20 BOOLEAN,
    plus40 BOOLEAN,
    total_horas_guardia INTEGER,
    horas_efectivas DECIMAL(6,2) DEFAULT 0.0,
    porcentaje_plus DECIMAL(5,2) DEFAULT 0.0,
    monto_calculado DECIMAL(10,2),
    estado_plus VARCHAR(30) DEFAULT 'pendiente',
    fecha_calculo TIMESTAMP,
    aprobado_en TIMESTAMP,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE CASCADE,
    UNIQUE(id_agente, mes, anio)
);

-- =====================================================
-- TABLAS DE ASISTENCIA (REFACTORIZADAS del script 08)
-- =====================================================

-- 14. Tabla: parte_diario
CREATE TABLE IF NOT EXISTS parte_diario (
    id_parte_diario BIGSERIAL PRIMARY KEY,
    fecha_parte DATE NOT NULL,
    id_agente BIGINT NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE CASCADE,
    UNIQUE(id_agente, fecha_parte)
);

CREATE INDEX IF NOT EXISTS idx_parte_diario_fecha ON parte_diario(fecha_parte DESC);
CREATE INDEX IF NOT EXISTS idx_parte_diario_agente ON parte_diario(id_agente);

-- 15. Tabla: asistencia (NUEVA ESTRUCTURA del script 08)
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    hora_salida TIME,
    horas_efectivas DECIMAL(4,2),
    marcacion_entrada_automatica BOOLEAN DEFAULT false,
    marcacion_salida_automatica BOOLEAN DEFAULT false,
    es_correccion BOOLEAN DEFAULT false,
    corregido_por BIGINT,
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_agente BIGINT NOT NULL,
    id_area BIGINT,
    id_parte_diario BIGINT,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE SET NULL,
    FOREIGN KEY (corregido_por) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (id_parte_diario) REFERENCES parte_diario(id_parte_diario) ON DELETE SET NULL,
    UNIQUE(id_agente, fecha)
);

-- Índices para asistencia
CREATE INDEX IF NOT EXISTS idx_asistencia_agente_fecha ON asistencia(id_agente, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_asistencia_fecha ON asistencia(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_asistencia_area ON asistencia(id_area);

COMMENT ON TABLE asistencia IS 'Registro de asistencias diarias de agentes con marcación de entrada/salida';

-- 16. Tabla: intento_marcacion_fraudulenta (del script 08)
CREATE TABLE IF NOT EXISTS intento_marcacion_fraudulenta (
    id_intento BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    dni_ingresado VARCHAR(20) NOT NULL,
    id_agente_sesion BIGINT NOT NULL,
    id_agente_dni BIGINT,
    tipo_intento VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_agente_sesion) REFERENCES agente(id_agente) ON DELETE CASCADE,
    FOREIGN KEY (id_agente_dni) REFERENCES agente(id_agente) ON DELETE SET NULL
);

-- Índices para intentos fraudulentos
CREATE INDEX IF NOT EXISTS idx_intento_fraud_agente ON intento_marcacion_fraudulenta(id_agente_sesion);
CREATE INDEX IF NOT EXISTS idx_intento_fraud_fecha ON intento_marcacion_fraudulenta(fecha DESC);

-- 17. Tabla: licencia (CON CAMPOS EXTENDIDOS del script 12)
CREATE TABLE IF NOT EXISTS licencia (
    id_licencia BIGSERIAL PRIMARY KEY,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    id_agente BIGINT NOT NULL,
    id_tipo_licencia BIGINT NOT NULL,
    -- Campos extendidos del script 12
    observaciones TEXT,
    justificacion TEXT,
    aprobada_por BIGINT,
    fecha_aprobacion DATE,
    observaciones_aprobacion TEXT,
    rechazada_por BIGINT,
    fecha_rechazo DATE,
    motivo_rechazo TEXT,
    solicitada_por BIGINT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_tipo_licencia) REFERENCES tipo_licencia(id_tipo_licencia) ON DELETE RESTRICT,
    FOREIGN KEY (aprobada_por) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (rechazada_por) REFERENCES agente(id_agente) ON DELETE SET NULL,
    FOREIGN KEY (solicitada_por) REFERENCES agente(id_agente) ON DELETE SET NULL
);

-- Índices para licencia
CREATE INDEX IF NOT EXISTS idx_licencia_estado ON licencia(estado);
CREATE INDEX IF NOT EXISTS idx_licencia_aprobada_por ON licencia(aprobada_por);
CREATE INDEX IF NOT EXISTS idx_licencia_fechas_estado ON licencia(fecha_desde, fecha_hasta, estado);
CREATE INDEX IF NOT EXISTS idx_licencia_creado_en ON licencia(creado_en);

-- 18. Tabla: novedad
CREATE TABLE IF NOT EXISTS novedad (
    id_novedad BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo VARCHAR(100),
    descripcion TEXT,
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_agente BIGINT NOT NULL,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT
);

-- 19. Tabla: auditoria
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria BIGSERIAL PRIMARY KEY,
    pk_afectada BIGINT,
    nombre_tabla VARCHAR(100) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_previo JSONB,
    valor_nuevo JSONB,
    accion VARCHAR(50) NOT NULL,
    id_agente BIGINT,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_auditoria_tabla ON auditoria(nombre_tabla);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON auditoria(accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(creado_en DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_agente ON auditoria(id_agente);

-- =====================================================
-- TABLAS DE DJANGO (del script 09)
-- =====================================================

-- 20. django_migrations
CREATE TABLE IF NOT EXISTS django_migrations (
    id BIGSERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 21. django_content_type
CREATE TABLE IF NOT EXISTS django_content_type (
    id BIGSERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- 22. django_session
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS django_session_expire_date_idx ON django_session(expire_date);

-- 23. auth_permission
CREATE TABLE IF NOT EXISTS auth_permission (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id BIGINT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE,
    UNIQUE(content_type_id, codename)
);

-- 24. auth_group
CREATE TABLE IF NOT EXISTS auth_group (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- 25. auth_group_permissions
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id BIGSERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(group_id, permission_id)
);

-- 26. auth_user
CREATE TABLE IF NOT EXISTS auth_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 27. auth_user_groups
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE(user_id, group_id)
);

-- 28. auth_user_user_permissions
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(user_id, permission_id)
);

-- 29. django_admin_log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id BIGSERIAL PRIMARY KEY,
    action_time TIMESTAMP NOT NULL,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id BIGINT,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Índices para Django
CREATE INDEX IF NOT EXISTS auth_permission_content_type_id_idx ON auth_permission(content_type_id);
CREATE INDEX IF NOT EXISTS auth_group_permissions_group_id_idx ON auth_group_permissions(group_id);
CREATE INDEX IF NOT EXISTS auth_group_permissions_permission_id_idx ON auth_group_permissions(permission_id);
CREATE INDEX IF NOT EXISTS auth_user_groups_user_id_idx ON auth_user_groups(user_id);
CREATE INDEX IF NOT EXISTS auth_user_groups_group_id_idx ON auth_user_groups(group_id);
CREATE INDEX IF NOT EXISTS auth_user_user_permissions_user_id_idx ON auth_user_user_permissions(user_id);
CREATE INDEX IF NOT EXISTS auth_user_user_permissions_permission_id_idx ON auth_user_user_permissions(permission_id);
CREATE INDEX IF NOT EXISTS django_admin_log_content_type_id_idx ON django_admin_log(content_type_id);
CREATE INDEX IF NOT EXISTS django_admin_log_user_id_idx ON django_admin_log(user_id);

-- ========================================================================
-- FIN DEL SCRIPT CONSOLIDADO DE TABLAS
-- ========================================================================
-- Total: 30 tablas consolidadas (agregada parte_diario)
-- Incluye: Tablas base + ALTER TABLE + Licencias + Asistencia + Django
-- ========================================================================
