-- ========================================================================
-- MIGRACIÓN: Agregar campo horas_efectivas a tabla asistencia
-- Fecha: 9 de Diciembre 2025
-- Descripción: Agrega columna para almacenar las horas efectivas trabajadas
-- ========================================================================

-- Agregar columna horas_efectivas a la tabla asistencia
ALTER TABLE asistencia 
ADD COLUMN IF NOT EXISTS horas_efectivas DECIMAL(4,2);

-- Comentario sobre el campo
COMMENT ON COLUMN asistencia.horas_efectivas IS 'Horas trabajadas calculadas automáticamente (diferencia entre entrada y salida)';

-- Actualizar registros existentes con horas_efectivas calculadas
UPDATE asistencia 
SET horas_efectivas = ROUND(
    EXTRACT(EPOCH FROM (hora_salida - hora_entrada)) / 3600.0, 
    2
)
WHERE hora_entrada IS NOT NULL 
  AND hora_salida IS NOT NULL 
  AND hora_salida > hora_entrada
  AND horas_efectivas IS NULL;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'MIGRACIÓN COMPLETADA: horas_efectivas agregado';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'Campo agregado: asistencia.horas_efectivas DECIMAL(4,2)';
    RAISE NOTICE 'Registros actualizados: %', (SELECT COUNT(*) FROM asistencia WHERE horas_efectivas IS NOT NULL);
    RAISE NOTICE '=====================================================';
END $$;
