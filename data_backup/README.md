# Datos de la Base de Datos

Este directorio contiene los backups de la base de datos del proyecto GIGA.

## Archivos

- `initial_data.json`: Datos iniciales del sistema (usuarios, roles, licencias básicas)

## Uso

### Para crear un backup de los datos actuales:
```bash
docker exec giga_back python manage.py export_data
```

### Para restaurar datos desde backup:
```bash
docker exec giga_back python manage.py import_data --latest
```

## Flujo de Trabajo

1. **Al hacer cambios en la BD**: Después de modificar datos importantes, crear un backup:
   ```bash
   docker exec giga_back python manage.py export_data
   git add data_backup/
   git commit -m "feat: actualizar datos de la base de datos"
   git push
   ```

2. **Al hacer pull**: Los nuevos datos se cargarán automáticamente en el próximo `docker compose up`

## Importante

- Los datos se cargan automáticamente al hacer `docker compose up`
- Los fixtures están versionados en Git
- Los cambios en la BD se pueden compartir entre desarrolladores
- El volumen de PostgreSQL mantiene persistencia local