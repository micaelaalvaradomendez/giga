# Sistema GIGA - Tareas Pendientes
## Guía de Acción para Completar el Proyecto

**Última actualización**: 27 de Noviembre de 2025  
**Estado del proyecto**: 🟢 Funcionalidades Core Completas | 🔴 Seguridad y Reportes Pendientes

---

## 📊 Resumen de Tareas

| Prioridad | Tareas | Estimación Total |
|-----------|--------|------------------|
| 🔴 **CRÍTICA** | 5 tareas | 25-35 horas |
| 🟡 **ALTA** | 4 tareas | 20-25 horas |
| 🟢 **MEDIA** | 3 tareas | 15-20 horas |
| 🔵 **BAJA** | 2 tareas | 10-15 horas |

**Total estimado**: 70-95 horas de trabajo

---

## 🔴 PRIORIDAD CRÍTICA

Estas tareas **DEBEN completarse** antes de subir el sistema a producción.

---

### TAREA 1: Reactivar Autenticación Completa 🔴

**Problema**: Muchos endpoints tienen `permission_classes = [AllowAny]` lo que permite acceso sin autenticación.

**¿Qué hacer?**

1. **Buscar todos los endpoints sin autenticación**
   - Abrir cada archivo de views en `back/`
   - Buscar: `permission_classes = [AllowAny]`
   - Hacer una lista de cuántos endpoints encontraste

2. **Cambiar a autenticación requerida**
   - Cambiar `[AllowAny]` por `[IsAuthenticated]`
   - Archivos a revisar:
     - `back/personas/views.py`
     - `back/asistencia/views.py`
     - `back/guardias/views.py`
     - `back/auditoria/views.py`

**Qué tener en cuenta:**
- ⚠️ La marcación de asistencia por DNI debe seguir requiriendo autenticación
- ⚠️ Los reportes también necesitan autenticación para saber qué datos mostrar según el rol
- ⚠️ El endpoint de login (`/auth/login/`) SÍ debe quedar con `AllowAny`

**Estimación**: 2-3 horas

**Verificación**:
- [ ] Intentar acceder a un endpoint sin token → debe dar error 401
- [ ] Hacer login y obtener token
- [ ] Acceder con el token → debe funcionar
- [ ] Probar desde el frontend que todo siga funcionando

---

### TAREA 2: Implementar Validación de Rol Administrador 🔴

**Problema**: Cualquier usuario puede crear, editar o eliminar agentes.

**¿Qué hacer?**

1. **Ir a `back/personas/views.py`**
   
2. **Buscar estas funciones:**
   - `create_agente()`
   - `update_agente()`
   - `delete_agente()`

3. **Agregar validación al inicio de cada función:**
   - Obtener el agente que está haciendo la petición
   - Obtener su rol usando la función `get_agente_rol(agente)`
   - Si el rol NO es 'administrador', retornar error 403

**Qué tener en cuenta:**
- ⚠️ Solo administradores pueden hacer estas operaciones
- ⚠️ La función `get_agente_rol()` ya existe en `guardias/utils.py`, puedes importarla
- ⚠️ El mensaje de error debe ser claro: "Solo administradores pueden crear/editar/eliminar agentes"

**Estimación**: 3-4 horas

**Verificación**:
- [ ] Login como agente normal
- [ ] Intentar crear un agente → debe dar error 403
- [ ] Login como administrador
- [ ] Crear un agente → debe funcionar
- [ ] Editar un agente → debe funcionar
- [ ] Eliminar un agente → debe funcionar

---

### TAREA 3: Implementar Filtros por Rol en Asistencias 🔴

**Problema**: Todos los usuarios ven todas las asistencias de toda la organización.

**¿Qué hacer?**

1. **Ir a `back/asistencia/views.py`**

2. **Buscar la función `listar_asistencias()`**

3. **Agregar lógica de filtrado:**
   - Obtener el rol del usuario autenticado
   - Según el rol, filtrar el queryset:
     - **Agente**: Solo sus propias asistencias
     - **Jefatura**: Asistencias de su área
     - **Director**: Asistencias de las áreas bajo su dirección
     - **Administrador**: Todas las asistencias (sin filtro)

