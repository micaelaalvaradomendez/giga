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
from auditoria.models import Auditoria

# RBAC Permissions
from common.permissions import (
    IsAuthenticatedGIGA, IsAdministrador, IsJefaturaOrAbove,
    CanApprove, obtener_agente_sesion, obtener_rol_agente,
    obtener_areas_jerarquia
)

logger = logging.getLogger(__name__)


def crear_auditoria_asistencia(agente_realizador_id, accion, asistencia_id, valor_previo=None, valor_nuevo=None):
    """
    Crear registro de auditoría específico para asistencias.
    """
    try:
        from django.utils import timezone
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        # Convertir datos a JSON serializable
        valor_previo_json = None
        valor_nuevo_json = None
        
        if valor_previo:
            valor_previo_json = json.loads(json.dumps(valor_previo, cls=DjangoJSONEncoder))
        
        if valor_nuevo:
            valor_nuevo_json = json.loads(json.dumps(valor_nuevo, cls=DjangoJSONEncoder))
        
        Auditoria.objects.create(
            pk_afectada=asistencia_id,
            nombre_tabla='asistencia',
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=agente_realizador_id
        )
    except Exception as e:
        logger.error(f"Error creando auditoría de asistencia: {e}")
        # No fallar la operación principal por error de auditoría
        pass


def crear_auditoria_licencia(agente_realizador_id, accion, licencia_id, valor_previo=None, valor_nuevo=None):
    """
    Crear registro de auditoría específico para licencias.
    """
    try:
        from django.utils import timezone
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        # Convertir datos a JSON serializable
        valor_previo_json = None
        valor_nuevo_json = None
        
        if valor_previo:
            valor_previo_json = json.loads(json.dumps(valor_previo, cls=DjangoJSONEncoder))
        
        if valor_nuevo:
            valor_nuevo_json = json.loads(json.dumps(valor_nuevo, cls=DjangoJSONEncoder))
        
        Auditoria.objects.create(
            pk_afectada=licencia_id,
            nombre_tabla='licencia',
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=agente_realizador_id
        )
    except Exception as e:
        logger.error(f"Error creando auditoría de licencia: {e}")
        # No fallar la operación principal por error de auditoría
        pass


