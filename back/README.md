# Estructura del Proyecto Django - Sistema de Control Horario y Guardias

## Resumen de la estructura creada

Este proyecto Django ha sido creado basándose en el diagrama PlantUML proporcionado. La estructura incluye:

### Apps creadas:

#### 1. **personas** - Gestión de Personal
- **Modelos**: 
  - `Area`: Áreas de la organización
  - `Agente`: Empleados/agentes
  - `Rol`: Roles del sistema
  - `CuentaAcceso`: Cuentas de acceso al sistema
- **Funcionalidades**: Gestión de personal, áreas y roles

#### 2. **asistencia** - Control de Asistencia
- **Modelos**:
  - `Asistencia`: Registro diario de asistencia
  - `Marca`: Marcas de entrada/salida
  - `LicenciaONovedad`: Clase abstracta base
  - `Licencia`: Licencias de los agentes
  - `Novedad`: Novedades y permisos
  - `Adjunto`: Archivos adjuntos
- **Enums**: EstadoAsistencia, TipoMarca, TipoLicencia, etc.

#### 3. **guardias** - Sistema de Guardias
- **Modelos**:
  - `CronogramaGuardias`: Cronogramas mensuales
  - `Guardia`: Guardias individuales
  - `HorasGuardias`: Resumen de horas por período
  - `Feriado`: Días feriados
  - `ReglaPlus`: Reglas para asignación de plus
  - `AsignacionPlus`: Asignaciones calculadas
- **Enums**: EstadoCronograma, TipoGuardia, AplicaA

#### 4. **auditoria** - Auditoría y Parámetros
- **Modelos**:
  - `ParametrosControlHorario`: Configuración del sistema
  - `RegistroAuditoria`: Registro de todas las acciones
- **Enums**: PoliticaVentanas, AccionAuditoria

#### 5. **reportes** - Reportes y Notificaciones
- **Modelos**:
  - `Reporte`: Generación de reportes
  - `Notificacion`: Sistema de notificaciones
  - `PlantillaCorreo`: Plantillas para emails
  - `EnvioLoteNotificaciones`: Envíos masivos
- **Clases auxiliares**: RenderCorreo, Vista

#### 6. **convenio_ia** - IA para Convenios
- **Modelos**:
  - `Convenio`: Convenios colectivos
  - `IndiceConvenio`: Índices de búsqueda
  - `ConsultaConvenio`: Consultas realizadas
- **Clases auxiliares**: ResultadoBusqueda, RespuestaConCitas, Archivo

### Configuración realizada:

1. **Settings.py**:
   - Apps registradas
   - Django REST Framework configurado
   - Configuración de archivos multimedia
   - Logging básico
   - Configuración regional (español argentino)

2. **URLs**:
   - URLs principales configuradas
   - URLs de cada app creadas (estructura básica)
   - Servicio de archivos multimedia

3. **Estructura API REST**:
   - Views básicas usando Django REST Framework
   - Serializers para la app personas (como ejemplo)
   - Autenticación por token y sesión

### Para continuar el desarrollo:

1. **Instalar migraciones**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Crear superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Completar serializers** para las demás apps

4. **Implementar las views** con la lógica de negocio

5. **Completar los métodos** en los modelos (actualmente tienen `pass`)

6. **Configurar el admin** de Django para gestión

### Próximos pasos recomendados:

- Implementar autenticación personalizada
- Crear tests unitarios
- Implementar validaciones de negocio
- Configurar permisos granulares
- Integrar sistema de IA para consultas de convenio
- Implementar notificaciones por email

El proyecto está listo para comenzar el desarrollo con una estructura sólida basada en el diagrama UML proporcionado.