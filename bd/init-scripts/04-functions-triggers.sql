-- =====================================================
-- FUNCIONES Y TRIGGERS SIMPLIFICADOS PARA SISTEMA GIGA  
-- =====================================================

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER 
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- Triggers para timestamps automáticos
CREATE TRIGGER update_agente_timestamp
    BEFORE UPDATE ON agente
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_cronograma_timestamp
    BEFORE UPDATE ON cronograma
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Función simplificada para validar fechas de licencia
CREATE OR REPLACE FUNCTION validar_fechas_licencia()
    RETURNS TRIGGER 
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.fecha_hasta < NEW.fecha_desde THEN
        RAISE EXCEPTION 'La fecha de fin no puede ser anterior a la fecha de inicio';
    END IF;
    
    RETURN NEW;
END;
$$;

-- Trigger para validación de licencias
CREATE TRIGGER validate_licencia
    BEFORE INSERT OR UPDATE ON licencia
    FOR EACH ROW
    EXECUTE FUNCTION validar_fechas_licencia();

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Funciones y triggers del sistema GIGA creados exitosamente';
END $$;