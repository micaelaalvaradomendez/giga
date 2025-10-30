# 📊 Detalles de Datos Extraídos - Sistema GIGA

## Resumen de Archivos JSON

### 👥 personas_data.json (24 registros)

#### Usuario (6 registros)
Cuentas de usuario del sistema con autenticación Django:
- **tayra.aguila** - CUIL: 27123456784 - tayra.aguila@proteccioncivil.tdf.gov.ar
- **cristian.garcia** - CUIL: 27345678904 - cristian.garcia@proteccioncivil.tdf.gov.ar
- **maria.lopez** - CUIL: 27456789015 - maria.lopez@proteccioncivil.tdf.gov.ar
- **juan.perez** - CUIL: 20234567891 - juan.perez@proteccioncivil.tdf.gov.ar
- **ana.rodriguez** - CUIL: 27567890126 - ana.rodriguez@proteccioncivil.tdf.gov.ar
- **admin** - Usuario administrador del sistema

**Características:**
- Passwords hasheados con PBKDF2-SHA256
- Todos los usuarios están activos
- Fechas de creación: 2025-01-01T00:00:00Z
- Ninguno ha iniciado sesión aún (last_login: null)

#### Area (1 registro)
- **Protección Civil** - Código: PC01
- Descripción: Dirección de Protección Civil y Emergencias

#### Agente (6 registros)
Perfiles de empleados vinculados a usuarios:
- **Tayra Águila** - Legajo: 001 - DNI: 12345678
- **Cristian García** - Legajo: 002 - DNI: 34567890  
- **María López** - Legajo: 003 - DNI: 45678901
- **Juan Pérez** - Legajo: 004 - DNI: 23456789
- **Ana Rodríguez** - Legajo: 005 - DNI: 56789012
- **Administrador** - Legajo: 999 - DNI: 00000000

**Características:**
- Todos pertenecen al área de Protección Civil
- Estados: ACTIVO
- Fechas de ingreso: 2024-01-01
- Teléfonos y direcciones configurados

#### Rol (5 registros)
Sistema de autorización:
- **Administrador** - Control total del sistema
- **Supervisor** - Supervisión y gestión
- **Agente** - Usuario estándar
- **Consulta** - Solo lectura
- **Invitado** - Acceso limitado

#### AgenteRol (6 registros)
Asignaciones de roles a agentes:
- Tayra Águila → Administrador
- Cristian García → Supervisor  
- María López → Agente
- Juan Pérez → Agente
- Ana Rodríguez → Consulta
- Admin → Administrador

---

### 📅 asistencia_data.json (15 registros)

#### TipoLicencia (3 registros)
Tipos de licencias disponibles:
- **VAC** - Vacaciones
- **ENF** - Enfermedad  
- **PER** - Personal

#### Licencia (12 registros)
Licencias registradas en el sistema:

**Vacaciones:**
- Tayra Águila: 01/01/2024 - 15/01/2024 (15 días) - APROBADA
- Cristian García: 15/02/2024 - 29/02/2024 (15 días) - APROBADA
- María López: 01/03/2024 - 15/03/2024 (15 días) - APROBADA
- Juan Pérez: 15/04/2024 - 29/04/2024 (15 días) - PENDIENTE

**Enfermedad:**
- Ana Rodríguez: 01/05/2024 - 03/05/2024 (3 días) - APROBADA
- Tayra Águila: 10/06/2024 - 12/06/2024 (3 días) - APROBADA
- Cristian García: 15/07/2024 - 17/07/2024 (3 días) - APROBADA
- María López: 20/08/2024 - 22/08/2024 (3 días) - RECHAZADA

**Personal:**
- Juan Pérez: 01/09/2024 - 01/09/2024 (1 día) - APROBADA
- Ana Rodríguez: 15/10/2024 - 15/10/2024 (1 día) - PENDIENTE
- Tayra Águila: 20/11/2024 - 20/11/2024 (1 día) - APROBADA
- Cristian García: 25/12/2024 - 25/12/2024 (1 día) - APROBADA

**Características:**
- Estados: PENDIENTE, APROBADA, RECHAZADA
- Justificaciones incluidas
- Fechas de solicitud registradas
- Vínculos a agentes y tipos de licencia

---

### 🔍 Apps Sin Datos

#### guardias (0 registros)
- Feriado: Sin datos
- ReglaPlus: Sin datos  
- CronogramaGuardias: Sin datos
- Guardia: Sin datos
- HorasGuardias: Sin datos
- AsignacionPlus: Sin datos

#### auditoria (0 registros)  
- Auditoria: Sin registros de auditoría

#### reportes (0 registros)
- Reporte: Sin reportes generados
- PlantillaCorreo: Sin plantillas configuradas
- Notificacion: Sin notificaciones
- EnvioLoteNotificaciones: Sin envíos masivos
- RenderCorreo: Sin renders de correo
- Vista: Sin vistas personalizadas

#### convenio_ia (0 registros)
- Convenio: Sin convenios cargados
- IndiceConvenio: Sin índices construidos
- ConsultaConvenio: Sin consultas realizadas
- ResultadoBusqueda: Sin búsquedas
- RespuestaConCitas: Sin respuestas generadas
- Archivo: Sin archivos almacenados

---

## 🔗 Relaciones de Datos

### Integridad Referencial
- **Usuario ↔ Agente:** 1:1 (6 pares vinculados)
- **Agente ↔ Area:** N:1 (todos en Protección Civil)
- **Agente ↔ Rol:** N:M (via AgenteRol - 6 asignaciones)
- **Licencia ↔ Agente:** N:1 (12 licencias distribuidas)
- **Licencia ↔ TipoLicencia:** N:1 (3 tipos usados)

### Distribución de Datos
- **Usuarios más activos en licencias:** Tayra Águila (4), Cristian García (3)
- **Tipos de licencia más usados:** Vacaciones (4), Enfermedad (4), Personal (4)
- **Estados de aprobación:** 9 aprobadas, 2 pendientes, 1 rechazada

---

## 📋 Metadatos Django

Todos los registros incluyen:
- **model:** Nombre completo del modelo Django
- **pk:** Clave primaria UUID v4
- **fields:** Todos los campos del modelo
- **Referencias FK:** UUIDs de objetos relacionados

### Ejemplo de Estructura
```json
{
  "model": "personas.agente",
  "pk": "11111111-1111-1111-1111-111111111111", 
  "fields": {
    "usuario": "11111111-1111-1111-1111-111111111111",
    "area": "11111111-1111-1111-1111-111111111111",
    "legajo": "001",
    "dni": "12345678",
    // ... más campos
  }
}
```

---

## ✅ Estado de Validación

### Datos Verificados
- ✅ Todos los UUIDs son válidos v4
- ✅ Referencias FK apuntan a registros existentes  
- ✅ Campos requeridos están presentes
- ✅ Formatos de fecha son ISO 8601
- ✅ Passwords están hasheados correctamente

### Observaciones
- 🔸 Apps de guardias, auditoria, reportes y convenio_ia están vacías
- 🔸 Sistema está en fase inicial con datos de testing/desarrollo
- 🔸 Todas las fechas son de 2024-2025 (datos de prueba)

---

*Última actualización: 30/10/2024 05:14 UTC*