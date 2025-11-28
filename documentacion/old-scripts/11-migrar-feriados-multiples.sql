-- ========================================
-- Migración: Feriados Múltiples y Multi-Día
-- Fecha: 23 de Noviembre 2025
-- Descripción: Permite múltiples feriados por día y feriados de múltiples días
-- ========================================

-- 1. Crear tabla temporal con nueva estructura
CREATE TABLE IF NOT EXISTS feriado_nuevo (
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
    
    -- Constraints
    CONSTRAINT chk_fechas_validas CHECK (fecha_fin >= fecha_inicio)
);

-- 2. Crear índices para optimizar consultas de rango
CREATE INDEX IF NOT EXISTS idx_feriado_fecha_inicio ON feriado_nuevo (fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_feriado_fecha_fin ON feriado_nuevo (fecha_fin);
CREATE INDEX IF NOT EXISTS idx_feriado_rango ON feriado_nuevo (fecha_inicio, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_feriado_activo ON feriado_nuevo (activo) WHERE activo = true;

-- 3. Migrar datos existentes de la tabla anterior
INSERT INTO feriado_nuevo (
    nombre, 
    descripcion, 
    fecha_inicio, 
    fecha_fin, 
    es_nacional, 
    es_provincial, 
    es_local, 
    activo, 
    creado_en
)
SELECT 
    COALESCE(descripcion, 'Feriado') as nombre,  -- Usar descripción como nombre
    descripcion as descripcion,                   -- Mantener descripción
    fecha as fecha_inicio,                        -- Fecha actual como inicio
    fecha as fecha_fin,                          -- Misma fecha como fin (un día)
    es_nacional,
    es_provincial,
    es_local,
    activo,
    COALESCE(creado_en, CURRENT_TIMESTAMP)
FROM feriado 
WHERE activo = true;

-- 4. Respaldar tabla anterior y renombrar
ALTER TABLE IF EXISTS feriado RENAME TO feriado_backup_20251123;

-- 5. Renombrar nueva tabla
ALTER TABLE feriado_nuevo RENAME TO feriado;

-- 6. Función para verificar si una fecha es feriado
CREATE OR REPLACE FUNCTION es_fecha_feriado(fecha_consulta DATE)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM feriado 
        WHERE fecha_consulta BETWEEN fecha_inicio AND fecha_fin 
        AND activo = true
    );
END;
$$ LANGUAGE plpgsql;

-- 7. Función para obtener feriados en una fecha específica
CREATE OR REPLACE FUNCTION obtener_feriados_fecha(fecha_consulta DATE)
RETURNS TABLE(
    id_feriado BIGINT,
    nombre VARCHAR(200),
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    es_nacional BOOLEAN,
    es_provincial BOOLEAN,
    es_local BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id_feriado,
        f.nombre,
        f.descripcion,
        f.fecha_inicio,
        f.fecha_fin,
        f.es_nacional,
        f.es_provincial,
        f.es_local
    FROM feriado f
    WHERE fecha_consulta BETWEEN f.fecha_inicio AND f.fecha_fin
    AND f.activo = true
    ORDER BY f.fecha_inicio, f.nombre;
END;
$$ LANGUAGE plpgsql;

-- 8. Función para obtener feriados en un rango de fechas
CREATE OR REPLACE FUNCTION obtener_feriados_rango(
    fecha_inicio_consulta DATE,
    fecha_fin_consulta DATE
)
RETURNS TABLE(
    id_feriado BIGINT,
    nombre VARCHAR(200),
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    es_nacional BOOLEAN,
    es_provincial BOOLEAN,
    es_local BOOLEAN,
    duracion_dias INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id_feriado,
        f.nombre,
        f.descripcion,
        f.fecha_inicio,
        f.fecha_fin,
        f.es_nacional,
        f.es_provincial,
        f.es_local,
        (f.fecha_fin - f.fecha_inicio + 1)::INTEGER as duracion_dias
    FROM feriado f
    WHERE f.fecha_inicio <= fecha_fin_consulta 
    AND f.fecha_fin >= fecha_inicio_consulta
    AND f.activo = true
    ORDER BY f.fecha_inicio, f.nombre;
END;
$$ LANGUAGE plpgsql;

-- 9. Trigger para actualizar timestamp de modificación
CREATE OR REPLACE FUNCTION actualizar_feriado_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_feriado_actualizado
    BEFORE UPDATE ON feriado
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_feriado_timestamp();

-- 10. Vista para compatibilidad con código existente (temporal)
CREATE OR REPLACE VIEW feriado_simple AS
SELECT 
    id_feriado,
    nombre as descripcion,  -- Mantener compatibilidad
    fecha_inicio as fecha, -- Para código que espera campo 'fecha'
    es_nacional,
    es_provincial,
    es_local,
    activo,
    creado_en
FROM feriado;

-- 11. Insertar algunos feriados de ejemplo para testing
INSERT INTO feriado (nombre, descripcion, fecha_inicio, fecha_fin, es_nacional, activo) VALUES
('Año Nuevo', 'Celebración de Año Nuevo', '2025-01-01', '2025-01-01', true, true),
('Carnaval', 'Feriados de Carnaval', '2025-03-03', '2025-03-04', true, true),
('Semana Santa', 'Semana Santa - Jueves y Viernes Santo', '2025-04-17', '2025-04-18', true, true),
('Día del Trabajador', 'Día Internacional del Trabajador', '2025-05-01', '2025-05-01', true, true),
('Vacaciones de Invierno', 'Receso invernal educativo', '2025-07-14', '2025-07-25', false, true),
('Día de la Independencia', 'Declaración de Independencia Argentina', '2025-07-09', '2025-07-09', true, true);

-- 12. Verificar migración
DO $$
DECLARE
    feriados_originales INTEGER;
    feriados_migrados INTEGER;
BEGIN
    -- Contar feriados en tabla backup
    SELECT COUNT(*) INTO feriados_originales FROM feriado_backup_20251123 WHERE activo = true;
    
    -- Contar feriados migrados
    SELECT COUNT(*) INTO feriados_migrados FROM feriado WHERE activo = true;
    
    -- Log de verificación
    RAISE NOTICE 'Migración completada:';
    RAISE NOTICE '- Feriados originales: %', feriados_originales;
    RAISE NOTICE '- Feriados migrados: %', feriados_migrados;
    RAISE NOTICE '- Diferencia: %', (feriados_migrados - feriados_originales);
    
    -- Verificar que se mantuvieron los datos
    IF feriados_migrados < feriados_originales THEN
        RAISE WARNING 'Posible pérdida de datos en migración. Verificar manualmente.';
    END IF;
END $$;