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

-- 1. Tabla base: area (sin dependencias)
CREATE TABLE IF NOT EXISTS area (
    id_area BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    FOREIGN KEY (id_area) REFERENCES area(id_area) ON DELETE RESTRICT
);

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
    plus20 BOOLEAN DEFAULT false,
    plus40 BOOLEAN DEFAULT false,
    total_horas_guardia INTEGER DEFAULT 0,
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

-- Insertar área por defecto
INSERT INTO area (nombre) VALUES 
    ('General')
ON CONFLICT (nombre) DO NOTHING;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Tablas del sistema GIGA creadas exitosamente';
END $$;