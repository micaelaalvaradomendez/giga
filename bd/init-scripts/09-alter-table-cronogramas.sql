-- bd/init-scripts/10-migracion-cronograma-guardias.sql
BEGIN;

-- =========================================================
-- A) SCHEMA: agregar columnas nuevas en cronograma
-- =========================================================
ALTER TABLE cronograma
  ADD COLUMN IF NOT EXISTS anio INT,
  ADD COLUMN IF NOT EXISTS mes INT,
  ADD COLUMN IF NOT EXISTS fecha_desde DATE,
  ADD COLUMN IF NOT EXISTS fecha_hasta DATE,
  ADD COLUMN IF NOT EXISTS creado_por_rol VARCHAR(50),
  ADD COLUMN IF NOT EXISTS creado_por_id BIGINT,
  ADD COLUMN IF NOT EXISTS aprobado_por_id BIGINT;

-- =========================================================
-- B) BACKFILL: completar anio/mes/fechas para cronogramas existentes
-- =========================================================
-- Usa fecha_creacion o creado_en (si alguna es NULL, cae en la otra)
UPDATE cronograma
SET
  anio = COALESCE(anio, EXTRACT(YEAR FROM COALESCE(fecha_creacion, creado_en))::INT),
  mes  = COALESCE(mes,  EXTRACT(MONTH FROM COALESCE(fecha_creacion, creado_en))::INT),
  fecha_desde = COALESCE(fecha_desde, DATE_TRUNC('month', COALESCE(fecha_creacion, creado_en))::DATE),
  fecha_hasta = COALESCE(fecha_hasta, (DATE_TRUNC('month', COALESCE(fecha_creacion, creado_en)) + INTERVAL '1 month - 1 day')::DATE)
WHERE
  anio IS NULL OR mes IS NULL OR fecha_desde IS NULL OR fecha_hasta IS NULL;

-- Backfill de creado_por_* (opcional pero recomendable)
UPDATE cronograma
SET creado_por_id = COALESCE(creado_por_id, id_jefe)
WHERE creado_por_id IS NULL AND id_jefe IS NOT NULL;

UPDATE cronograma
SET creado_por_rol = COALESCE(creado_por_rol, 'jefatura')
WHERE creado_por_rol IS NULL;

-- =========================================================
-- C) ÍNDICES / UNIQUE parcial (pendiente)
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_cronograma_anio_mes
  ON cronograma(anio, mes);

CREATE INDEX IF NOT EXISTS idx_cronograma_area_anio_mes_estado
  ON cronograma(id_area, anio, mes, estado);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='public'
      AND indexname='ux_cronograma_area_mes_anio_pendiente'
  ) THEN
    EXECUTE '
      CREATE UNIQUE INDEX ux_cronograma_area_mes_anio_pendiente
      ON cronograma(id_area, anio, mes)
      WHERE estado = ''pendiente'';
    ';
  END IF;
END $$;

-- =========================================================
-- D) FKs creado_por_id / aprobado_por_id (si faltan)
-- =========================================================
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY'
      AND table_name = 'cronograma'
      AND constraint_name = 'fk_cronograma_creado_por'
  ) THEN
    ALTER TABLE cronograma
      ADD CONSTRAINT fk_cronograma_creado_por
      FOREIGN KEY (creado_por_id) REFERENCES agente(id_agente)
      ON DELETE SET NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY'
      AND table_name = 'cronograma'
      AND constraint_name = 'fk_cronograma_aprobado_por'
  ) THEN
    ALTER TABLE cronograma
      ADD CONSTRAINT fk_cronograma_aprobado_por
      FOREIGN KEY (aprobado_por_id) REFERENCES agente(id_agente)
      ON DELETE SET NULL;
  END IF;
END $$;

-- =========================================================
-- E) DATA: “lo que hicimos tocando seeds” pero en DB existente
--     -> crear 3 cronogramas publicados (sep/oct/nov 2025) si no existen
-- =========================================================
WITH meses AS (
  SELECT * FROM (VALUES
    ('2025-09-01'::DATE),
    ('2025-10-01'::DATE),
    ('2025-11-01'::DATE)
  ) AS v(mes_fecha)
),
refs AS (
  SELECT
    (SELECT id_agente FROM agente WHERE legajo = '004' LIMIT 1) AS jefe_id,
    (SELECT id_agente FROM agente WHERE legajo = '003' LIMIT 1) AS director_id,
    (SELECT id_area FROM area LIMIT 1) AS area_id
)
INSERT INTO cronograma (
  id_jefe, id_director, id_area, tipo, hora_inicio, hora_fin,
  estado, fecha_creacion, fecha_aprobacion,
  creado_por_rol, creado_por_id, aprobado_por_id,
  anio, mes, fecha_desde, fecha_hasta,
  creado_en, actualizado_en
)
SELECT
  refs.jefe_id,
  refs.director_id,
  refs.area_id,
  'regular',
  '08:00'::TIME,
  '16:00'::TIME,
  'publicada',
  meses.mes_fecha,
  meses.mes_fecha + INTERVAL '2 days',
  'jefatura',
  refs.jefe_id,
  refs.director_id,
  EXTRACT(YEAR FROM meses.mes_fecha)::INT,
  EXTRACT(MONTH FROM meses.mes_fecha)::INT,
  DATE_TRUNC('month', meses.mes_fecha)::DATE,
  (DATE_TRUNC('month', meses.mes_fecha) + INTERVAL '1 month - 1 day')::DATE,
  NOW(),
  NOW()
FROM meses
CROSS JOIN refs
WHERE refs.jefe_id IS NOT NULL
  AND refs.director_id IS NOT NULL
  AND refs.area_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM cronograma c
    WHERE c.id_area = refs.area_id
      AND c.estado = 'publicada'
      AND c.anio = EXTRACT(YEAR FROM meses.mes_fecha)::INT
      AND c.mes  = EXTRACT(MONTH FROM meses.mes_fecha)::INT
  );

-- =========================================================
-- F) DATA: guardias ejemplo asociadas al primer cronograma (si no existen)
--     (IMPORTANTE: no duplicar)
-- =========================================================
WITH base AS (
  SELECT (SELECT id_cronograma FROM cronograma ORDER BY id_cronograma ASC LIMIT 1) AS cronograma_id
),
fechas AS (
  SELECT * FROM (VALUES
    ('2025-09-15'::DATE),
    ('2025-10-15'::DATE),
    ('2025-11-15'::DATE)
  ) AS v(fecha_guardia)
),
agentes AS (
  SELECT id_agente
  FROM agente
  WHERE activo = true
  ORDER BY id_agente
  LIMIT 20
)
INSERT INTO guardia (
  id_cronograma, id_agente, fecha,
  hora_inicio, hora_fin, tipo, estado, activa,
  horas_planificadas, horas_efectivas,
  observaciones, creado_en, actualizado_en
)
SELECT
  base.cronograma_id,
  a.id_agente,
  f.fecha_guardia,
  '08:00'::TIME,
  '16:00'::TIME,
  'regular',
  'planificada',
  true,
  8,
  8,
  'Guardia de ejemplo',
  NOW(),
  NOW()
FROM base
JOIN agentes a ON true
JOIN fechas f ON true
WHERE base.cronograma_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM guardia g
    WHERE g.id_cronograma = base.cronograma_id
      AND g.id_agente = a.id_agente
      AND g.fecha = f.fecha_guardia
      AND g.hora_inicio = '08:00'::TIME
      AND g.hora_fin = '16:00'::TIME
  );

COMMIT;
