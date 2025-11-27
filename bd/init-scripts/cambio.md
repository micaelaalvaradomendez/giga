Documentación de Cambios: Scripts Consolidados
Resumen Ejecutivo
Se consolidaron 12 scripts SQL incrementales en 3 scripts limpios finales que contienen el estado completo de la base de datos del sistema GIGA.

Archivos Generados
CONSOLIDATED-01-tables-final.sql - Todas las tablas (29 tablas)
CONSOLIDATED-02-functions-final.sql - Todas las funciones y triggers
CONSOLIDATED-03-seed-data.sql - Datos iniciales organizacionales
Mapeo de Archivos Originales a Consolidados
Scripts Consolidado 01: Tablas Finales
Reemplaza:

03-create-tables.sql
 - Tablas base originales
06-add-approval-tracking.sql
 - ALTER TABLE para aprobación jerárquica + hora_compensacion
08-refactor-asistencia.sql
 - Refactorización completa de asistencia
09-django-tables.sql
 - Tablas de Django
11-migrar-feriados-multiples.sql
 - Nueva estructura de feriados con rangos
12-actualizar-licencias.sql
 - Campos extendidos de licencias
Total: 29 tablas consolidadas con todas las modificaciones incluidas

Scripts Consolidado 02: Funciones Finales
Reemplaza:

02-setup-functions.sql
 - Funciones de setup básicas
04-functions-triggers.sql
 - Triggers y validaciones base
06-add-approval-tracking.sql
 - Funciones de compensaciones
07-actualizar-funcion-plus-compensaciones.sql
 - Actualización de cálculo de plus v2.0
08-refactor-asistencia.sql
 - Funciones de asistencia y auditoría
11-migrar-feriados-multiples.sql
 - Funciones de feriados por rango
12-actualizar-licencias.sql
 - Trigger de actualización de licencias
Total: Todas las funciones con versiones actualizadas

Scripts Consolidado 03: Datos Iniciales
Reemplaza:

05-seed-data.sql
 - Datos completos con estructura jerárquica actualizada
Incluye actualización de feriados para usar nueva estructura (fecha_inicio/fecha_fin)
Cambios Principales por Categoría
1. Aprobación Jerárquica de Cronogramas
Script Original: 06-add-approval-tracking.sql

Cambios en tabla 
cronograma
:

ALTER TABLE cronograma ADD COLUMN creado_por_rol VARCHAR(50);
ALTER TABLE cronograma ADD COLUMN creado_por_id BIGINT;
ALTER TABLE cronograma ADD COLUMN aprobado_por_id BIGINT;
Impacto: Permite rastrear quién crea y quién aprueba cada cronograma, habilitando flujos de aprobación jerárquica.

2. Sistema de Compensación de Horas Extra
Script Original: 06-add-approval-tracking.sql

Nueva tabla: 
hora_compensacion

Registra horas de emergencia que exceden el límite de 10 horas
Incluye validaciones automáticas (máximo 8 horas extra, máximo 18 horas totales)
Estado: pendiente, aprobada, rechazada, pagada
Motivo: siniestro, emergencia, operativo, refuerzo, otro
Compensación: pago, franco, plus
Funciones asociadas:

actualizar_horas_compensacion() - Trigger que calcula horas automáticamente
obtener_resumen_compensaciones_agente() - Resumen mensual por agente
validar_compensacion() - Validaciones de límites y requisitos
3. Asistencia Refactorizada
Script Original: 08-refactor-asistencia.sql

Cambios en tabla asistencia:

DROP completo de tabla anterior
Nueva estructura con soporte para:
Marcación automática de salida a las 22:00
Correcciones manuales por administrador
Marcación con DNI
Nueva tabla: intento_marcacion_fraudulenta

Registra intentos de marcar con DNI ajeno
Incluye IP address para auditoría
Funciones:

marcar_salidas_automaticas() - Marca automáticamente salida a 22:00
obtener_estado_asistencia() - Consulta estado actual
Triggers de auditoría para cambios
4. Feriados con Soporte de Rangos Múltiples
Script Original: 11-migrar-feriados-multiples.sql

Cambios en tabla 
feriado
:

-- ANTES:
fecha DATE  -- Un solo día
-- DESPUÉS:
fecha_inicio DATE
fecha_fin DATE  -- Permite feriados de múltiples días
nombre VARCHAR(200)  -- Nuevo campo
Permite:

Feriados de un solo día (fecha_inicio = fecha_fin)
Feriados de múltiples días (ej: Semana Santa, Carnaval)
Múltiples feriados en la misma fecha
Funciones actualizadas:

es_fecha_feriado() - Verifica rangos en lugar de fecha única
obtener_feriados_fecha() - Retorna todos los feriados de una fecha
obtener_feriados_rango() - Consulta por rango de fechas
5. Licencias Extendidas
Script Original: 12-actualizar-licencias.sql

Campos agregados a tabla 
licencia
:

observaciones TEXT
justificacion TEXT
aprobada_por BIGINT
fecha_aprobacion DATE
observaciones_aprobacion TEXT
rechazada_por BIGINT
fecha_rechazo DATE
motivo_rechazo TEXT
solicitada_por BIGINT
creado_en TIMESTAMP
actualizado_en TIMESTAMP
Beneficios:

Flujo completo de solicitud-aprobación-rechazo
Auditoría detallada de todo el ciclo de vida
Observaciones en cada etapa
6. Cálculo de Plus v2.0 con Compensaciones
Script Original: 07-actualizar-funcion-plus-compensaciones.sql

Función actualizada: calcular_plus_agente()

Cambios principales:

-- ANTES (v1.0):
Solo contaba horas de guardias regulares
-- DESPUÉS (v2.0):
Suma guardias + compensaciones aprobadas
Reglas actualizadas:

Área operativa + guardias/compensaciones = 40%
Otras áreas + 32+ horas (incluyendo compensaciones) = 40%
Cualquier guardia/compensación = 20%
Sin guardias ni compensaciones = 0%
Nueva función: detalle_calculo_plus_agente() para debugging y transparencia

7. Tablas Django
Script Original: 09-django-tables.sql

Tablas agregadas:

django_migrations - Tracking de migraciones
django_content_type - Tipos de contenido
django_session - Sesiones de usuario
auth_permission, auth_group, auth_user - Autenticación
auth_group_permissions, auth_user_groups, auth_user_user_permissions - Relaciones
django_admin_log - Log administrativo
Total: 9 tablas adicionales para Django

Scripts que NO Cambiaron (se mantienen)
01-init-database.sh
Script de inicialización bash que ejecuta los otros scripts en orden.

Acción recomendada: Actualizar para ejecutar los 3 nuevos scripts consolidados en lugar de los 12 originales.

10-guardias-historicas.sql
Genera datos de prueba históricos para desarrollo.

Acción recomendada: Mantener como está, ejecutar después de los scripts consolidados.

Problema Real Encontrado
❗ Las migraciones de Django NO están aplicadas

You have 4 unapplied migration(s). Your project may not work properly until 
you apply the migrations for app(s): asistencia, auditoria, guardias, personas.
Run 'python manage.py migrate' to apply them.
Causa del Problema en el Frontend
El frontend no carga datos NO porque falten datos en la BD, sino porque:

Las migraciones de Django no coinciden con el esquema de la BD
Esto causa inconsistencias en los serializadores de Django
Los endpoints API retornan errores o datos incompletos
Solución
docker exec giga-django python manage.py migrate
O reiniciar los contenedores para que Django aplique las migraciones:

docker-compose down
docker-compose up -d
Verificación de Datos
La base de datos SÍ tiene datos:

SELECT COUNT(*) FROM agente;   -- 12 agentes
SELECT COUNT(*) FROM area;     -- 31 áreas  
SELECT COUNT(*) FROM guardia;  -- 15 guardias
El backend SÍ se conecta:

$ curl http://localhost:8000/api/personas/agentes/
{"count":12,"results":[...]}  ✅
Orden de Ejecución Recomendado
CONSOLIDATED-01-tables-final.sql - Crear todas las tablas
CONSOLIDATED-02-functions-final.sql - Crear funciones y triggers
CONSOLIDATED-03-seed-data.sql - Insertar datos iniciales
10-guardias-historicas.sql (original) - Datos de prueba históricos
python manage.py migrate - Aplicar migraciones de Django ⚠️ CRUCIAL
Comparación: Scripts Originales vs Consolidados
Scripts Originales (12 archivos)
01-init-database.sh          → Script de ejecución
02-setup-functions.sql       → \
03-create-tables.sql         → |
04-functions-triggers.sql    → |
05-seed-data.sql             → |
06-add-approval-tracking.sql → |  Consolidados en 3 archivos
07-actualizar-funcion-plus...→ |
08-refactor-asistencia.sql   → |
09-django-tables.sql         → |
10-guardias-historicas.sql   → Mantener como está
11-migrar-feriados-mult...   → |
12-actualizar-licencias.sql  → /
Scripts Consolidados (3 archivos)
CONSOLIDATED-01-tables-final.sql    → 29 tablas finales
CONSOLIDATED-02-functions-final.sql → Todas las funciones
CONSOLIDATED-03-seed-data.sql       → Datos organizacionales
+ 10-guardias-historicas.sql (sin cambios)
Beneficios de la Consolidación
Claridad: Estado final de la BD en 3 archivos en lugar de 12
Mantenibilidad: Más fácil entender la estructura completa
Sin ALTER TABLE: Todas las tablas se crean con su forma final
Menos errores: No hay dependencias entre múltiples scripts
Documentación: Este archivo explica todos los cambios
Notas de Compatibilidad
Coherencia Backend-BD
Los modelos Django en /back/ apps (personas, guardias, asistencia, auditoria) deben coincidir con las tablas SQL.

Verificar:

Nombres de campos coinciden
Tipos de datos son compatibles
Foreign keys están correctamente definidas
Ejecutar después de aplicar scripts:

python manage.py makemigrations --dry-run
python manage.py migrate
Resumen de Funcionalidades por Script
Script	Funcionalidades Clave
01-tables	29 tablas: dominio + asistencia + licencias + Django + compensaciones
02-functions	Timestamps, validaciones, compensaciones, asistencia, plus v2.0, feriados
03-seed-data	5 roles, 3 tipos licencia, 31 áreas jerárquicas, 12 agentes, feriados 2025
Fecha de consolidación: 27 de Noviembre 2025
Sistema: GIGA - Gestión Integral de Guardias y Asistencias
Organización: Protección Civil - Tierra del Fuego