def crear_auditoria_tipo_licencia(agente_realizador_id, accion, tipo_licencia_id, valor_previo=None, valor_nuevo=None):
    """
    Crear registro de auditoría específico para tipos de licencia.
    """
    try:
        from django.utils import timezone
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        # Convertir datos a JSON serializable
        valor_previo_json = None
        valor_nuevo_json = None
        
        if valor_previo:
            valor_previo_json = json.loads(json.dumps(valor_previo, cls=DjangoJSONEncoder))
        
        if valor_nuevo:
            valor_nuevo_json = json.loads(json.dumps(valor_nuevo, cls=DjangoJSONEncoder))
        
        Auditoria.objects.create(
            pk_afectada=tipo_licencia_id,
            nombre_tabla='tipo_licencia',
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=agente_realizador_id
        )
    except Exception as e:
        logger.error(f"Error creando auditoría de tipo de licencia: {e}")
        # No fallar la operación principal por error de auditoría
        pass


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
@permission_classes([IsAuthenticatedGIGA])  # ✅ SEGURIDAD: Solo usuarios autenticados
def marcar_asistencia(request):
    """
    Marcar entrada o salida de un agente con DNI.
    Los administradores pueden marcar asistencia de otros agentes.
    
    SEGURIDAD:
    - Requiere sesión GIGA válida (IsAuthenticatedGIGA)
    - Anti-fraude implementado: valida que DNI coincida con sesión
    - Registra intentos fraudulentos en tabla de auditoría
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
        fecha_especifica_str = request.data.get('fecha_especifica')  # Nueva: fecha específica en formato YYYY-MM-DD
        
        # Determinar la fecha a usar
        if fecha_especifica_str and es_admin:
            try:
                fecha_para_marcar = datetime.strptime(fecha_especifica_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-11-24)'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            fecha_para_marcar = date.today()
        
        # Verificar si es un día laborable (solo para fechas actuales, no para correcciones históricas)
        if fecha_para_marcar == date.today() and not es_dia_laborable(fecha_para_marcar):
            motivo = get_motivo_no_laborable(fecha_para_marcar)
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
                fecha=fecha_para_marcar,
                defaults={
                    'id_area': agente_a_marcar.id_area,
                    'hora_entrada': None,
                    'hora_salida': None
                }
            )
            
            # Auditoría: Si se creó nueva asistencia
            if created:
                valor_nuevo = {
                    'agente_dni': agente_a_marcar.dni,
                    'agente_nombre': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}",
                    'fecha': str(fecha_para_marcar),
                    'area': agente_a_marcar.id_area.nombre if agente_a_marcar.id_area else None,
                    'creado_por_admin': es_admin,
                    'motivo': 'Creación automática de registro de asistencia'
                }
                crear_auditoria_asistencia(
                    agente_sesion_id, 
                    'CREAR_ASISTENCIA', 
                    asistencia.id_asistencia, 
                    None, 
                    valor_nuevo
                )
            
            # Si es admin y especificó tipo_marcacion, respetarlo
            if es_admin and tipo_marcacion:
                if tipo_marcacion == 'entrada':
                    # Auditoría: Capturar estado previo
                    valor_previo = {
                        'hora_entrada': str(asistencia.hora_entrada) if asistencia.hora_entrada else None,
                        'observaciones': asistencia.observaciones,
                        'es_correccion': asistencia.es_correccion
                    }
                    
                    asistencia.hora_entrada = hora_para_marcar
                    if observacion:
                        asistencia.observaciones = observacion
                    asistencia.es_correccion = True
                    asistencia.corregido_por = agente_sesion
                    asistencia.save()
                    
                    # Auditoría: Registrar marcación de entrada por admin
                    valor_nuevo = {
                        'hora_entrada': str(hora_para_marcar),
                        'observaciones': observacion,
                        'es_correccion': True,
                        'corregido_por': f"{agente_sesion.nombre} {agente_sesion.apellido}",
                        'agente_afectado': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}",
                        'agente_dni': agente_a_marcar.dni,
                        'fecha': str(fecha_para_marcar),
                        'marcacion_admin': True
                    }
                    crear_auditoria_asistencia(
                        agente_sesion_id, 
                        'MARCAR_ENTRADA_ADMIN', 
                        asistencia.id_asistencia, 
                        valor_previo, 
                        valor_nuevo
                    )
                    
                    return Response({
                        'success': True,
                        'message': f'Entrada registrada a las {hora_para_marcar.strftime("%H:%M")} por administrador',
                        'tipo': 'entrada',
                        'data': {
                            'fecha': fecha_para_marcar,
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
                    
                    # Auditoría: Capturar estado previo
                    valor_previo = {
                        'hora_salida': str(asistencia.hora_salida) if asistencia.hora_salida else None,
                        'observaciones': asistencia.observaciones,
                        'es_correccion': asistencia.es_correccion
                    }
                    
                    asistencia.hora_salida = hora_para_marcar
                    if observacion:
                        if asistencia.observaciones:
                            asistencia.observaciones += f" | {observacion}"
                        else:
                            asistencia.observaciones = observacion
                    asistencia.es_correccion = True
                    asistencia.corregido_por = agente_sesion
                    asistencia.save()
                    
                    # Auditoría: Registrar marcación de salida por admin
                    valor_nuevo = {
                        'hora_salida': str(hora_para_marcar),
                        'observaciones': asistencia.observaciones,
                        'es_correccion': True,
                        'corregido_por': f"{agente_sesion.nombre} {agente_sesion.apellido}",
                        'agente_afectado': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}",
                        'agente_dni': agente_a_marcar.dni,
                        'fecha': str(fecha_para_marcar),
                        'marcacion_admin': True
                    }
                    crear_auditoria_asistencia(
                        agente_sesion_id, 
                        'MARCAR_SALIDA_ADMIN', 
                        asistencia.id_asistencia, 
                        valor_previo, 
                        valor_nuevo
                    )
                    
                    return Response({
                        'success': True,
                        'message': f'Salida registrada a las {hora_para_marcar.strftime("%H:%M")} por administrador',
                        'tipo': 'salida',
                        'data': {
                            'fecha': fecha_para_marcar,
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
                
                # Auditoría: Registrar marcación normal de entrada
                valor_nuevo = {
                    'hora_entrada': str(hora_para_marcar),
                    'observaciones': observacion,
                    'agente_nombre': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}",
                    'agente_dni': agente_a_marcar.dni,
                    'fecha': str(fecha_para_marcar),
                    'marcacion_normal': True,
                    'es_admin': es_admin
                }
                crear_auditoria_asistencia(
                    agente_sesion_id, 
                    'MARCAR_ENTRADA', 
                    asistencia.id_asistencia, 
                    None, 
                    valor_nuevo
                )
                
                return Response({
                    'success': True,
                    'message': f'Entrada registrada a las {hora_para_marcar.strftime("%H:%M")}',
                    'tipo': 'entrada',
                    'data': {
                        'fecha': fecha_para_marcar,
                        'hora_entrada': hora_para_marcar,
                        'agente': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}"
                    }
                })
            
            elif asistencia.hora_salida is None:
                # Marcar salida
                valor_previo_salida = {
                    'hora_salida': str(asistencia.hora_salida) if asistencia.hora_salida else None,
                    'horas_efectivas': asistencia.horas_efectivas,
                    'observaciones': asistencia.observaciones
                }
                
                asistencia.hora_salida = hora_para_marcar
                if observacion:
                    if asistencia.observaciones:
                        asistencia.observaciones += f" | {observacion}"
                    else:
                        asistencia.observaciones = observacion
                
                # Calcular horas efectivas solo si ambas están presentes
                if asistencia.hora_entrada:
                    entrada_dt = timezone.make_aware(timezone.datetime.combine(fecha_para_marcar, asistencia.hora_entrada))
                    salida_dt = timezone.make_aware(timezone.datetime.combine(fecha_para_marcar, hora_para_marcar))
                    if salida_dt > entrada_dt:
                        diferencia = salida_dt - entrada_dt
                        horas_efectivas = diferencia.total_seconds() / 3600  # Convertir a horas
                        asistencia.horas_efectivas = round(horas_efectivas, 2)
                    else:
                        asistencia.horas_efectivas = 0
                
                asistencia.save()
                
                # Auditoría: Registrar marcación normal de salida
                valor_nuevo_salida = {
                    'hora_salida': str(hora_para_marcar),
                    'horas_efectivas': asistencia.horas_efectivas,
                    'observaciones': asistencia.observaciones,
                    'agente_nombre': f"{agente_a_marcar.nombre} {agente_a_marcar.apellido}",
                    'agente_dni': agente_a_marcar.dni,
                    'fecha': str(fecha_para_marcar),
                    'marcacion_normal': True,
                    'es_admin': es_admin
                }
                crear_auditoria_asistencia(
                    agente_sesion_id, 
                    'MARCAR_SALIDA', 
                    asistencia.id_asistencia, 
                    valor_previo_salida, 
                    valor_nuevo_salida
                )
                
                return Response({
                    'success': True,
                    'message': f'Salida registrada a las {hora_para_marcar.strftime("%H:%M")}',
                    'tipo': 'salida',
                    'data': {
                        'fecha': fecha_para_marcar,
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
                        'fecha': fecha_para_marcar,
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
@permission_classes([IsAuthenticatedGIGA])
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
@permission_classes([IsAuthenticatedGIGA])
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
@permission_classes([IsAdministrador])
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
            tipo_licencia = serializer.save()
            
            # Auditoría: Registrar creación de tipo de licencia
            valor_nuevo = {
                'codigo': tipo_licencia.codigo,
                'descripcion': tipo_licencia.descripcion,
                'creado_por': f"{agente.nombre} {agente.apellido}",
                'id_tipo_licencia': tipo_licencia.id_tipo_licencia
            }
            crear_auditoria_tipo_licencia(
                agente_id, 
                'CREAR_TIPO_LICENCIA', 
                tipo_licencia.id_tipo_licencia, 
                None, 
                valor_nuevo
            )
            
            logger.info(f'Tipo de licencia creado por {agente.nombre} {agente.apellido}: {tipo_licencia.codigo}')
            
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
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
        
        # Capturar valores previos para auditoría
        valor_previo = {
            'codigo': tipo_licencia.codigo,
            'descripcion': tipo_licencia.descripcion,
            'id_tipo_licencia': tipo_licencia.id_tipo_licencia
        }
        
        serializer = TipoLicenciaSerializer(tipo_licencia, data=request.data, partial=True)

        if serializer.is_valid():
            tipo_licencia_actualizado = serializer.save()
            
            # Auditoría: Registrar actualización de tipo de licencia
            valor_nuevo = {
                'codigo': tipo_licencia_actualizado.codigo,
                'descripcion': tipo_licencia_actualizado.descripcion,
                'actualizado_por': f"{agente.nombre} {agente.apellido}",
                'id_tipo_licencia': tipo_licencia_actualizado.id_tipo_licencia
            }
            crear_auditoria_tipo_licencia(
                agente_id, 
                'ACTUALIZAR_TIPO_LICENCIA', 
                tipo_licencia_id, 
                valor_previo, 
                valor_nuevo
            )
            
            logger.info(f'Tipo de licencia actualizado por {agente.nombre} {agente.apellido}: {tipo_licencia.codigo}')
            
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
@permission_classes([IsAdministrador])
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
        
        # Auditoría: Capturar datos antes de eliminar
        valor_previo = {
            'codigo': tipo_licencia.codigo,
            'descripcion': tipo_licencia.descripcion,
            'id_tipo_licencia': tipo_licencia.id_tipo_licencia,
            'eliminado_por': f"{agente.nombre} {agente.apellido}"
        }
        tipo_licencia_info = f"ID: {tipo_licencia.id_tipo_licencia}, Código: {tipo_licencia.codigo}"
        tipo_licencia_id_para_auditoria = tipo_licencia.id_tipo_licencia
        
        # Eliminar el tipo de licencia
        tipo_licencia.delete()
        
        # Auditoría: Registrar eliminación
        crear_auditoria_tipo_licencia(
            agente_id, 
            'ELIMINAR_TIPO_LICENCIA', 
            tipo_licencia_id_para_auditoria, 
            valor_previo, 
            None
        )
        
        logger.info(f'Tipo de licencia eliminado por {agente.nombre} {agente.apellido}: {tipo_licencia_info}')

        return Response({'success': True, 'message': 'Tipo de licencia eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

    except TipoLicencia.DoesNotExist:
        return Response({'success': False, 'message': 'Tipo de licencia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en eliminar_tipo_licencia: {str(e)}')
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsJefaturaOrAbove])
def listar_asistencias_admin(request):
    """
    Listar asistencias con filtros por fecha, área, estado.
    
    RBAC - Lógica Correcta:
    - Administrador: Todas las asistencias
    - Director: Asistencias de agentes de su área + sub-áreas
    - Jefatura: Asistencias de agentes de su área (sin sub-áreas)
    """
    try:
        # RBAC: Obtener agente y rol
        agente_sesion = obtener_agente_sesion(request)
        if not agente_sesion:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        rol_sesion = obtener_rol_agente(agente_sesion)
        
        # Filtros de consulta
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
            
            # Obtener agentes activos
            agentes_query = Agente.objects.filter(activo=True)
            
            # RBAC: Filtrar agentes por áreas permitidas
            # La lógica es la misma: Admin ve todos, Director área+sub, Jefatura solo área
            if rol_sesion != 'administrador':
                areas_permitidas = obtener_areas_jerarquia(agente_sesion)
                area_ids_permitidas = [a.id_area for a in areas_permitidas]
                agentes_query = agentes_query.filter(id_area__id_area__in=area_ids_permitidas)
            
            # Filtro adicional por área específica (si se proporciona)
            if area_id:
                agentes_query = agentes_query.filter(id_area_id=area_id)
            
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
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
        
        # Auditoría: Capturar estado previo ANTES de hacer cambios
        valor_previo = {
            'hora_entrada': str(asistencia.hora_entrada) if asistencia.hora_entrada else None,
            'hora_salida': str(asistencia.hora_salida) if asistencia.hora_salida else None,
            'observaciones': asistencia.observaciones,
            'es_correccion': asistencia.es_correccion,
            'corregido_por': f"{asistencia.corregido_por.nombre} {asistencia.corregido_por.apellido}" if asistencia.corregido_por else None,
            'agente_nombre': f"{asistencia.id_agente.nombre} {asistencia.id_agente.apellido}",
            'agente_dni': asistencia.id_agente.dni,
            'fecha': str(asistencia.fecha)
        }
        
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
        
        # Auditoría: Registrar corrección de asistencia
        valor_nuevo = {
            'hora_entrada': str(asistencia.hora_entrada) if asistencia.hora_entrada else None,
            'hora_salida': str(asistencia.hora_salida) if asistencia.hora_salida else None,
            'observaciones': asistencia.observaciones,
            'es_correccion': True,
            'corregido_por': f"{agente.nombre} {agente.apellido}",
            'agente_nombre': f"{asistencia.id_agente.nombre} {asistencia.id_agente.apellido}",
            'agente_dni': asistencia.id_agente.dni,
            'fecha': str(asistencia.fecha),
            'motivo_correccion': observacion,
            'hora_entrada_original': valor_previo['hora_entrada'],
            'hora_salida_original': valor_previo['hora_salida']
        }
        crear_auditoria_asistencia(
            agente_id, 
            'CORREGIR_ASISTENCIA', 
            asistencia.id_asistencia, 
            valor_previo, 
            valor_nuevo
        )
        
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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
def gestionar_licencias(request):
    """
    GET: Listar licencias con filtros y permisos jerárquicos.
    POST: Crear nueva licencia (solicitud o asignación).
    """
    if request.method == 'GET':
        return listar_licencias_impl(request)
    elif request.method == 'POST':
        return crear_licencia_impl(request)


def listar_licencias_impl(request):
    """
    Listar licencias con filtros y permisos jerárquicos.
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
        
        if not rol:
            return Response({
                'success': False,
                'message': 'Usuario sin rol asignado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Filtros de la URL
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        area_id = request.GET.get('area_id')
        estado = request.GET.get('estado')
        tipo_licencia_id = request.GET.get('tipo_licencia_id')
        
        # Convertir strings "null" a None
        if area_id in ('null', '', 'None'):
            area_id = None
        elif area_id:
            try:
                area_id = int(area_id)
            except (ValueError, TypeError):
                area_id = None
                
        if tipo_licencia_id in ('null', '', 'None'):
            tipo_licencia_id = None
        elif tipo_licencia_id:
            try:
                tipo_licencia_id = int(tipo_licencia_id)
            except (ValueError, TypeError):
                tipo_licencia_id = None
        
        # Base queryset con relaciones
        queryset = Licencia.objects.select_related(
            'id_agente__id_area', 'id_tipo_licencia'
        ).prefetch_related(
            'id_agente__agenterol_set__id_rol'
        )
        
        # Aplicar filtros según permisos y jerarquía del usuario
        rol_nombre = rol.id_rol.nombre
        
        if rol_nombre == 'Administrador':
            # Administrador ve todo
            pass
        elif rol_nombre == 'Director':
            # Director ve licencias de Director, Jefatura, Agente Avanzado y Agente de su área
            from personas.models import Rol
            roles_permitidos = ['Director', 'Jefatura', 'Agente Avanzado', 'Agente']
            queryset = queryset.filter(
                id_agente__id_area=agente.id_area,
                id_agente__agenterol__id_rol__nombre__in=roles_permitidos
            )
        elif rol_nombre == 'Jefatura':
            # Jefatura ve licencias de Jefatura, Agente Avanzado y Agente de su área
            from personas.models import Rol
            roles_permitidos = ['Jefatura', 'Agente Avanzado', 'Agente']
            queryset = queryset.filter(
                id_agente__id_area=agente.id_area,
                id_agente__agenterol__id_rol__nombre__in=roles_permitidos
            )
        elif rol_nombre == 'Agente Avanzado':
            # Agente Avanzado ve licencias de Agente Avanzado y Agente de su área
            from personas.models import Rol
            roles_permitidos = ['Agente Avanzado', 'Agente']
            queryset = queryset.filter(
                id_agente__id_area=agente.id_area,
                id_agente__agenterol__id_rol__nombre__in=roles_permitidos
            )
        else:
            # Agente solo ve sus propias licencias
            queryset = queryset.filter(id_agente=agente)
        
        # Aplicar filtros adicionales
        if fecha_desde:
            queryset = queryset.filter(fecha_desde__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_hasta__lte=fecha_hasta)
        
        if area_id and rol.id_rol.nombre == 'Administrador':
            queryset = queryset.filter(id_agente__id_area_id=area_id)
        
        if estado and estado != 'todas':
            queryset = queryset.filter(estado=estado)
        
        if tipo_licencia_id:
            queryset = queryset.filter(id_tipo_licencia_id=tipo_licencia_id)
        
        # Ordenar por fecha de creación descendente
        queryset = queryset.order_by('-id_licencia')
        
        serializer = LicenciaSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except Agente.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en listar_licencias: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def crear_licencia_impl(request):
    """
    Crear nueva licencia (solicitud o asignación).
    """
    try:
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente_solicitante = Agente.objects.get(id_agente=agente_id)
        rol_solicitante = agente_solicitante.agenterol_set.first()
        
        if not rol_solicitante:
            return Response({
                'success': False,
                'message': 'Usuario sin rol asignado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validar que el agente de la licencia exista
        id_agente_licencia = request.data.get('id_agente')
        if not id_agente_licencia:
            return Response({
                'success': False,
                'message': 'Debe especificar el agente para la licencia'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        agente_licencia = Agente.objects.get(id_agente=id_agente_licencia)
        
        # Validar permisos según jerarquía
        if rol_solicitante.id_rol.nombre == 'Administrador':
            # Administrador puede crear licencias para cualquiera
            pass
        elif rol_solicitante.id_rol.nombre in ['Director', 'Jefatura']:
            # Director y Jefatura solo en su área
            if agente_licencia.id_area != agente_solicitante.id_area:
                return Response({
                    'success': False,
                    'message': 'No tiene permisos para crear licencias en esta área'
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            # Agente/Agente Avanzado solo para sí mismos
            if agente_licencia.id_agente != agente_solicitante.id_agente:
                return Response({
                    'success': False,
                    'message': 'Solo puede crear licencias para usted mismo'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Validar fechas
        fecha_desde = request.data.get('fecha_desde')
        fecha_hasta = request.data.get('fecha_hasta')
        
        if not fecha_desde or not fecha_hasta:
            return Response({
                'success': False,
                'message': 'Debe especificar fechas de inicio y fin'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        if fecha_desde_obj > fecha_hasta_obj:
            return Response({
                'success': False,
                'message': 'La fecha de inicio no puede ser posterior a la fecha de fin'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar solapamientos
        licencias_existentes = Licencia.objects.filter(
            id_agente=agente_licencia,
            estado__in=['pendiente', 'aprobada']
        ).filter(
            Q(fecha_desde__lte=fecha_hasta_obj, fecha_hasta__gte=fecha_desde_obj)
        )
        
        if licencias_existentes.exists():
            return Response({
                'success': False,
                'message': 'Ya existe una licencia en ese período'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determinar estado inicial
        estado_inicial = request.data.get('estado', 'pendiente')
        
        # Solo jefatura superior puede crear licencias aprobadas directamente
        if estado_inicial == 'aprobada' and rol_solicitante.id_rol.nombre not in ['Administrador', 'Director', 'Jefatura']:
            estado_inicial = 'pendiente'
        
        # Crear la licencia
        licencia_data = {
            'id_agente': agente_licencia.id_agente,
            'id_tipo_licencia': request.data.get('id_tipo_licencia'),
            'fecha_desde': fecha_desde_obj,
            'fecha_hasta': fecha_hasta_obj,
            'estado': estado_inicial,
            'observaciones': request.data.get('observaciones', ''),
            'justificacion': request.data.get('justificacion', ''),
            'solicitada_por': agente_solicitante.id_agente
        }
        
        if estado_inicial == 'aprobada':
            licencia_data['aprobada_por'] = agente_solicitante.id_agente
            licencia_data['fecha_aprobacion'] = timezone.now().date()
        
        serializer = LicenciaSerializer(data=licencia_data)
        if serializer.is_valid():
            licencia = serializer.save()
            
            # Auditoría: Registrar creación de licencia
            valor_nuevo = {
                'agente_licencia': f"{agente_licencia.nombre} {agente_licencia.apellido}",
                'agente_dni': agente_licencia.dni,
                'tipo_licencia': licencia.id_tipo_licencia.descripcion if licencia.id_tipo_licencia else 'N/A',
                'fecha_desde': str(fecha_desde_obj),
                'fecha_hasta': str(fecha_hasta_obj),
                'estado': estado_inicial,
                'observaciones': licencia.observaciones,
                'justificacion': licencia.justificacion,
                'solicitada_por': f"{agente_solicitante.nombre} {agente_solicitante.apellido}",
                'es_auto_aprobada': estado_inicial == 'aprobada',
                'area': agente_licencia.id_area.nombre if agente_licencia.id_area else None
            }
            crear_auditoria_licencia(
                agente_id, 
                'CREAR_LICENCIA', 
                licencia.id_licencia, 
                None, 
                valor_nuevo
            )
            
            return Response({
                'success': True,
                'message': f'Licencia {"asignada" if estado_inicial == "aprobada" else "solicitada"} correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Agente.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Agente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en crear_licencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
def aprobar_licencia(request, licencia_id):
    """
    Aprobar una licencia pendiente.
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
        
        if not rol:
            return Response({
                'success': False,
                'message': 'Usuario sin rol asignado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        licencia = Licencia.objects.select_related('id_agente').get(id_licencia=licencia_id)
        
        # Auditoría: Capturar estado previo
        valor_previo = {
            'estado': licencia.estado,
            'aprobada_por': f"{licencia.aprobada_por.nombre} {licencia.aprobada_por.apellido}" if licencia.aprobada_por else None,
            'fecha_aprobacion': str(licencia.fecha_aprobacion) if licencia.fecha_aprobacion else None,
            'observaciones_aprobacion': licencia.observaciones_aprobacion,
            'agente_licencia': f"{licencia.id_agente.nombre} {licencia.id_agente.apellido}",
            'agente_dni': licencia.id_agente.dni,
            'fecha_desde': str(licencia.fecha_desde),
            'fecha_hasta': str(licencia.fecha_hasta)
        }
        
        # Validar que esté pendiente
        if licencia.estado != 'pendiente':
            return Response({
                'success': False,
                'message': 'Solo se pueden aprobar licencias pendientes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar permisos de aprobación según jerarquía
        puede_aprobar = False
        
        if rol.id_rol.nombre == 'Administrador':
            puede_aprobar = True
        elif rol.id_rol.nombre == 'Director':
            # Director puede aprobar todo en su área
            puede_aprobar = (licencia.id_agente.id_area == agente.id_area)
        elif rol.id_rol.nombre == 'Jefatura':
            # Jefatura puede aprobar agentes y agentes avanzados de su área
            agente_licencia_rol = licencia.id_agente.agenterol_set.first()
            puede_aprobar = (
                licencia.id_agente.id_area == agente.id_area and
                agente_licencia_rol and
                agente_licencia_rol.id_rol.nombre in ['Agente', 'Agente Avanzado']
            )
        
        if not puede_aprobar:
            return Response({
                'success': False,
                'message': 'No tiene permisos para aprobar esta licencia'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Actualizar licencia
        observaciones_aprobacion = request.data.get('observaciones', '')
        licencia.estado = 'aprobada'
        licencia.aprobada_por = agente
        licencia.fecha_aprobacion = timezone.now().date()
        licencia.observaciones_aprobacion = observaciones_aprobacion
        licencia.save()
        
        # Auditoría: Registrar aprobación de licencia
        valor_nuevo = {
            'estado': 'aprobada',
            'aprobada_por': f"{agente.nombre} {agente.apellido}",
            'fecha_aprobacion': str(licencia.fecha_aprobacion),
            'observaciones_aprobacion': observaciones_aprobacion,
            'agente_licencia': f"{licencia.id_agente.nombre} {licencia.id_agente.apellido}",
            'agente_dni': licencia.id_agente.dni,
            'fecha_desde': str(licencia.fecha_desde),
            'fecha_hasta': str(licencia.fecha_hasta),
            'tipo_licencia': licencia.id_tipo_licencia.descripcion if licencia.id_tipo_licencia else 'N/A'
        }
        crear_auditoria_licencia(
            agente_id, 
            'APROBAR_LICENCIA', 
            licencia.id_licencia, 
            valor_previo, 
            valor_nuevo
        )
        
        serializer = LicenciaSerializer(licencia)
        
        return Response({
            'success': True,
            'message': 'Licencia aprobada correctamente',
            'data': serializer.data
        })
    
    except Licencia.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Licencia no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en aprobar_licencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
def rechazar_licencia(request, licencia_id):
    """
    Rechazar una licencia pendiente.
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
        
        if not rol:
            return Response({
                'success': False,
                'message': 'Usuario sin rol asignado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        licencia = Licencia.objects.select_related('id_agente').get(id_licencia=licencia_id)
        
        # Auditoría: Capturar estado previo
        valor_previo_rechazo = {
            'estado': licencia.estado,
            'rechazada_por': f"{licencia.rechazada_por.nombre} {licencia.rechazada_por.apellido}" if licencia.rechazada_por else None,
            'fecha_rechazo': str(licencia.fecha_rechazo) if licencia.fecha_rechazo else None,
            'motivo_rechazo': licencia.motivo_rechazo,
            'agente_licencia': f"{licencia.id_agente.nombre} {licencia.id_agente.apellido}",
            'agente_dni': licencia.id_agente.dni,
            'fecha_desde': str(licencia.fecha_desde),
            'fecha_hasta': str(licencia.fecha_hasta)
        }
        
        # Validar que esté pendiente
        if licencia.estado != 'pendiente':
            return Response({
                'success': False,
                'message': 'Solo se pueden rechazar licencias pendientes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar permisos (misma lógica que aprobar)
        puede_rechazar = False
        
        if rol.id_rol.nombre == 'Administrador':
            puede_rechazar = True
        elif rol.id_rol.nombre == 'Director':
            puede_rechazar = (licencia.id_agente.id_area == agente.id_area)
        elif rol.id_rol.nombre == 'Jefatura':
            agente_licencia_rol = licencia.id_agente.agenterol_set.first()
            puede_rechazar = (
                licencia.id_agente.id_area == agente.id_area and
                agente_licencia_rol and
                agente_licencia_rol.id_rol.nombre in ['Agente', 'Agente Avanzado']
            )
        
        if not puede_rechazar:
            return Response({
                'success': False,
                'message': 'No tiene permisos para rechazar esta licencia'
            }, status=status.HTTP_403_FORBIDDEN)
        
        motivo_rechazo = request.data.get('motivo')
        if not motivo_rechazo:
            return Response({
                'success': False,
                'message': 'Debe especificar el motivo del rechazo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar licencia
        licencia.estado = 'rechazada'
        licencia.rechazada_por = agente
        licencia.fecha_rechazo = timezone.now().date()
        licencia.motivo_rechazo = motivo_rechazo
        licencia.save()
        
        # Auditoría: Registrar rechazo de licencia
        valor_nuevo_rechazo = {
            'estado': 'rechazada',
            'rechazada_por': f"{agente.nombre} {agente.apellido}",
            'fecha_rechazo': str(licencia.fecha_rechazo),
            'motivo_rechazo': motivo_rechazo,
            'agente_licencia': f"{licencia.id_agente.nombre} {licencia.id_agente.apellido}",
            'agente_dni': licencia.id_agente.dni,
            'fecha_desde': str(licencia.fecha_desde),
            'fecha_hasta': str(licencia.fecha_hasta),
            'tipo_licencia': licencia.id_tipo_licencia.descripcion if licencia.id_tipo_licencia else 'N/A'
        }
        crear_auditoria_licencia(
            agente_id, 
            'RECHAZAR_LICENCIA', 
            licencia.id_licencia, 
            valor_previo_rechazo, 
            valor_nuevo_rechazo
        )
        
        serializer = LicenciaSerializer(licencia)
        
        return Response({
            'success': True,
            'message': 'Licencia rechazada',
            'data': serializer.data
        })
    
    except Licencia.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Licencia no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en rechazar_licencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
def eliminar_licencia(request, licencia_id):
    """
    Eliminar una licencia (solo administradores).
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
        
        if not rol or rol.id_rol.nombre != 'Administrador':
            return Response({
                'success': False,
                'message': 'Solo los administradores pueden eliminar licencias'
            }, status=status.HTTP_403_FORBIDDEN)
        
        licencia = Licencia.objects.get(id_licencia=licencia_id)
        
        # Auditoría: Capturar datos completos antes de eliminar
        valor_previo_eliminacion = {
            'id_licencia': licencia.id_licencia,
            'agente_licencia': f"{licencia.id_agente.nombre} {licencia.id_agente.apellido}",
            'agente_dni': licencia.id_agente.dni,
            'tipo_licencia': licencia.id_tipo_licencia.descripcion if licencia.id_tipo_licencia else 'N/A',
            'fecha_desde': str(licencia.fecha_desde),
            'fecha_hasta': str(licencia.fecha_hasta),
            'estado': licencia.estado,
            'observaciones': licencia.observaciones,
            'justificacion': licencia.justificacion,
            'solicitada_por': f"{licencia.solicitada_por.nombre} {licencia.solicitada_por.apellido}" if licencia.solicitada_por else None,
            'aprobada_por': f"{licencia.aprobada_por.nombre} {licencia.aprobada_por.apellido}" if licencia.aprobada_por else None,
            'rechazada_por': f"{licencia.rechazada_por.nombre} {licencia.rechazada_por.apellido}" if licencia.rechazada_por else None,
            'fecha_aprobacion': str(licencia.fecha_aprobacion) if licencia.fecha_aprobacion else None,
            'fecha_rechazo': str(licencia.fecha_rechazo) if licencia.fecha_rechazo else None,
            'eliminada_por': f"{agente.nombre} {agente.apellido}"
        }
        
        # Guardar información para el log
        licencia_info = f"ID: {licencia.id_licencia}, Agente: {licencia.id_agente.nombre} {licencia.id_agente.apellido}, Estado: {licencia.estado}"
        licencia_id_para_auditoria = licencia.id_licencia
        
        # Eliminar la licencia
        licencia.delete()
        
        # Auditoría: Registrar eliminación de licencia
        crear_auditoria_licencia(
            agente_id, 
            'ELIMINAR_LICENCIA', 
            licencia_id_para_auditoria, 
            valor_previo_eliminacion, 
            None
        )
        
        logger.info(f'Licencia eliminada por administrador {agente.nombre} {agente.apellido}: {licencia_info}')
        
        return Response({
            'success': True,
            'message': 'Licencia eliminada correctamente'
        }, status=status.HTTP_200_OK)
    
    except Licencia.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Licencia no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error en eliminar_licencia: {str(e)}')
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Requiere autenticación
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
        
        # Auditoría: Capturar estado previo
        valor_previo = {
            'hora_entrada': str(asistencia.hora_entrada) if asistencia.hora_entrada else None,
            'hora_salida': str(asistencia.hora_salida) if asistencia.hora_salida else None,
            'horas_efectivas': asistencia.horas_efectivas,
            'observaciones': asistencia.observaciones,
            'marcacion_entrada_automatica': asistencia.marcacion_entrada_automatica,
            'marcacion_salida_automatica': asistencia.marcacion_salida_automatica,
            'agente_nombre': f"{asistencia.id_agente.nombre} {asistencia.id_agente.apellido}",
            'agente_dni': asistencia.id_agente.dni,
            'fecha': str(asistencia.fecha)
        }
        
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
        
        # Auditoría: Registrar marcado como ausente
        valor_nuevo = {
            'hora_entrada': None,
            'hora_salida': None,
            'horas_efectivas': None,
            'observaciones': asistencia.observaciones,
            'marcacion_entrada_automatica': False,
            'marcacion_salida_automatica': False,
            'agente_nombre': f"{asistencia.id_agente.nombre} {asistencia.id_agente.apellido}",
            'agente_dni': asistencia.id_agente.dni,
            'fecha': str(asistencia.fecha),
            'motivo_ausencia': observacion,
            'marcado_por': f"{agente.nombre} {agente.apellido}"
        }
        crear_auditoria_asistencia(
            agente_id, 
            'MARCAR_AUSENTE', 
            asistencia.id_asistencia, 
            valor_previo, 
            valor_nuevo
        )
        
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
