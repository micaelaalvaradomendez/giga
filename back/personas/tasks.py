#!/usr/bin/env python
from django.utils import timezone
from datetime import timedelta
from personas.models import SesionActiva
from django.contrib.sessions.models import Session
from django.db import transaction
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
    total = qs.count()
    session_keys = list(qs.values_list('session_key', flat=True))

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
