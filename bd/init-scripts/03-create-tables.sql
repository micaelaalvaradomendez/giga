-- =====================================================
-- CREACIÓN DE TABLAS PARA SISTEMA GIGA
-- Archivo: 03-create-tables.sql
-- Descripción: Definición de todas las tablas del sistema
-- =====================================================

-- Este archivo se ejecuta automáticamente cuando se inicia
-- el contenedor PostgreSQL por primera vez.

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- TABLAS DEL SISTEMA GIGA
-- =====================================================

-- Crear tablas en orden de dependencias

-- 1. Tabla base: area (soporte jerárquico)
CREATE TABLE IF NOT EXISTS area (
    id_area BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    id_area_padre BIGINT,
    jefe_area BIGINT, -- Referencia al agente que es jefe del área
    nivel INTEGER DEFAULT 0,
    orden_visualizacion INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_area_padre) REFERENCES area(id_area) ON DELETE CASCADE,
    -- La referencia al jefe se agregará después de crear la tabla agente
    UNIQUE(nombre, id_area_padre) -- Permite nombres duplicados si están en diferentes padres
);

-- 2. Tabla base: tipo_licencia (sin dependencias)
CREATE TABLE IF NOT EXISTS tipo_licencia (
    id_tipo_licencia BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- 3. Tabla base: rol (sin dependencias)
CREATE TABLE IF NOT EXISTS rol (
    id_rol BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla agente (depende de area)
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
    -- Nuevos campos para control horario
    tolerancia_entrada_min INTEGER DEFAULT 10,
    tolerancia_salida_min INTEGER DEFAULT 10,
    horas_trabajo_dia DECIMAL(4,2) DEFAULT 8.0,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT
);

-- Agregar constraint de jefe de área después de crear la tabla agente
ALTER TABLE area ADD CONSTRAINT fk_area_jefe 
    FOREIGN KEY (jefe_area) REFERENCES agente(id_agente) ON DELETE SET NULL;

-- 5. Tabla cronograma (depende de area y agente)
CREATE TABLE IF NOT EXISTS cronograma (
    id_cronograma BIGSERIAL PRIMARY KEY,
    fecha_aprobacion DATE,
    tipo VARCHAR(50),
    hora_fin TIME,
    hora_inicio TIME,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_jefe BIGINT NOT NULL,
    id_director BIGINT NOT NULL,
    estado VARCHAR(50),
    fecha_creacion DATE,
    id_area BIGINT NOT NULL,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT,
    FOREIGN KEY (id_jefe) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_director) REFERENCES agente(id_agente) ON DELETE RESTRICT
);

-- 6. Tabla agente_rol (depende de agente y rol)
CREATE TABLE IF NOT EXISTS agente_rol (
    id_agente_rol BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL,
    id_rol BIGINT NOT NULL,
    asignado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_agente, id_rol),
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol) ON DELETE RESTRICT
);

-- 7. Tabla auditoria (depende de agente)
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria BIGSERIAL PRIMARY KEY,
    pk_afectada BIGINT NOT NULL,
    nombre_tabla VARCHAR(100) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_previo JSONB,
    valor_nuevo JSONB,
    accion VARCHAR(50) NOT NULL,
    id_agente BIGINT,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE SET NULL
);

-- 8. Tabla parte_diario (depende de agente y area)
CREATE TABLE IF NOT EXISTS parte_diario (
    id_parte_diario BIGSERIAL PRIMARY KEY,
    fecha_parte DATE NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por BIGINT NOT NULL,
    actualizado_por BIGINT NOT NULL,
    estado VARCHAR(50),
    id_agente BIGINT NOT NULL,
    observaciones TEXT,
    id_area BIGINT NOT NULL,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (creado_por) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (actualizado_por) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT
);

-- 9. Tabla guardia (depende de cronograma y agente)
CREATE TABLE IF NOT EXISTS guardia (
    id_guardia BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    tipo VARCHAR(50),
    activa BOOLEAN DEFAULT true,
    estado VARCHAR(50),
    horas_planificadas INTEGER,
    horas_efectivas INTEGER,
    id_cronograma BIGINT NOT NULL,
    id_agente BIGINT NOT NULL,
    FOREIGN KEY (id_cronograma) REFERENCES cronograma(id_cronograma) ON DELETE RESTRICT,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT
);

