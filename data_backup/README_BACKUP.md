# README - Backup Completo de Base de Datos GIGA

## 📋 Información General

Este directorio contiene el backup completo de la base de datos PostgreSQL del sistema GIGA, extraído el **30 de octubre de 2024** antes de implementar la nueva arquitectura de base de datos.

### 📊 Resumen de Extracción
- **Fecha de extracción:** 2025-10-30 05:14:53 UTC
- **Total de registros:** 39 registros
- **Apps procesadas:** 6 aplicaciones Django
- **Formato:** JSON con metadatos Django

---

## 🗂️ Estructura de Archivos

### 📐 Documentación de Modelos
| Archivo | Descripción | Estado |
|---------|-------------|--------|
| `database_structure.puml` | Diagrama PlantUML completo de la BD | ✅ Completo |
| `personas_models.md` | Documentación de modelos de usuarios y roles | ✅ Completo |
| `asistencia_models.md` | Documentación de sistema de asistencias | ✅ Completo |
| `guardias_models.md` | Documentación de sistema de guardias | ✅ Completo |
| `auditoria_models.md` | Documentación de sistema de auditoría | ✅ Completo |
| `reportes_models.md` | Documentación de reportes y notificaciones | ✅ Completo |
| `convenio_ia_models.md` | Documentación de IA para convenios | ✅ Completo |

### 💾 Datos Extraídos (JSON)
| Archivo | App | Registros | Descripción |
|---------|-----|-----------|-------------|
| `personas_data.json` | personas | 24 | Usuarios, agentes, áreas, roles |
| `asistencia_data.json` | asistencia | 15 | Tipos de licencias y licencias |
| `extraccion_resumen.json` | - | - | Resumen de la extracción |

### 📋 Datos Iniciales/Semilla
| Archivo | Descripción | Propósito |
|---------|-------------|-----------|
| `initial_data.json` | Datos básicos del sistema | Inicialización |
| `usuarios_agentes.json` | Usuarios y agentes básicos | Setup inicial |
| `area_basica.json` | Área organizacional básica | Estructura |
| `roles_basicos.json` | Roles del sistema | Permisos |
| `asignacion_roles.json` | Asignaciones rol-usuario | Autorización |
| `tipos_licencia.json` | Tipos de licencias disponibles | Configuración |
| `licencias_basicas.json` | Licencias de ejemplo | Testing |

### 🛠️ Herramientas
| Archivo | Descripción |
|---------|-------------|
| `extract_data.py` | Script de extracción de datos |
| `README.md` | Esta documentación |

---

## 📈 Detalles de Datos Extraídos

### App: Personas (24 registros)
- **Usuario:** 6 registros - Cuentas de usuario del sistema
- **Area:** 1 registro - Estructura organizacional
- **Agente:** 6 registros - Perfiles de agentes/empleados
- **Rol:** 5 registros - Roles de autorización
- **AgenteRol:** 6 registros - Asignaciones de roles

### App: Asistencia (15 registros)
- **TipoLicencia:** 3 registros - Tipos de licencias disponibles
- **Licencia:** 12 registros - Licencias registradas en el sistema

### Apps Sin Datos
Las siguientes apps no contienen datos:
- **Guardias:** Sistema de guardias (no inicializado)
- **Auditoria:** Sistema de auditoría (sin registros)
- **Reportes:** Sistema de reportes (sin datos)
- **Convenio IA:** Sistema de IA (no configurado)

---

## 🔧 Uso de los Archivos

### Para Restaurar Datos
```bash
# 1. Cargar datos de personas
python manage.py loaddata personas_data.json

# 2. Cargar datos de asistencia  
python manage.py loaddata asistencia_data.json

# 3. Verificar integridad
python manage.py check --database=default
```

### Para Migración
1. **Usar documentación de modelos** para recrear estructura
2. **Importar JSON** para preservar datos existentes
3. **Validar relaciones** entre modelos según PlantUML

### Para Desarrollo
- **Datos iniciales:** Usar archivos `*_basicos.json` para desarrollo
- **Testing:** Datos reales disponibles para pruebas
- **Documentación:** Referencia completa de modelos

---

## 🔍 Verificación de Integridad

### Checksums de Archivos Críticos
```bash
# Verificar integridad de datos principales
md5sum personas_data.json
md5sum asistencia_data.json
md5sum database_structure.puml
```

### Validación de Datos
- Todos los registros incluyen metadatos Django completos
- Relaciones entre modelos preservadas en JSON
- Campos calculados y propiedades documentados en MD

---

## 🚀 Nueva Implementación

### Arquitectura Objetivo
- **Base de datos:** PostgreSQL aislada en contenedor independiente
- **Configuración:** Simplificada a single-database
- **Networking:** Red Docker dedicada `giga_network`
- **Persistencia:** Volúmenes Docker para datos y logs

### Migración Planificada
1. **Fase 1:** Implementar nueva BD aislada ✅ 
2. **Fase 2:** Migrar estructura según documentación ✅
3. **Fase 3:** Restaurar datos desde JSON 🔄 *En proceso*
4. **Fase 4:** Validar funcionalidad completa ⏳
5. **Fase 5:** Cutover y cleanup ⏳

---

## 📞 Información Técnica

### Versiones de Sistema
- **Django:** 4.2.x
- **PostgreSQL:** 16-alpine
- **Python:** 3.11+
- **Docker:** Compose v2

### Configuración de BD Original
- **Host:** localhost (embebido en backend)
- **Puerto:** 5432
- **Base:** giga
- **Usuario:** giga_user

### Configuración de BD Nueva
- **Host:** giga_database (contenedor aislado)
- **Puerto:** 5432 (interno), 5433 (externo)
- **Base:** giga
- **Usuario:** giga_user
- **Network:** giga_network

---

## ⚠️ Notas Importantes

### Precauciones
- **NEVER delete** estos archivos hasta confirmar migración exitosa
- **Verificar integridad** antes de usar en producción  
- **Backup adicional** recomendado antes de restore

### Dependencias
- Los datos de `personas` deben cargarse ANTES que otros módulos
- Relaciones FK requieren orden específico de carga
- Algunos campos pueden requerir migración manual

### Limitaciones
- Apps de guardias, auditoría y reportes están vacías
- Sistema de IA no tiene datos de configuración
- Algunos fixtures pueden estar obsoletos

---

## 📅 Cronología

- **2024-10-24:** Implementación inicial del sistema
- **2024-10-29:** Configuración de base de datos aislada
- **2024-10-30:** **Extracción completa de backup pre-migración**
- **2024-10-30:** Documentación y estructura PlantUML
- **Próximo:** Migración a nueva arquitectura

---

**⚡ Estado:** BACKUP COMPLETO - LISTO PARA MIGRACIÓN

*Generado automáticamente por el sistema GIGA el 30/10/2024*