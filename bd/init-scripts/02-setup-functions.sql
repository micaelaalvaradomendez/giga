-- Configuración inicial de la base de datos GIGA
-- Este archivo se ejecuta después de la creación de la base de datos

-- Configurar zona horaria
SET timezone = 'America/Argentina/Buenos_Aires';

-- Configurar búsqueda en español
SET default_text_search_config = 'spanish';

-- Crear esquemas adicionales si son necesarios
-- CREATE SCHEMA IF NOT EXISTS auth;
-- CREATE SCHEMA IF NOT EXISTS logs;

-- Función para timestamps automáticos
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Función para generar UUIDs
CREATE OR REPLACE FUNCTION generate_nanoid(size int DEFAULT 21)
RETURNS text AS $$
DECLARE
    alphabet text := '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    idBuilder text := '';
    i int := 0;
    bytes bytea;
    alphabetIndex int;
    alphabetArray text[];
    alphabetLength int := 62;
BEGIN
    alphabetArray := regexp_split_to_array(alphabet, '');
    bytes := gen_random_bytes(size);
    
    WHILE i < size LOOP
        alphabetIndex := (get_byte(bytes, i) % alphabetLength) + 1;
        idBuilder := idBuilder || alphabetArray[alphabetIndex];
        i := i + 1;
    END LOOP;
    
    RETURN idBuilder;
END
$$ LANGUAGE plpgsql VOLATILE;

-- Comentarios para documentación
COMMENT ON DATABASE giga IS 'Base de datos principal del sistema GIGA';
COMMENT ON FUNCTION update_modified_column() IS 'Función para actualizar automáticamente el campo updated_at';
COMMENT ON FUNCTION generate_nanoid(int) IS 'Genera un ID único usando NanoID';