-- 10. Tabla resumen_guardia_mes (depende de agente)
CREATE TABLE IF NOT EXISTS resumen_guardia_mes (
    id_resumen_guardia_mes BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL,
    mes INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    -- Campos legacy mantenidos
    plus20 BOOLEAN DEFAULT false,
    plus40 BOOLEAN DEFAULT false,
    total_horas_guardia INTEGER DEFAULT 0,
    -- Nuevos campos para cálculo automático de plus
    horas_efectivas DECIMAL(6,2) DEFAULT 0,
    porcentaje_plus DECIMAL(5,2) DEFAULT 0,
    monto_calculado DECIMAL(10,2),
    estado_plus VARCHAR(30) DEFAULT 'pendiente',
    fecha_calculo TIMESTAMP,
    aprobado_en TIMESTAMP,
    UNIQUE (id_agente, mes, anio),
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT
);

-- 11. Tabla asistencia (depende de agente y parte_diario)
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia BIGSERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    es_correccion BOOLEAN DEFAULT false,
    creado_por BIGINT NOT NULL,
    id_agente BIGINT NOT NULL,
    id_parte_diario BIGINT NOT NULL,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_parte_diario) REFERENCES parte_diario(id_parte_diario) ON DELETE RESTRICT,
    FOREIGN KEY (creado_por) REFERENCES agente(id_agente) ON DELETE RESTRICT
);

-- 12. Tabla licencia (depende de agente y tipo_licencia)
CREATE TABLE IF NOT EXISTS licencia (
    id_licencia BIGSERIAL PRIMARY KEY,
    estado VARCHAR(50),
    id_tipo_licencia BIGINT NOT NULL,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NOT NULL,
    id_agente BIGINT NOT NULL,
    FOREIGN KEY (id_agente) REFERENCES agente(id_agente) ON DELETE RESTRICT,
    FOREIGN KEY (id_tipo_licencia) REFERENCES tipo_licencia(id_tipo_licencia) ON DELETE RESTRICT
);

