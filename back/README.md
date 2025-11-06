## Arquitectura Implementada

### Apps Django

1. **`personas/`** - Gestión de agentes y áreas
   - `Area` - Áreas de trabajo en Protección Civil
   - `Rol` - Roles/cargos de los agentes  
   - `Agente` - Agentes de Protección Civil (modelo simple, no hereda de User)
   - `AgenteRol` - Relación N:N entre agentes y roles

2. **`auditoria/`** - Logging de cambios
   - `Auditoria` - Registro de cambios en el sistema

3. **`guardias/`** - Gestión de guardias
   - `Cronograma` - Programación de guardias
   - `Guardia` - Guardias asignadas
   - `ResumenGuardiaMes` - Resúmenes mensuales

4. **`asistencia/`** - Control de asistencias
   - `TipoLicencia` - Tipos de licencias
   - `ParteDiario` - Partes diarios de trabajo
   - `Licencia` - Licencias solicitadas
   - `Asistencia` - Registro de asistencias