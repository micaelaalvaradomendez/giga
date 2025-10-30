# 💾 Backup de Base de Datos - GIGA

## ✅ **Backup Completo del Sistema**

Este directorio contiene el **backup completo** de la base de datos PostgreSQL extraído el **30 de octubre de 2024** antes de migrar a la nueva arquitectura.

### 📊 **Datos Incluidos:**
- **39 registros** extraídos exitosamente
- **6 usuarios** con roles y permisos
- **3 tipos de licencias** + 12 licencias de ejemplo
- **1 área organizacional** (Protección Civil)

### 📁 **Archivos Principales:**
- `personas_data.json` - 24 registros (usuarios, agentes, roles)
- `asistencia_data.json` - 15 registros (licencias)
- `database_structure.puml` - Diagrama completo de la BD
- `*_models.md` - Documentación de cada app Django

## 🚀 **Uso con Nueva Arquitectura**

Los datos se cargan **automáticamente** al ejecutar:
```bash
cd giga && ./start.sh
```

O manualmente:
```bash
docker exec giga_backend_dev python manage.py loaddata /app/data_backup/personas_data.json
docker exec giga_backend_dev python manage.py loaddata /app/data_backup/asistencia_data.json
```

## 📚 **Documentación**

Ver `README_BACKUP.md` para documentación completa del backup.