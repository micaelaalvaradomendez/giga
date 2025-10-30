from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes
from django.db import transaction
from datetime import datetime, time
from .models import CronogramaGuardias, Guardia
from personas.models import Area, Agente, AgenteRol, Usuario


class PlanificarCronogramaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description='Crea un cronograma y guardias en estado borrador para aprobación posterior.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'desde': {'type': 'string', 'format': 'date'},
                    'hasta': {'type': 'string', 'format': 'date'},
                    'horas_totales': {'type': 'number'},
                    'area_id': {'type': 'string', 'format': 'uuid', 'nullable': True},
                    'asignaciones': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'fecha': {'type': 'string', 'format': 'date'},
                                'usuario_id': {'type': 'string', 'format': 'uuid'},
                                'horas': {'type': 'number'}
                            },
                            'required': ['fecha', 'usuario_id', 'horas']
                        }
                    }
                },
                'required': ['desde', 'hasta', 'horas_totales', 'asignaciones']
            }
        },
        responses={200: {'type': 'object', 'properties': {
            'cronograma_id': {'type': 'string', 'format': 'uuid'},
            'guardias_creadas': {'type': 'integer'},
            'mensaje': {'type': 'string'}
        }},
        400: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}},
        tags=['guardias']
    )
    def post(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        desde = data.get('desde')
        hasta = data.get('hasta')
        horas_totales = data.get('horas_totales')
        asignaciones = data.get('asignaciones', [])
        area_id = data.get('area_id')

        if not desde or not hasta:
            return Response({'detail': 'desde y hasta son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        if not horas_totales or float(horas_totales) <= 0:
            return Response({'detail': 'horas_totales debe ser > 0'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            d_desde = datetime.strptime(desde, '%Y-%m-%d').date()
            d_hasta = datetime.strptime(hasta, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': 'Formato de fecha inválido (usar YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)
        if d_desde > d_hasta:
            return Response({'detail': 'desde no puede ser mayor a hasta'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            jefe_agente = Agente.objects.get(usuario=request.user)
        except Agente.DoesNotExist:
            return Response({'detail': 'El usuario no está vinculado a un agente'}, status=status.HTTP_403_FORBIDDEN)

        # Validar que las asignaciones correspondan a subordinados del jefe
        subordinados_ids = set(Agente.objects.filter(id_jefe=jefe_agente).values_list('usuario_id', flat=True))
        for it in asignaciones:
            if it.get('usuario_id') not in [str(u) for u in subordinados_ids]:
                return Response({'detail': 'Asignaciones incluyen usuarios que no son subordinados'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar horas totales
        horas_sum = sum(float(it.get('horas') or 0) for it in asignaciones)
        if horas_sum > float(horas_totales):
            return Response({'detail': f'Las horas asignadas ({horas_sum}) exceden las horas_totales ({horas_totales})'}, status=status.HTTP_400_BAD_REQUEST)

        # Resolver área
        area = None
        if area_id:
            try:
                area = Area.objects.get(id=area_id)
            except Area.DoesNotExist:
                return Response({'detail': 'area_id no existe'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ag_rol = AgenteRol.objects.filter(usuario=request.user, area__isnull=False).select_related('area').first()
            area = ag_rol.area if ag_rol else Area.objects.order_by('nombre').first()
            if not area:
                return Response({'detail': 'No hay un área disponible para el cronograma'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            cronograma = CronogramaGuardias.objects.create(
                area=area,
                fecha=d_desde,
                hora_inicio=time(0, 0),
                hora_fin=time(23, 59),
                tipo='mensual',
                estado='generada',
                creado_por=request.user,
                actualizado_por=request.user,
            )

            creadas = 0
            for it in asignaciones:
                try:
                    f = datetime.strptime(it['fecha'], '%Y-%m-%d').date()
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'detail': f"Fecha inválida en asignación: {it.get('fecha')}"}, status=status.HTTP_400_BAD_REQUEST)
                g, _created = Guardia.objects.get_or_create(
                    cronograma=cronograma,
                    usuario_id=it['usuario_id'],
                    fecha=f,
                    defaults={
                        'estado': 'borrador',
                        'activa': False,
                        'creado_por': request.user,
                        'actualizado_por': request.user,
                    }
                )
                # Actualizar horas planificadas
                g.horas_planificadas = float(it['horas'])
                g.estado = 'borrador'
                g.activa = False
                g.actualizado_por = request.user
                g.save()
                creadas += 1

        return Response({
            'cronograma_id': str(cronograma.id),
            'guardias_creadas': creadas,
            'mensaje': 'Cronograma generado en estado generada y guardias en borrador'
        }, status=status.HTTP_200_OK)