**Qué tener en cuenta:**
- ⚠️ El filtro debe aplicarse SIEMPRE, no opcional
- ⚠️ Para jefatura y director, tienes que obtener las áreas que gestionan
- ⚠️ Los filtros de fecha y otros parámetros deben seguir funcionando, pero DENTRO del conjunto permitido

**Estimación**: 4-5 horas

**Verificación**:
- [ ] Login como agente y verificar que solo ve sus asistencias
- [ ] Login como jefatura y verificar que ve solo su área
- [ ] Login como administrador y verificar que ve todas
- [ ] Probar que los filtros por fecha siguen funcionando

---

### TAREA 4: Completar Funcionalidad de Reportes 🔴

**Problema**: Los reportes tienen datos de prueba hardcodeados en lugar de leer de la base de datos real.

**¿Qué hacer?**

1. **Ir a `back/guardias/views.py`**

2. **Buscar estas funciones:**
   - `exportar_pdf()`
   - `exportar_excel()`
   - `exportar_csv()`

3. **Buscar las funciones auxiliares:**
   - `_generar_tabla_pdf()`
   - `_generar_datos_csv()`

4. **Reemplazar datos hardcodeados con consultas reales:**
   - Identificar qué tipo de reporte se está generando
   - Hacer consulta a la base de datos según el tipo
   - Aplicar filtros por fechas si se enviaron
   - Aplicar filtros por ROL (solo mostrar datos que el usuario puede ver)

**Qué tener en cuenta:**
- ⚠️ Cada tipo de reporte necesita una consulta diferente:
  - Individual: Guardias de un agente específico
  - Mensual: Todas las guardias del mes
  - Asistencia: Parte diario del día
  - Compensaciones: Lista de compensaciones
- ⚠️ TODOS los reportes deben respetar el rol del usuario
- ⚠️ Los datos de ejemplo están bien para la estructura, pero cambiarlos por datos reales
- ⚠️ Validar que los filtros de fecha funcionan correctamente

**Estimación**: 8-10 horas

**Verificación**:
- [ ] Generar reporte PDF con datos reales
- [ ] Verificar que el PDF se abre correctamente
- [ ] Verificar que los datos coinciden con la base de datos
- [ ] Generar reporte Excel y abrirlo
- [ ] Generar reporte CSV y abrirlo
- [ ] Probar con diferentes filtros de fecha
- [ ] Verificar filtros por rol (agente solo ve sus datos)

---

### TAREA 5: Implementar Sistema de Notificaciones 🔴

**Problema**: No hay notificaciones por email ni dentro del sistema.

**¿Qué hacer?**

**OPCIÓN A - Notificaciones por Email:**

1. **Configurar SMTP:**
   - Decidir qué servicio de email usar (Gmail, Outlook, etc.)
   - Obtener credenciales SMTP
   - Configurar en `back/giga/settings.py`:
     - `EMAIL_BACKEND`
     - `EMAIL_HOST`
     - `EMAIL_PORT`
     - `EMAIL_HOST_USER`
     - `EMAIL_HOST_PASSWORD`

2. **Crear templates de emails:**
   - Crear carpeta `back/templates/emails/`
   - Crear un template HTML para cada tipo de notificación:
     - `guardia_asignada.html`
     - `licencia_aprobada.html`
     - `licencia_rechazada.html`
     - `cronograma_publicado.html`
     - `compensacion_aprobada.html`

3. **Crear función de envío:**
   - Crear archivo `back/notificaciones/utils.py`
   - Crear función `enviar_email(destinatario, asunto, template, contexto)`
   - Usar `send_mail()` de Django

4. **Integrar en los endpoints:**
   - En cada endpoint que genere un evento (aprobar licencia, publicar cronograma, etc.)
   - Llamar a la función de envío de email
   - Pasar los datos necesarios para el template

**OPCIÓN B - Notificaciones In-App (más simple para empezar):**

