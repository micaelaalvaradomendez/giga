#!/usr/bin/env python
"""
API para historial de sesiones activas.
Reemplaza la consulta de auditoría para login history en el panel admin.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from personas.models import SesionActiva
from django.core.paginator import Paginator

# RBAC Permissions
from common.permissions import IsAuthenticatedGIGA


@api_view(['GET'])
@permission_classes([IsAuthenticatedGIGA])
def login_history(request):
    """
    Endpoint para que el panel admin muestre inicios de sesión usando sesion_activa.
    Query params: page, page_size, agente_id (opcional)
    """
    agente_id = request.GET.get('agente_id')
    
    # Validate pagination parameters with defaults
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    
    try:
        page_size = min(100, max(1, int(request.GET.get('page_size', 25))))
    except (ValueError, TypeError):
        page_size = 25

    qs = SesionActiva.objects.all().order_by('-creado_en')
    if agente_id:
        qs = qs.filter(id_agente=agente_id)

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    items = []
    for s in page_obj:
        items.append({
            'id_sesion_activa': s.id_sesion_activa,
            'id_agente': s.id_agente_id,  # ForeignKey field stores the ID in _id attribute
            'session_key': s.session_key,
            'ip_address': str(s.ip_address) if s.ip_address else None,
            'user_agent': s.user_agent,
            'dispositivo': s.dispositivo,
            'navegador': s.navegador,
            'creado_en': s.creado_en,
            'ultimo_acceso': s.ultimo_acceso,
            'activa': s.activa,
        })

    return Response({
        'success': True,
        'page': page,
        'page_size': page_size,
        'total': paginator.count,
        'data': items
    })
