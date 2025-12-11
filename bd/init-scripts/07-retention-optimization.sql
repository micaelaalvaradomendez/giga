-- ========================================================================
-- SCRIPT: Retention & Optimization - Database Space Management
-- Fecha: Diciembre 2025
-- Descripción: Tablas de archivo, índices adicionales y funciones de retención
--              para optimizar el uso de espacio en la base de datos
-- ========================================================================

-- =====================================================
-- 1. TABLA DE ARCHIVO DE AUDITORÍA
-- =====================================================

-- Tabla para archivar registros de auditoría antiguos
CREATE TABLE IF NOT EXISTS auditoria_archivo (
    id_auditoria BIGINT PRIMARY KEY,
    pk_afectada BIGINT,
    nombre_tabla VARCHAR(100),
    creado_en TIMESTAMP,
    valor_previo JSONB,
    valor_nuevo JSONB,
    accion VARCHAR(50) NOT NULL,
    id_agente BIGINT,
    archivado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consultas en archivo
CREATE INDEX IF NOT EXISTS idx_auditoria_archivo_fecha ON auditoria_archivo(creado_en DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_archivo_tabla ON auditoria_archivo(nombre_tabla);
CREATE INDEX IF NOT EXISTS idx_auditoria_archivo_agente ON auditoria_archivo(id_agente);
CREATE INDEX IF NOT EXISTS idx_auditoria_archivo_archivado ON auditoria_archivo(archivado_en DESC);

COMMENT ON TABLE auditoria_archivo IS 'Archivo histórico de registros de auditoría para reducir tamaño de tabla principal';

-- =====================================================
-- 2. TABLA DE ARCHIVO DE INCIDENCIAS
-- =====================================================

-- Tabla para archivar incidencias cerradas/resueltas antiguas
CREATE TABLE IF NOT EXISTS incidencia_archivo (
    id BIGINT PRIMARY KEY,
    numero VARCHAR(20) UNIQUE NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(25) NOT NULL,
    prioridad VARCHAR(10) NOT NULL,
    creado_por BIGINT NOT NULL,
    asignado_a BIGINT,
    area_involucrada BIGINT NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL,
    fecha_asignacion TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    resolucion TEXT,
    comentarios_seguimiento JSONB,
    creado_en TIMESTAMP,
    actualizado_en TIMESTAMP,
    archivado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consultas en archivo de incidencias
CREATE INDEX IF NOT EXISTS idx_incidencia_archivo_numero ON incidencia_archivo(numero);
CREATE INDEX IF NOT EXISTS idx_incidencia_archivo_fecha ON incidencia_archivo(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_incidencia_archivo_estado ON incidencia_archivo(estado);
CREATE INDEX IF NOT EXISTS idx_incidencia_archivo_archivado ON incidencia_archivo(archivado_en DESC);

COMMENT ON TABLE incidencia_archivo IS 'Archivo histórico de incidencias cerradas para reducir tamaño de tabla principal';

-- =====================================================
-- 3. ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices compuestos para auditoría (optimización de consultas comunes)
CREATE INDEX IF NOT EXISTS idx_auditoria_tabla_fecha ON auditoria(nombre_tabla, creado_en DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_agente_fecha ON auditoria(id_agente, creado_en DESC);

-- Índice para limpieza de sesiones
CREATE INDEX IF NOT EXISTS idx_sesion_activa_limpieza ON sesion_activa(activa, ultimo_acceso);

-- Índice para django_session expire
CREATE INDEX IF NOT EXISTS idx_django_session_expire ON django_session(expire_date) WHERE expire_date < CURRENT_TIMESTAMP;

-- =====================================================
-- 4. FUNCIONES DE ARCHIVADO
-- =====================================================

-- Función para archivar auditorías antiguas
CREATE OR REPLACE FUNCTION archivar_auditorias(meses_antiguedad INTEGER DEFAULT 6)
RETURNS TABLE(total_archivados BIGINT, total_eliminados BIGINT) AS $$
DECLARE
    fecha_corte TIMESTAMP;
    archivados BIGINT;
    eliminados BIGINT;
BEGIN
    fecha_corte := CURRENT_TIMESTAMP - (meses_antiguedad || ' months')::INTERVAL;
    
    -- Mover a tabla de archivo
    INSERT INTO auditoria_archivo (id_auditoria, pk_afectada, nombre_tabla, creado_en, valor_previo, valor_nuevo, accion, id_agente)
    SELECT id_auditoria, pk_afectada, nombre_tabla, creado_en, valor_previo, valor_nuevo, accion, id_agente
    FROM auditoria
    WHERE creado_en < fecha_corte
    ON CONFLICT (id_auditoria) DO NOTHING;
    
    GET DIAGNOSTICS archivados = ROW_COUNT;
    
    -- Eliminar de tabla principal
    DELETE FROM auditoria WHERE creado_en < fecha_corte;
    
    GET DIAGNOSTICS eliminados = ROW_COUNT;
    
    RETURN QUERY SELECT archivados, eliminados;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archivar_auditorias IS 'Mueve registros de auditoría más antiguos de N meses a tabla de archivo';

-- Función para archivar incidencias cerradas antiguas
CREATE OR REPLACE FUNCTION archivar_incidencias(meses_antiguedad INTEGER DEFAULT 12)
RETURNS TABLE(total_archivados BIGINT, total_eliminados BIGINT) AS $$
DECLARE
    fecha_corte TIMESTAMP;
    archivados BIGINT;
    eliminados BIGINT;
BEGIN
    fecha_corte := CURRENT_TIMESTAMP - (meses_antiguedad || ' months')::INTERVAL;
    
    -- Mover a tabla de archivo solo incidencias cerradas o resueltas
    INSERT INTO incidencia_archivo (id, numero, titulo, descripcion, estado, prioridad, creado_por, asignado_a, area_involucrada, fecha_creacion, fecha_asignacion, fecha_resolucion, resolucion, comentarios_seguimiento, creado_en, actualizado_en)
    SELECT id, numero, titulo, descripcion, estado, prioridad, creado_por, asignado_a, area_involucrada, fecha_creacion, fecha_asignacion, fecha_resolucion, resolucion, comentarios_seguimiento, creado_en, actualizado_en
    FROM incidencia
    WHERE estado IN ('cerrada', 'resuelta')
      AND fecha_resolucion < fecha_corte
    ON CONFLICT (id) DO NOTHING;
    
    GET DIAGNOSTICS archivados = ROW_COUNT;
    
    -- Eliminar de tabla principal
    DELETE FROM incidencia 
    WHERE estado IN ('cerrada', 'resuelta')
      AND fecha_resolucion < fecha_corte;
    
    GET DIAGNOSTICS eliminados = ROW_COUNT;
    
    RETURN QUERY SELECT archivados, eliminados;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archivar_incidencias IS 'Mueve incidencias cerradas/resueltas más antiguas de N meses a tabla de archivo';

-- Función para limpiar sesiones expiradas
CREATE OR REPLACE FUNCTION limpiar_sesiones_expiradas(dias_antiguedad INTEGER DEFAULT 7)
RETURNS TABLE(sesiones_activas_eliminadas BIGINT, django_sessions_eliminadas BIGINT) AS $$
DECLARE
    fecha_corte TIMESTAMP WITH TIME ZONE;
    sa_eliminadas BIGINT;
    ds_eliminadas BIGINT;
    session_keys TEXT[];
BEGIN
    fecha_corte := CURRENT_TIMESTAMP - (dias_antiguedad || ' days')::INTERVAL;
    
    -- Obtener session_keys a eliminar
    SELECT ARRAY_AGG(session_key) INTO session_keys
    FROM sesion_activa
    WHERE activa = FALSE OR ultimo_acceso < fecha_corte;
    
    -- Eliminar de django_session
    IF session_keys IS NOT NULL AND array_length(session_keys, 1) > 0 THEN
        DELETE FROM django_session WHERE session_key = ANY(session_keys);
        GET DIAGNOSTICS ds_eliminadas = ROW_COUNT;
    ELSE
        ds_eliminadas := 0;
    END IF;
    
    -- Eliminar de sesion_activa
    DELETE FROM sesion_activa 
    WHERE activa = FALSE OR ultimo_acceso < fecha_corte;
    
    GET DIAGNOSTICS sa_eliminadas = ROW_COUNT;
    
    -- Limpiar sesiones Django expiradas adicionales
    DELETE FROM django_session WHERE expire_date < CURRENT_TIMESTAMP;
    
    RETURN QUERY SELECT sa_eliminadas, ds_eliminadas;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION limpiar_sesiones_expiradas IS 'Limpia sesiones inactivas y expiradas de ambas tablas de sesiones';

-- =====================================================
-- 5. VISTA PARA ESTADÍSTICAS DE TABLAS
-- =====================================================

CREATE OR REPLACE VIEW v_estadisticas_tablas AS
SELECT 
    schemaname,
    relname as tabla,
    n_live_tup as filas_vivas,
    n_dead_tup as filas_muertas,
    pg_size_pretty(pg_total_relation_size(relid)) as tamano_total,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE relname IN ('auditoria', 'auditoria_archivo', 'incidencia', 'incidencia_archivo', 
                   'sesion_activa', 'django_session', 'asistencia', 'guardia', 'licencia')
ORDER BY pg_total_relation_size(relid) DESC;

COMMENT ON VIEW v_estadisticas_tablas IS 'Vista de estadísticas de tablas principales para monitoreo de espacio';

-- =====================================================
-- FIN DEL SCRIPT DE RETENCIÓN Y OPTIMIZACIÓN
-- =====================================================