1. **Crear modelo de notificación:**
   - Crear archivo `back/notificaciones/models.py`
   - Crear modelo `Notificacion` con campos:
     - `id_agente`: A quién va dirigida
     - `titulo`: Título corto
     - `mensaje`: Contenido
     - `tipo`: Tipo de notificación
     - `leida`: Boolean
     - `fecha_creacion`: Timestamp

2. **Crear endpoints:**
   - `GET /notificaciones/` - Listar notificaciones del usuario
   - `PATCH /notificaciones/{id}/marcar_leida/` - Marcar como leída
   - `GET /notificaciones/no_leidas/count/` - Contador para badge

3. **Integrar en eventos:**
   - En cada endpoint de aprobación/rechazo/publicación
   - Crear una notificación para el agente afectado

4. **Mostrar en frontend:**
   - Agregar icono de campanita en el navbar
   - Mostrar badge con cantidad de no leídas
   - Crear componente para listar notificaciones

**Qué tener en cuenta:**
- ⚠️ Para emails necesitas configurar un servidor SMTP (puede ser complicado en desarrollo)
- ⚠️ Las notificaciones in-app son más fáciles de implementar y probar
- ⚠️ Puedes empezar con in-app y luego agregar emails
- ⚠️ Cada notificación debe tener información útil (qué pasó, cuándo, quién lo hizo)

**Estimación**: 8-12 horas (in-app) | 15-20 horas (con emails)

**Verificación**:
**Si hiciste in-app:**
- [ ] Aprobar una licencia y verificar que se crea una notificación
- [ ] Ver las notificaciones en el endpoint
- [ ] Marcar como leída y verificar que cambia el contador
- [ ] Verificar en frontend que aparece el badge

**Si hiciste emails:**
- [ ] Aprobar una licencia y verificar que llega un email
- [ ] Verificar que el email tiene el formato correcto
- [ ] Probar con diferentes tipos de notificaciones
- [ ] Verificar que NO se envían emails a agentes inactivos

---

## 🟡 PRIORIDAD ALTA

Estas tareas son importantes para el correcto funcionamiento del sistema.

---

### TAREA 6: Implementar Filtros por Rol en Guardias 🟡

**Problema**: Todos los usuarios ven todas las guardias de todos los agentes.

**¿Qué hacer?**

1. **Ir a `back/guardias/views.py`**

2. **Buscar la clase `GuardiaViewSet`**

3. **Agregar método `get_queryset()`:**
   - Este método se ejecuta automáticamente cuando se listan las guardias
   - Obtener el rol del usuario autenticado
   - Filtrar según el rol (similar a asistencias)

**Qué tener en cuenta:**
- ⚠️ Agente solo ve sus guardias
- ⚠️ Jefatura ve guardias de su área
- ⚠️ Director ve guardias de su división
- ⚠️ Los filtros por fecha deben seguir funcionando

**Estimación**: 3-4 horas

**Verificación**:
- [ ] Login como agente y verificar que solo ve sus guardias
- [ ] Login como jefatura y verificar que ve su área
- [ ] Verificar que los filtros adicionales funcionan

---

### TAREA 7: Implementar Filtros por Rol en Licencias 🟡

**Problema**: Todos los usuarios ven todas las licencias.

**¿Qué hacer?**

1. **Ir a `back/asistencia/views.py` (módulo de licencias)**

2. **Buscar la función de listar licencias**

3. **Agregar filtrado por rol** (igual que en asistencias y guardias)

4. **Validar aprobaciones:**
   - Cuando alguien intenta aprobar una licencia
   - Verificar que tiene jerarquía sobre el solicitante
   - Jefatura solo aprueba licencias de agentes de su área
   - Director aprueba licencias de jefaturas

**Qué tener en cuenta:**
- ⚠️ La aprobación jerárquica es crítica
- ⚠️ Un jefe no puede aprobar la licencia de otro jefe
- ⚠️ Debes validar tanto al listar como al aprobar

**Estimación**: 4-5 horas

**Verificación**:
- [ ] Agente solo ve sus licencias
- [ ] Jefatura ve licencias de su área
- [ ] Jefatura puede aprobar licencias de agentes de su área
- [ ] Jefatura NO puede aprobar licencias de otros jefes
- [ ] Director puede aprobar licencias de jefaturas

