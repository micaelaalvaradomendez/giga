"""
Vistas para el módulo de asistencia - Sistema GIGA
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q, Count, Case, When, IntegerField
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date, time, timedelta
import logging

from .models import Asistencia, IntentoMarcacionFraudulenta, Licencia, TipoLicencia
from .serializers import (
    AsistenciaSerializer, IntentoFraudulentoSerializer,
    LicenciaSerializer, TipoLicenciaSerializer, ResumenAsistenciaSerializer
)
from personas.models import Agente, Area
from guardias.models import Feriado

logger = logging.getLogger(__name__)


def es_dia_laborable(fecha):
    """
    Verifica si una fecha es un día laborable.
    Retorna False si es sábado, domingo o feriado.
    """
    # Verificar si es fin de semana (sábado=5, domingo=6)
    if fecha.weekday() in [5, 6]:  # 0=Lunes, 6=Domingo
        return False
    
    # Verificar si es feriado
    if Feriado.es_feriado(fecha):
        return False
        
    return True


def get_motivo_no_laborable(fecha):
    """
    Retorna el motivo por el cual una fecha no es laborable.
    """
    if fecha.weekday() == 5:  # Sábado
        return "sábado"
    elif fecha.weekday() == 6:  # Domingo
        return "domingo"
    elif Feriado.es_feriado(fecha):
        feriados = Feriado.feriados_en_fecha(fecha)
        if feriados.exists():
            nombres = [f.nombre for f in feriados]
            return f"feriado ({', '.join(nombres)})"
    
    return None


def get_client_ip(request):
    """Obtener la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def marcar_asistencia(request):
    """
    Marcar entrada o salida de un agente con DNI.
    Los administradores pueden marcar asistencia de otros agentes.
    """
    try:
        dni_ingresado = request.data.get('dni', '').strip()
        tipo_marcacion = request.data.get('tipo_marcacion')  # 'entrada' o 'salida'
        observacion = request.data.get('observacion', '')
        hora_especifica_str = request.data.get('hora_especifica')  # Nueva: hora específica en formato HH:MM
        
        if not dni_ingresado:
            return Response({
                'success': False,
                'message': 'Debe ingresar un DNI'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener agente de la sesión
        agente_sesion_id = request.session.get('user_id')
        if not agente_sesion_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente_sesion = Agente.objects.get(id_agente=agente_sesion_id, activo=True)
        
        # Verificar si el usuario es administrador
        rol_sesion = agente_sesion.agenterol_set.first()
        es_admin = rol_sesion and rol_sesion.id_rol.nombre in ['Administrador', 'Director', 'Jefatura']
        
        # Obtener el agente al que se le va a marcar asistencia
        if es_admin:
            # El admin puede marcar para cualquier agente
            try:
                agente_a_marcar = Agente.objects.get(dni=dni_ingresado, activo=True)
            except Agente.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'No se encontró un agente activo con DNI {dni_ingresado}'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Usuario normal solo puede marcar su propia asistencia
            agente_a_marcar = agente_sesion
            
            # Verificar que el DNI corresponda al agente logueado
            if agente_sesion.dni != dni_ingresado:
                # Registrar intento fraudulento
                agente_dni = Agente.objects.filter(dni=dni_ingresado).first()
                
                with transaction.atomic():
                    intento = IntentoMarcacionFraudulenta.objects.create(
                        fecha=date.today(),
                        hora=datetime.now().time(),
                        dni_ingresado=dni_ingresado,
                        id_agente_sesion=agente_sesion,
                        id_agente_dni=agente_dni,
                        tipo_intento='entrada_salida',
                        ip_address=get_client_ip(request)
                    )
                    
                    logger.warning(
                        f'Intento fraudulento: Agente {agente_sesion.id_agente} '
                        f'intentó usar DNI {dni_ingresado}'
                    )
                
                return Response({
                    'success': False,
                    'message': 'El DNI ingresado no corresponde a su usuario',
                    'tipo': 'error_dni',
                    'registrado_en_auditoria': True
                }, status=status.HTTP_403_FORBIDDEN)
        
        # DNI correcto, proceder con marcación
        hoy = date.today()
        
        # Verificar si es un día laborable
        if not es_dia_laborable(hoy):
            motivo = get_motivo_no_laborable(hoy)
            return Response({
                'success': False,
                'message': f'No se puede registrar asistencia en {motivo}',
                'tipo': 'dia_no_laborable',
                'motivo': motivo
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determinar la hora a usar (específica o actual)
        if hora_especifica_str and es_admin:
            try:
                hora_para_marcar = datetime.strptime(hora_especifica_str, '%H:%M').time()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de hora inválido. Use HH:MM (ej: 08:30)'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            hora_para_marcar = datetime.now().time()
        
        with transaction.atomic():
            # Buscar o crear asistencia del día
            asistencia, created = Asistencia.objects.get_or_create(
                id_agente=agente_a_marcar,
                fecha=hoy,
                defaults={
                    'id_area': agente_a_marcar.id_area,
                    'hora_entrada': None,
                    'hora_salida': None
                }
            )
            
            # Si es admin y especificó tipo_marcacion, respetarlo
            if es_admin and tipo_marcacion:
                if tipo_marcacion == 'entrada':
                    asistencia.hora_entrada = hora_para_marcar
                    if observacion:
                        asistencia.observaciones = observacion
                    asistencia.es_correccion = True
                    asistencia.corregido_por = agente_sesion
                    asistencia.save()
                    
                    return Response({
                        'success': True,
                        'message': f'Entrada registrada a las {hora_para_marcar.strftime("%H:%M")} por administrador',
                        'tipo': 'entrada',
                        'data': {
                            'fecha': hoy,
                            'hora_entrada': hora_para_marcar,
                            'agente': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}"
                        }
                    })
                elif tipo_marcacion == 'salida':
                    if not asistencia.hora_entrada:
                        return Response({
                            'success': False,
                            'message': 'No se puede marcar salida sin entrada previa'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    asistencia.hora_salida = hora_para_marcar
                    if observacion:
                        if asistencia.observaciones:
                            asistencia.observaciones += f" | {observacion}"
                        else:
                            asistencia.observaciones = observacion
                    asistencia.es_correccion = True
                    asistencia.corregido_por = agente_sesion
                    asistencia.save()
                    
                    return Response({
                        'success': True,
                        'message': f'Salida registrada a las {hora_para_marcar.strftime("%H:%M")} por administrador',
                        'tipo': 'salida',
                        'data': {
                            'fecha': hoy,
                            'hora_entrada': asistencia.hora_entrada,
                            'hora_salida': hora_para_marcar,
                            'agente': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}"
                        }
                    })
            
            # Lógica normal: determinar automáticamente si es entrada o salida
            if asistencia.hora_entrada is None:
                # Marcar entrada
                asistencia.hora_entrada = hora_para_marcar
                if observacion:
                    asistencia.observaciones = observacion
                asistencia.save()
                
                return Response({
                    'success': True,
                    'message': f'Entrada registrada a las {hora_para_marcar.strftime("%H:%M")}',
                    'tipo': 'entrada',
                    'data': {
                        'fecha': hoy,
                        'hora_entrada': hora_para_marcar,
                        'agente': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}"
                    }
                })
            
            elif asistencia.hora_salida is None:
                # Marcar salida
                asistencia.hora_salida = hora_para_marcar
                if observacion:
                    if asistencia.observaciones:
                        asistencia.observaciones += f" | {observacion}"
                    else:
                        asistencia.observaciones = observacion
                
                # Calcular horas efectivas solo si ambas están presentes
                if asistencia.hora_entrada:
                    entrada_dt = timezone.make_aware(timezone.datetime.combine(hoy, asistencia.hora_entrada))
                    salida_dt = timezone.make_aware(timezone.datetime.combine(hoy, hora_para_marcar))
                    if salida_dt > entrada_dt:
                        diferencia = salida_dt - entrada_dt
                        horas_efectivas = diferencia.total_seconds() / 3600  # Convertir a horas
                        asistencia.horas_efectivas = round(horas_efectivas, 2)
                    else:
                        asistencia.horas_efectivas = 0
                
                asistencia.save()
                
                return Response({
                    'success': True,
                    'message': f'Salida registrada a las {hora_para_marcar.strftime("%H:%M")}',
                    'tipo': 'salida',
                    'data': {
                        'fecha': hoy,
                        'hora_entrada': asistencia.hora_entrada,
                        'hora_salida': hora_para_marcar,
                        'horas_efectivas': asistencia.horas_efectivas,
                        'agente': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}"
                    }
                })
            
            else:
                # Ya tiene entrada y salida
                return Response({
                    'success': False,
                    'message': 'Ya has registrado entrada y salida para hoy',
                    'tipo': 'ya_completo',
                    'data': {
                        'fecha': hoy,
                        'hora_entrada': asistencia.hora_entrada,
                        'hora_salida': asistencia.hora_salida
                    }
                })
    
    except Agente.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Agente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f'Error en marcar_asistencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error al registrar asistencia: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_estado_asistencia(request):
    """
    Obtener el estado de asistencia del agente logueado para hoy.
    """
    try:
        agente_id = request.session.get('user_id')  # Cambiar de agente_id a user_id
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        hoy = date.today()
        
        # Verificar si es un día laborable
        if not es_dia_laborable(hoy):
            motivo = get_motivo_no_laborable(hoy)
            return Response({
                'success': True,
                'data': {
                    'tiene_entrada': False,
                    'tiene_salida': False,
                    'hora_entrada': None,
                    'hora_salida': None,
                    'puede_marcar_entrada': False,
                    'puede_marcar_salida': False,
                    'es_dia_no_laborable': True,
                    'motivo_no_laborable': motivo
                }
            })
        
        try:
            asistencia = Asistencia.objects.get(
                id_agente_id=agente_id,
                fecha=hoy
            )
            
            return Response({
                'success': True,
                'data': {
                    'tiene_entrada': asistencia.hora_entrada is not None,
                    'tiene_salida': asistencia.hora_salida is not None,
                    'hora_entrada': asistencia.hora_entrada,
                    'hora_salida': asistencia.hora_salida,
                    'puede_marcar_entrada': asistencia.hora_entrada is None,
                    'puede_marcar_salida': asistencia.hora_entrada is not None and asistencia.hora_salida is None
                }
            })
        
        except Asistencia.DoesNotExist:
            return Response({
                'success': True,
                'data': {
                    'tiene_entrada': False,
                    'tiene_salida': False,
                    'hora_entrada': None,
                    'hora_salida': None,
                    'puede_marcar_entrada': True,
                    'puede_marcar_salida': False
                }
            })
    
    except Exception as e:
        logger.error(f'Error en obtener_estado_asistencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_tipos_licencia(request):
    """
    Listar todos los tipos de licencia disponibles.
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({'success': False, 'message': 'No hay sesión activa'}, status=status.HTTP_401_UNAUTHORIZED)

        # El modelo TipoLicencia tiene campos 'codigo' y 'descripcion'.
        # Antes se ordenaba por 'nombre' (inexistente) lo que provocaba
        # "Cannot resolve keyword 'nombre' into field" en las consultas.
        tipos_licencia = TipoLicencia.objects.all().order_by('codigo')
        serializer = TipoLicenciaSerializer(tipos_licencia, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    except Exception as e:
        logger.error(f'Error en listar_tipos_licencia: {str(e)}')
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def crear_tipo_licencia(request):
    """
    Crear un nuevo tipo de licencia (solo administradores).
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({'success': False, 'message': 'No hay sesión activa'}, status=status.HTTP_401_UNAUTHORIZED)

        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()

        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director']:
            return Response({'success': False, 'message': 'No tiene permisos para crear tipos de licencia'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TipoLicenciaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Tipo de licencia creado correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f'Error en crear_tipo_licencia: {str(e)}')
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def actualizar_tipo_licencia(request, tipo_licencia_id):
    """
    Actualizar un tipo de licencia existente (solo administradores).
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({'success': False, 'message': 'No hay sesión activa'}, status=status.HTTP_401_UNAUTHORIZED)

        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()

        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director']:
            return Response({'success': False, 'message': 'No tiene permisos para actualizar tipos de licencia'}, status=status.HTTP_403_FORBIDDEN)

        tipo_licencia = TipoLicencia.objects.get(id_tipo_licencia=tipo_licencia_id)
        serializer = TipoLicenciaSerializer(tipo_licencia, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Tipo de licencia actualizado correctamente',
                'data': serializer.data
            })
        
        return Response({'success': False, 'message': 'Datos inválidos', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except TipoLicencia.DoesNotExist:
        return Response({'success': False, 'message': 'Tipo de licencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en actualizar_tipo_licencia: {str(e)}')
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_tipo_licencia(request, tipo_licencia_id):
    """
    Eliminar un tipo de licencia (solo administradores).
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({'success': False, 'message': 'No hay sesión activa'}, status=status.HTTP_401_UNAUTHORIZED)

        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()

        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director']:
            return Response({'success': False, 'message': 'No tiene permisos para eliminar tipos de licencia'}, status=status.HTTP_403_FORBIDDEN)

        tipo_licencia = TipoLicencia.objects.get(id_tipo_licencia=tipo_licencia_id)
        tipo_licencia.delete()

        return Response({'success': True, 'message': 'Tipo de licencia eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

    except TipoLicencia.DoesNotExist:
        return Response({'success': False, 'message': 'Tipo de licencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en eliminar_tipo_licencia: {str(e)}')
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_asistencias(request):
    """
    Listar asistencias con filtros por fecha, área, estado.
    Solo para administradores.
    """
    try:
        # Verificar que el usuario sea administrador
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()
        
        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director', 'Jefatura']:
            return Response({
                'success': False,
                'message': 'No tiene permisos para ver asistencias'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Filtros
        fecha_desde = request.GET.get('fecha_desde', date.today().isoformat())
        fecha_hasta = request.GET.get('fecha_hasta', date.today().isoformat())
        area_id = request.GET.get('area_id')
        estado_filtro = request.GET.get('estado')  # 'completa', 'sin_salida', 'sin_entrada'
        
        # Caso especial: sin_entrada (ausentes) - buscar agentes sin registro de asistencia
        if estado_filtro == 'sin_entrada':
            # Verificar si la fecha consultada es un día laborable
            fecha_consulta = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            if not es_dia_laborable(fecha_consulta):
                # Si no es día laborable, no hay ausentes a mostrar
                return Response({
                    'success': True,
                    'data': [],
                    'total': 0,
                    'message': f'No se registra asistencia en {get_motivo_no_laborable(fecha_consulta)}'
                })
            
            # Obtener agentes activos según permisos
            agentes_query = Agente.objects.filter(activo=True)
            
            if area_id:
                agentes_query = agentes_query.filter(id_area_id=area_id)
            elif rol.id_rol.nombre == 'Jefatura':
                agentes_query = agentes_query.filter(id_area=agente.id_area)
            
            # Obtener IDs de agentes que SÍ tienen asistencia en ese rango de fechas
            agentes_con_asistencia = Asistencia.objects.filter(
                fecha__gte=fecha_desde,
                fecha__lte=fecha_hasta
            ).values_list('id_agente_id', flat=True).distinct()
            
            # Filtrar agentes que NO tienen asistencia (ausentes)
            agentes_ausentes = agentes_query.exclude(
                id_agente__in=agentes_con_asistencia
            ).select_related('id_area').order_by('apellido')
            
            # Construir respuesta en formato similar al serializer de asistencias
            ausentes_data = []
            for agente_obj in agentes_ausentes:
                ausentes_data.append({
                    'id_asistencia': None,
                    'fecha': fecha_desde,
                    'agente_nombre': f"{agente_obj.apellido}, {agente_obj.nombre}",
                    'agente_dni': agente_obj.dni,
                    'area_nombre': agente_obj.id_area.nombre if agente_obj.id_area else 'Sin área',
                    'hora_entrada': None,
                    'hora_salida': None,
                    'horario_esperado_entrada': str(agente_obj.horario_entrada) if agente_obj.horario_entrada else None,
                    'horario_esperado_salida': str(agente_obj.horario_salida) if agente_obj.horario_salida else None,
                    'marcacion_entrada_automatica': False,
                    'marcacion_salida_automatica': False,
                    'es_correccion': False,
                    'corregido_por_nombre': None,
                    'observaciones': None,
                    'id_agente': agente_obj.id_agente,
                    'id_area': agente_obj.id_area.id_area if agente_obj.id_area else None
                })
            
            return Response({
                'success': True,
                'data': ausentes_data,
                'total': len(ausentes_data)
            })
        
        # Para otros estados, consultar asistencias normalmente
        queryset = Asistencia.objects.select_related(
            'id_agente', 'id_area', 'corregido_por'
        ).filter(
            fecha__gte=fecha_desde,
            fecha__lte=fecha_hasta
        )
        
        # Filtro por área
        if area_id:
            queryset = queryset.filter(id_area_id=area_id)
        elif rol.id_rol.nombre == 'Jefatura':
            # Jefatura solo ve su área
            queryset = queryset.filter(id_area=agente.id_area)
        
        # Filtro por estado
        if estado_filtro == 'completa':
            queryset = queryset.filter(hora_entrada__isnull=False, hora_salida__isnull=False)
        elif estado_filtro == 'sin_salida':
            queryset = queryset.filter(hora_entrada__isnull=False, hora_salida__isnull=True)
        
        queryset = queryset.order_by('-fecha', 'id_agente__apellido')
        
        serializer = AsistenciaSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'total': queryset.count()
        })
    
    except Exception as e:
        logger.error(f'Error en listar_asistencias: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def resumen_asistencias(request):
    """
    Obtener resumen de asistencias por fecha y área.
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()
        
        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director', 'Jefatura']:
            return Response({
                'success': False,
                'message': 'No tiene permisos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        fecha = request.GET.get('fecha', date.today().isoformat())
        area_id = request.GET.get('area_id')
        
        # Obtener agentes activos del área
        agentes_query = Agente.objects.filter(activo=True)
        
        if area_id:
            agentes_query = agentes_query.filter(id_area_id=area_id)
        elif rol.id_rol.nombre == 'Jefatura':
            agentes_query = agentes_query.filter(id_area=agente.id_area)
        
        total_agentes = agentes_query.count()
        
        # Contar asistencias
        asistencias = Asistencia.objects.filter(fecha=fecha)
        if area_id:
            asistencias = asistencias.filter(id_area_id=area_id)
        elif rol.id_rol.nombre == 'Jefatura':
            asistencias = asistencias.filter(id_area=agente.id_area)
        
        presentes = asistencias.filter(hora_entrada__isnull=False).count()
        sin_salida = asistencias.filter(hora_entrada__isnull=False, hora_salida__isnull=True).count()
        salidas_automaticas = asistencias.filter(marcacion_salida_automatica=True).count()
        
        # Contar licencias
        licencias = Licencia.objects.filter(
            fecha_desde__lte=fecha,
            fecha_hasta__gte=fecha,
            estado='aprobada'
        )
        if area_id:
            licencias = licencias.filter(id_agente__id_area_id=area_id)
        elif rol.id_rol.nombre == 'Jefatura':
            licencias = licencias.filter(id_agente__id_area=agente.id_area)
        
        en_licencia = licencias.count()
        
        ausentes = total_agentes - presentes - en_licencia
        
        return Response({
            'success': True,
            'data': {
                'fecha': fecha,
                'total_agentes': total_agentes,
                'presentes': presentes,
                'ausentes': ausentes,
                'sin_salida': sin_salida,
                'salidas_automaticas': salidas_automaticas,
                'en_licencia': en_licencia
            }
        })
    
    except Exception as e:
        logger.error(f'Error en resumen_asistencias: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def corregir_asistencia(request, asistencia_id):
    """
    Corregir una asistencia (solo administradores).
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()
        
        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director']:
            return Response({
                'success': False,
                'message': 'No tiene permisos para corregir asistencias'
            }, status=status.HTTP_403_FORBIDDEN)
        
        asistencia = Asistencia.objects.get(id_asistencia=asistencia_id)
        
        # Validar y procesar horas
        hora_entrada = request.data.get('hora_entrada')
        hora_salida = request.data.get('hora_salida')
        
        # Validar formato de horas si se proporcionan
        if hora_entrada:
            try:
                from datetime import datetime
                datetime.strptime(hora_entrada, '%H:%M')
                asistencia.hora_entrada = hora_entrada
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de hora de entrada inválido. Use HH:MM'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if hora_salida:
            try:
                from datetime import datetime
                datetime.strptime(hora_salida, '%H:%M')
                asistencia.hora_salida = hora_salida
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de hora de salida inválido. Use HH:MM'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que la salida sea posterior a la entrada
        if asistencia.hora_entrada and asistencia.hora_salida:
            if asistencia.hora_entrada >= asistencia.hora_salida:
                return Response({
                    'success': False,
                    'message': 'La hora de salida debe ser posterior a la hora de entrada'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marcar como corrección
        asistencia.es_correccion = True
        asistencia.corregido_por = agente
        
        # Actualizar observaciones
        observacion = request.data.get('observacion', '')
        if observacion:
            if asistencia.observaciones:
                asistencia.observaciones += f" | CORRECCIÓN: {observacion}"
            else:
                asistencia.observaciones = f"CORRECCIÓN: {observacion}"
        
        asistencia.save()
        
        serializer = AsistenciaSerializer(asistencia)
        
        return Response({
            'success': True,
            'message': 'Asistencia corregida correctamente',
            'data': serializer.data
        })
    
    except Asistencia.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Asistencia no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f'Error en corregir_asistencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_licencias(request):
    """
    Listar licencias activas para una fecha.
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        fecha = request.GET.get('fecha', date.today().isoformat())
        area_id = request.GET.get('area_id')
        
        queryset = Licencia.objects.select_related(
            'id_agente', 'id_tipo_licencia'
        ).filter(
            fecha_desde__lte=fecha,
            fecha_hasta__gte=fecha,
            estado='aprobada'
        )
        
        if area_id:
            queryset = queryset.filter(id_agente__id_area_id=area_id)
        
        serializer = LicenciaSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except Exception as e:
        logger.error(f'Error en listar_licencias: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def ejecutar_marcacion_automatica(request):
    """
    Ejecutar marcación automática de salidas a las 22:00.
    Este endpoint debe ser llamado por un cron job o tarea programada.
    """
    try:
        # Solo permite ejecución desde el sistema
        auth_key = request.data.get('auth_key')
        if auth_key != 'GIGA_CRON_KEY_2025':
            return Response({
                'success': False,
                'message': 'No autorizado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        ayer = date.today() - timedelta(days=1)
        
        # Actualizar asistencias sin salida del día anterior
        asistencias_actualizadas = Asistencia.objects.filter(
            fecha=ayer,
            hora_entrada__isnull=False,
            hora_salida__isnull=True
        ).update(
            hora_salida=time(22, 0),
            marcacion_salida_automatica=True,
            actualizado_en=timezone.now()
        )
        
        logger.info(f'Marcación automática ejecutada: {asistencias_actualizadas} salidas marcadas')
        
        return Response({
            'success': True,
            'message': f'Se marcaron {asistencias_actualizadas} salidas automáticas',
            'fecha': ayer,
            'total_marcadas': asistencias_actualizadas
        })
    
    except Exception as e:
        logger.error(f'Error en ejecutar_marcacion_automatica: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def marcar_como_ausente(request, asistencia_id):
    """
    Marcar un agente como ausente (eliminar su presentismo).
    Solo para administradores.
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()
        
        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director']:
            return Response({
                'success': False,
                'message': 'No tiene permisos para marcar ausentes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        asistencia = Asistencia.objects.get(id_asistencia=asistencia_id)
        
        # Validar observación obligatoria
        observacion = request.data.get('observacion', '').strip()
        if not observacion:
            return Response({
                'success': False,
                'message': 'Debe proporcionar una observación explicando el motivo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Eliminar las marcaciones y marcar como ausente
        asistencia.hora_entrada = None
        asistencia.hora_salida = None
        asistencia.horas_efectivas = None
        asistencia.marcacion_entrada_automatica = False
        asistencia.marcacion_salida_automatica = False
        asistencia.es_correccion = True
        asistencia.corregido_por = agente
        
        # Agregar observación de ausencia
        if asistencia.observaciones:
            asistencia.observaciones += f" | MARCADO COMO AUSENTE: {observacion}"
        else:
            asistencia.observaciones = f"MARCADO COMO AUSENTE: {observacion}"
        
        asistencia.save()
        
        logger.info(
            f'Agente {asistencia.id_agente.id_agente} marcado como ausente '
            f'para el {asistencia.fecha} por {agente.id_agente}'
        )
        
        return Response({
            'success': True,
            'message': f'Agente {asistencia.id_agente.nombre} {asistencia.id_agente.apellido} marcado como ausente',
            'data': {
                'fecha': asistencia.fecha,
                'agente': f"{asistencia.id_agente.nombre} {asistencia.id_agente.apellido}",
                'motivo': observacion
            }
        })
    
    except Asistencia.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Asistencia no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f'Error en marcar_como_ausente: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