-- 13. Tabla agrupacion (organizacional)
CREATE TABLE IF NOT EXISTS agrupacion (
    id_agrupacion BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    color VARCHAR(7) DEFAULT '#e79043',
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Tabla feriado (nueva - gestión de feriados)
CREATE TABLE IF NOT EXISTS feriado (
    id_feriado BIGSERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    es_nacional BOOLEAN DEFAULT false,
    es_provincial BOOLEAN DEFAULT false,
    es_local BOOLEAN DEFAULT false,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Tabla parametros_area (nueva - control horario por área)
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
    vigente_desde DATE DEFAULT CURRENT_DATE,
    vigente_hasta DATE,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT
);

-- 16. Tabla reglas_plus (nueva - cálculo automático de plus)
CREATE TABLE IF NOT EXISTS reglas_plus (
    id_regla_plus BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    horas_minimas_diarias DECIMAL(5,2) DEFAULT 8.0,
    horas_minimas_mensuales DECIMAL(6,2) DEFAULT 160.0,
    porcentaje_plus DECIMAL(5,2) DEFAULT 20.0,
    aplica_areas_operativas BOOLEAN DEFAULT true,
    aplica_areas_administrativas BOOLEAN DEFAULT false,
    vigente_desde DATE DEFAULT CURRENT_DATE,
    vigente_hasta DATE,
    activa BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES Y CONSTRAINTS ADICIONALES
-- =====================================================

-- Índices para optimizar consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_agente_email ON agente(email);
CREATE INDEX IF NOT EXISTS idx_agente_dni ON agente(dni);
CREATE INDEX IF NOT EXISTS idx_agente_legajo ON agente(legajo);
CREATE INDEX IF NOT EXISTS idx_agente_activo ON agente(activo);
CREATE INDEX IF NOT EXISTS idx_agente_area ON agente(id_area);

CREATE INDEX IF NOT EXISTS idx_auditoria_tabla_pk ON auditoria(nombre_tabla, pk_afectada);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(creado_en);
CREATE INDEX IF NOT EXISTS idx_auditoria_agente ON auditoria(id_agente);

CREATE INDEX IF NOT EXISTS idx_guardia_fecha ON guardia(fecha);
CREATE INDEX IF NOT EXISTS idx_guardia_agente ON guardia(id_agente);
CREATE INDEX IF NOT EXISTS idx_guardia_cronograma ON guardia(id_cronograma);
CREATE INDEX IF NOT EXISTS idx_guardia_activa ON guardia(activa);

CREATE INDEX IF NOT EXISTS idx_parte_diario_fecha ON parte_diario(fecha_parte);
CREATE INDEX IF NOT EXISTS idx_parte_diario_agente ON parte_diario(id_agente);
CREATE INDEX IF NOT EXISTS idx_parte_diario_area ON parte_diario(id_area);

CREATE INDEX IF NOT EXISTS idx_asistencia_agente ON asistencia(id_agente);
CREATE INDEX IF NOT EXISTS idx_asistencia_parte ON asistencia(id_parte_diario);
CREATE INDEX IF NOT EXISTS idx_asistencia_fecha ON asistencia(DATE(creado_en));

CREATE INDEX IF NOT EXISTS idx_licencia_agente ON licencia(id_agente);
CREATE INDEX IF NOT EXISTS idx_licencia_fechas ON licencia(fecha_desde, fecha_hasta);
CREATE INDEX IF NOT EXISTS idx_licencia_tipo ON licencia(id_tipo_licencia);

CREATE INDEX IF NOT EXISTS idx_resumen_guardia_agente_periodo ON resumen_guardia_mes(id_agente, anio, mes);

-- Índices para nuevas tablas
CREATE INDEX IF NOT EXISTS idx_agrupacion_nombre ON agrupacion(nombre);
CREATE INDEX IF NOT EXISTS idx_agrupacion_activo ON agrupacion(activo);

CREATE INDEX IF NOT EXISTS idx_feriado_fecha ON feriado(fecha);
CREATE INDEX IF NOT EXISTS idx_feriado_activo ON feriado(activo);

CREATE INDEX IF NOT EXISTS idx_parametros_area_area ON parametros_area(id_area);
CREATE INDEX IF NOT EXISTS idx_parametros_area_vigencia ON parametros_area(vigente_desde, vigente_hasta);
CREATE INDEX IF NOT EXISTS idx_parametros_area_activo ON parametros_area(activo);

CREATE INDEX IF NOT EXISTS idx_reglas_plus_vigencia ON reglas_plus(vigente_desde, vigente_hasta);
CREATE INDEX IF NOT EXISTS idx_reglas_plus_activa ON reglas_plus(activa);

-- Índices para texto (usando pg_trgm para búsquedas parciales)
CREATE INDEX IF NOT EXISTS idx_agente_nombre_trgm ON agente USING gin ((nombre || ' ' || apellido) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_area_nombre_trgm ON area USING gin (nombre gin_trgm_ops);

-- =====================================================
-- DATOS INICIALES BÁSICOS
-- =====================================================

-- Insertar roles básicos del sistema
INSERT INTO rol (nombre, descripcion) VALUES 
    ('administrador', 'Administrador del sistema'),
    ('jefe', 'Jefe de área'),
    ('director', 'Director'),
    ('agente', 'Agente estándar'),
    ('supervisor', 'Supervisor de guardias')
ON CONFLICT (nombre) DO NOTHING;

-- Insertar tipos de licencia comunes
INSERT INTO tipo_licencia (codigo, descripcion) VALUES 
    ('ANUAL', 'Licencia anual ordinaria'),
    ('ENFERMEDAD', 'Licencia por enfermedad'),
    ('MATERNIDAD', 'Licencia por maternidad'),
    ('PATERNIDAD', 'Licencia por paternidad'),
    ('ESPECIAL', 'Licencia especial'),
    ('ESTUDIO', 'Licencia por estudio'),
    ('FALLECIMIENTO', 'Licencia por fallecimiento familiar'),
    ('CASAMIENTO', 'Licencia por casamiento')
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- TABLAS DEL MÓDULO GUARDIAS
-- =====================================================

-- Tabla feriado (sin dependencias)
CREATE TABLE IF NOT EXISTS feriado (
    id_feriado BIGSERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    es_nacional BOOLEAN DEFAULT false,
    es_provincial BOOLEAN DEFAULT false,
    es_local BOOLEAN DEFAULT false,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla cronograma (depende de agente y area)
CREATE TABLE IF NOT EXISTS cronograma (
    id_cronograma BIGSERIAL PRIMARY KEY,
    id_jefe BIGINT NOT NULL REFERENCES agente(id_agente) ON DELETE CASCADE,
    id_area BIGINT NOT NULL REFERENCES area(id_area) ON DELETE CASCADE,
    fecha_aprobacion DATE,
    tipo VARCHAR(50),
    hora_inicio TIME,
    hora_fin TIME,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla guardia (depende de cronograma y agente)
CREATE TABLE IF NOT EXISTS guardia (
    id_guardia BIGSERIAL PRIMARY KEY,
    id_cronograma BIGINT NOT NULL REFERENCES cronograma(id_cronograma) ON DELETE CASCADE,
    id_agente BIGINT NOT NULL REFERENCES agente(id_agente) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    tipo VARCHAR(50),
    estado VARCHAR(50),
    horas_planificadas INTEGER,
    horas_efectivas INTEGER,
    observaciones TEXT,
    activa BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla reglas_plus (sin dependencias)
CREATE TABLE IF NOT EXISTS reglas_plus (
    id_regla_plus BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
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

-- Tabla parametros_area (depende de area)
CREATE TABLE IF NOT EXISTS parametros_area (
    id_parametros_area BIGSERIAL PRIMARY KEY,
    id_area BIGINT NOT NULL REFERENCES area(id_area) ON DELETE CASCADE,
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
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla resumen_guardia_mes (depende de agente)
CREATE TABLE IF NOT EXISTS resumen_guardia_mes (
    id_resumen_guardia_mes BIGSERIAL PRIMARY KEY,
    id_agente BIGINT NOT NULL REFERENCES agente(id_agente) ON DELETE CASCADE,
    mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
    anio INTEGER NOT NULL CHECK (anio >= 2020),
    total_horas_guardia INTEGER,
    horas_efectivas DECIMAL(6,2) DEFAULT 0.0,
    porcentaje_plus DECIMAL(5,2) DEFAULT 0.0,
    monto_calculado DECIMAL(10,2),
    estado_plus VARCHAR(30) DEFAULT 'pendiente',
    fecha_calculo TIMESTAMP,
    aprobado_en TIMESTAMP,
    plus20 BOOLEAN,
    plus40 BOOLEAN,
    UNIQUE(id_agente, mes, anio)
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_feriado_fecha ON feriado(fecha);
CREATE INDEX IF NOT EXISTS idx_feriado_activo ON feriado(activo);
CREATE INDEX IF NOT EXISTS idx_cronograma_area ON cronograma(id_area);
CREATE INDEX IF NOT EXISTS idx_cronograma_jefe ON cronograma(id_jefe);
CREATE INDEX IF NOT EXISTS idx_guardia_fecha ON guardia(fecha);
CREATE INDEX IF NOT EXISTS idx_guardia_agente ON guardia(id_agente);
CREATE INDEX IF NOT EXISTS idx_guardia_cronograma ON guardia(id_cronograma);
CREATE INDEX IF NOT EXISTS idx_resumen_mes_agente ON resumen_guardia_mes(id_agente);
CREATE INDEX IF NOT EXISTS idx_resumen_mes_periodo ON resumen_guardia_mes(mes, anio);

-- Insertar área por defecto
INSERT INTO area (nombre) VALUES 
    ('General')
ON CONFLICT (nombre) DO NOTHING;

-- Insertar algunos feriados nacionales por defecto
INSERT INTO feriado (fecha, descripcion, es_nacional) VALUES
    ('2025-01-01', 'Año Nuevo', true),
    ('2025-03-24', 'Día Nacional de la Memoria por la Verdad y la Justicia', true),
    ('2025-04-02', 'Día del Veterano y de los Caídos en la Guerra de Malvinas', true),
    ('2025-05-01', 'Día del Trabajador', true),
    ('2025-05-25', 'Día de la Revolución de Mayo', true),
    ('2025-06-20', 'Día de la Bandera', true),
    ('2025-07-09', 'Día de la Independencia', true),
    ('2025-08-17', 'Paso a la Inmortalidad del General José de San Martín', true),
    ('2025-10-12', 'Día del Respeto a la Diversidad Cultural', true),
    ('2025-11-20', 'Día de la Soberanía Nacional', true),
    ('2025-12-08', 'Inmaculada Concepción de María', true),
    ('2025-12-25', 'Navidad', true)
ON CONFLICT (fecha) DO NOTHING;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Tablas del sistema GIGA creadas exitosamente (incluye módulo guardias)';
END $$;