---

### TAREA 8: Implementar Filtros por Rol en Compensaciones 🟡

**Problema**: Todos ven todas las compensaciones.

**¿Qué hacer?**

1. **Ir a `back/guardias/views.py`**

2. **Buscar `HoraCompensacionViewSet`**

3. **Agregar `get_queryset()` con filtrado por rol**

4. **Validar aprobaciones** (similar a licencias)

**Estimación**: 3-4 horas

**Verificación**: Similar a licencias

---

### TAREA 9: Validar Áreas en Creación de Cronogramas 🟡

**Problema**: Una jefatura puede crear cronogramas para áreas que no gestiona.

**¿Qué hacer?**

1. **Ir a `back/guardias/views.py`**

2. **Buscar función `crear_con_guardias()`**

3. **Agregar validación:**
   - Obtener el área del cronograma que se quiere crear
   - Obtener el área del usuario que lo crea
   - Si es jefatura: verificar que sea SU área
   - Si es director: verificar que esté bajo su dirección

**Qué tener en cuenta:**
- ⚠️ Administrador no tiene restricciones
- ⚠️ El mensaje de error debe ser claro
- ⚠️ Esto previene que se creen cronogramas indebidos

**Estimación**: 2-3 horas

**Verificación**:
- [ ] Login como jefatura
- [ ] Intentar crear cronograma para otra área → debe dar error
- [ ] Crear cronograma para su área → debe funcionar

---

## 🟢 PRIORIDAD MEDIA

Estas tareas mejoran la seguridad y funcionalidad pero no son bloqueantes.

---

### TAREA 10: Implementar Filtros en Auditoría 🟢

**Problema**: Todos los usuarios ven todos los logs de auditoría.

**¿Qué hacer?**

1. **Ir a `back/auditoria/views.py`**

2. **Agregar filtrado por rol:**
   - Agente solo ve sus propias acciones
   - Jefatura ve auditoría de su área
   - Director ve auditoría de su división
   - Administra dor ve todo

**Qué tener en cuenta:**
- ⚠️ La auditoría es sensible, solo mostrar lo permitido
- ⚠️ Relacionar los logs con las áreas correspondientes

**Estimación**: 4-5 horas

---

### TAREA 11: Agregar Paginación en Listados 🟢

**Problema**: Si hay muchos registros, las consultas pueden ser lentas.

**¿Qué hacer?**

1. **Ir a `back/giga/settings.py`**

2. **Configurar paginación global:**
   ```
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 50
   }
   ```

3. **Probar que funciona en los listados**

**Qué tener en cuenta:**
- ⚠️ La paginación es automática una vez configurada
- ⚠️ El frontend debe manejar la paginación

**Estimación**: 2-3 horas

**Verificación**:
- [ ] Consultar un listado con muchos registros
- [ ] Verificar que retorna solo 50 registros
- [ ] Usar `?page=2` para ver la siguiente página

---

### TAREA 12: Implementar Rate Limiting 🟢

**Problema**: Un usuario podría hacer muchas peticiones y sobrecargar el servidor.

**¿Qué hacer?**

1. **Instalar librería:**
   - Agregar `django-ratelimit` a `requirements.txt`
   - Instalar: `pip install django-ratelimit`

2. **Aplicar a endpoints críticos:**
   - Login: máximo 5 intentos por minuto
   - Marcar asistencia: máximo 10 por día
   - Crear cronogramas: máximo 20 por hora

3. **Usar decorador `@ratelimit`**

**Qué tener en cuenta:**
- ⚠️ No bloquees el uso normal, solo abuso
- ⚠️ Login es especialmente importante (previene ataques de fuerza bruta)

**Estimación**: 3-4 horas

---

## 🔵 PRIORIDAD BAJA

Tareas deseables pero no esenciales.

---

### TAREA 13: Crear Tests Automatizados 🔵

**Problema**: No hay tests, si algo se rompe no lo detectarás hasta que un usuario lo reporte.

**¿Qué hacer?**

