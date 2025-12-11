#!/usr/bin/env python
"""
Tareas de mantenimiento para el sistema GIGA.
Incluye limpieza de sesiones y archivado de datos antiguos.
"""
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from personas.models import SesionActiva
from django.contrib.sessions.models import Session
from django.db import transaction, connection
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


def cleanup_sessions(days=7, dry_run=False):
    """
    Borra SesionActiva y entradas django_session asociadas:
      - elimina filas con activa=False
      - elimina filas con ultimo_acceso < now - days
    Retorna dict con conteos.
    """
    cutoff = timezone.now() - timedelta(days=days)
    qs = SesionActiva.objects.filter(Q(activa=False) | Q(ultimo_acceso__lt=cutoff))
    session_keys = list(qs.values_list('session_key', flat=True))
    total = len(session_keys)

    result = {
        'candidatas': total,
        'sesion_activa_deleted': 0,
        'django_session_deleted': 0
    }

    logger.info(f'cleanup_sessions: {total} sesiones candidatas (days={days}, dry_run={dry_run})')

    if total == 0 or dry_run:
        return result

    with transaction.atomic():
        # Eliminar en django_session
        ss_deleted, _ = Session.objects.filter(session_key__in=session_keys).delete()
        # Eliminar en sesion_activa
        sa_deleted, _ = qs.delete()

    result['sesion_activa_deleted'] = sa_deleted
    result['django_session_deleted'] = ss_deleted

    logger.info(f'cleanup_sessions: borradas {sa_deleted} sesion_activa, {ss_deleted} django_session')
    return result


def archive_old_audits(months=6, dry_run=False):
    """
    Archiva registros de auditoría más antiguos de N meses.
    Mueve los registros a la tabla auditoria_archivo.
    Retorna dict con conteos.
    """
    result = {
        'candidatas': 0,
        'archivadas': 0,
        'eliminadas': 0,
        'error': None
    }
    
    try:
        # Calcular fecha de corte usando relativedelta
        cutoff_date = timezone.now() - relativedelta(months=months)
        
        with connection.cursor() as cursor:
            # Verificar si la tabla de archivo existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'auditoria_archivo'
                )
            """)
            if not cursor.fetchone()[0]:
                result['error'] = 'Tabla auditoria_archivo no existe'
                logger.warning(f'archive_old_audits: {result["error"]}')
                return result
            
            # Contar candidatas usando fecha calculada
            cursor.execute(
                "SELECT COUNT(*) FROM auditoria WHERE creado_en < %s",
                [cutoff_date]
            )
            result['candidatas'] = cursor.fetchone()[0]
            
            logger.info(f'archive_old_audits: {result["candidatas"]} registros candidatos (months={months}, dry_run={dry_run})')
            
            if result['candidatas'] == 0 or dry_run:
                return result
            
            # Ejecutar función de archivo (la función usa INTEGER para meses)
            cursor.execute("SELECT * FROM archivar_auditorias(%s)", [months])
            row = cursor.fetchone()
            if row:
                result['archivadas'] = row[0]
                result['eliminadas'] = row[1]
                
            logger.info(f'archive_old_audits: archivadas={result["archivadas"]}, eliminadas={result["eliminadas"]}')
            
    except Exception as e:
        result['error'] = str(e)
        logger.exception(f'Error en archive_old_audits: {e}')
    
    return result


def archive_old_incidencias(months=12, dry_run=False):
    """
    Archiva incidencias cerradas/resueltas más antiguas de N meses.
    Mueve los registros a la tabla incidencia_archivo.
    Retorna dict con conteos.
    """
    result = {
        'candidatas': 0,
        'archivadas': 0,
        'eliminadas': 0,
        'error': None
    }
    
    try:
        # Calcular fecha de corte usando relativedelta
        cutoff_date = timezone.now() - relativedelta(months=months)
        
        with connection.cursor() as cursor:
            # Verificar si la tabla de archivo existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'incidencia_archivo'
                )
            """)
            if not cursor.fetchone()[0]:
                result['error'] = 'Tabla incidencia_archivo no existe'
                logger.warning(f'archive_old_incidencias: {result["error"]}')
                return result
            
            # Contar candidatas usando fecha calculada
            cursor.execute("""
                SELECT COUNT(*) FROM incidencia 
                WHERE estado IN ('cerrada', 'resuelta')
                  AND fecha_resolucion < %s
            """, [cutoff_date])
            result['candidatas'] = cursor.fetchone()[0]
            
            logger.info(f'archive_old_incidencias: {result["candidatas"]} incidencias candidatas (months={months}, dry_run={dry_run})')
            
            if result['candidatas'] == 0 or dry_run:
                return result
            
            # Ejecutar función de archivo (la función usa INTEGER para meses)
            cursor.execute("SELECT * FROM archivar_incidencias(%s)", [months])
            row = cursor.fetchone()
            if row:
                result['archivadas'] = row[0]
                result['eliminadas'] = row[1]
                
            logger.info(f'archive_old_incidencias: archivadas={result["archivadas"]}, eliminadas={result["eliminadas"]}')
            
    except Exception as e:
        result['error'] = str(e)
        logger.exception(f'Error en archive_old_incidencias: {e}')
    
    return result