1. **Crear tests unitarios para modelos:**
   - Crear `back/guardias/tests.py`
   - Probar que se crea una guardia correctamente
   - Probar que no se puede crear guardia en día hábil
   - Probar cálculo de horas

2. **Crear tests de endpoints:**
   - Probar login
   - Probar que sin autenticación da error 401
   - Probar que los filtros por rol funcionan

3. **Ejecutar tests:**
   - `python manage.py test`

**Qué tener en cuenta:**
- ⚠️ Empieza con lo crítico (autenticación, filtros por rol)
- ⚠️ Los tests toman tiempo pero previenen errores futuros

**Estimación**: 8-12 horas

---

### TAREA 14: Documentar API con Swagger 🔵

**Problema**: No hay documentación automática de la API.

**¿Qué hacer?**

1. **Instalar librería:**
   - Agregar `drf-yasg` a `requirements.txt`
   - Instalar: `pip install drf-yasg`

2. **Configurar en `urls.py`:**
   - Agregar ruta para Swagger UI
   - Configurar metadata de la API

3. **Agregar docstrings:**
   - En cada endpoint explicar qué hace
   - Documentar parámetros esperados

**Qué tener en cuenta:**
- ⚠️ La documentación se genera automáticamente de los docstrings
- ⚠️ Facilita que otros desarrolladores entiendan tu API

**Estimación**: 4-6 horas

---

## 📝 Checklist General

Antes de considerar el proyecto "terminado":

### Seguridad
- [ ] Todos los endpoints tienen autenticación (excepto login)
- [ ] Los filtros por rol están implementados en todos los módulos
- [ ] Solo administradores pueden crear/editar/eliminar agentes
- [ ] Las aprobaciones validan jerarquía correctamente
- [ ] Rate limiting está configurado

### Funcionalidad
- [ ] Las notificaciones están funcionando
- [ ] Los reportes generan datos reales (no hardcodeados)
- [ ] Los reportes respetan los permisos por rol
- [ ] La paginación está configurada
- [ ] Los filtros de fecha funcionan

### Calidad
- [ ] Hay tests para las funciones críticas
- [ ] La documentación de API está generada
- [ ] El código tiene comentarios en partes complejas
- [ ] No hay warnings en la consola

### Deployment
- [ ] Las variables de entorno están configuradas
- [ ] El archivo `.env` está en `.gitignore`
- [ ] Las credenciales de producción son diferentes a desarrollo
- [ ] Está configurado el backup de base de datos

---

## 💡 Consejos Generales

### Cómo Empezar

1. **No hagas todo de golpe**: Empieza por las tareas críticas una por una
2. **Prueba cada cambio**: Después de cada tarea, verifica que funciona
3. **Usa Git**: Haz commit después de cada tarea completada
4. **Documenta**: Agrega comentarios explicando las validaciones que agregaste

### Orden Recomendado

```
DÍA 1-2: TAREA 1 (Autenticación)
DÍA 2-3: TAREA 2 (Validación Admin)
DÍA 3-4: TAREA 3 (Filtros Asistencia)
DÍA 4-5: TAREA 6 (Filtros Guardias)
DÍA 5-6: TAREA 7 (Filtros Licencias)
DÍA 6-7: TAREA 4 (Reportes)
DÍA 7-10: TAREA 5 (Notificaciones)
...continuar con el resto
```

### Cuando Tengas Problemas

- **Lee los errores**: Django da mensajes claros, léelos con atención
- **Usa `print()`**: Para entender qué está pasando en el código
- **Revisa los logs**: Mira la terminal del backend para ver errores
- **Prueba en el navegador**: Usa las herramientas de desarrollo (F12)
- **Consulta la documentación**: Django y DRF tienen muy buena documentación

---

## 🎯 Objetivo Final

Al completar estas tareas tendrás:

✅ Un sistema SEGURO con autenticación y permisos correctos  
✅ Notificaciones funcionando  
✅ Reportes con datos reales  
✅ Filtros por rol en TODOS los módulos  
✅ Sistema listo para PRODUCCIÓN  

**¡Éxito!** 🚀
