"""
Vistas de autenticación para el sistema GIGA
Compatible con Database First y nueva estructura de BD
"""
import json
import secrets
import string
from datetime import datetime
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction, connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Agente, AgenteRol, Rol, Area
from auditoria.models import Auditoria
import logging

# RBAC Permissions
from common.permissions import IsAuthenticatedGIGA

logger = logging.getLogger(__name__)

def registrar_auditoria(agente_id, accion, detalle=""):
    """Registrar acción en auditoría"""
    try:
        # Crear registro de auditoría básico
        import json as json_module
        with connection.cursor() as cursor:
            valor_json = json_module.dumps({'detalle': detalle}) if detalle else None
            cursor.execute(
                """
                INSERT INTO auditoria (id_agente, accion, nombre_tabla, pk_afectada, creado_en, valor_nuevo)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [agente_id, accion, 'agente', agente_id or 0, datetime.now(), valor_json]
            )
    except Exception as e:
        logger.error(f"Error registrando auditoría: {e}")

def clean_cuil(cuil_input):
    """Limpia un CUIL removiendo guiones, espacios y caracteres no numéricos"""
    if not cuil_input:
        return ""
    return ''.join(filter(str.isdigit, str(cuil_input)))

def generate_password(length=8):
    """Generar contraseña aleatoria"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint para login con DNI/CUIL y contraseña.
    Valida contra la nueva base de datos y devuelve datos del agente.
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        data = request.data
        cuil_dni = data.get('cuil', '')  # Puede ser DNI o CUIL
        password = data.get('password', '')

        if not cuil_dni or not password:
            return Response({
                'success': False,
                'message': 'DNI/CUIL y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Limpiar entrada (remover espacios, guiones, etc.)
        clean_input = clean_cuil(cuil_dni)
        
        agente = None
        
        # Intentar buscar por CUIL primero (si tiene 11 dígitos)
        if len(clean_input) == 11:
            try:
                agente = Agente.objects.get(cuil=clean_input, activo=True)
            except Agente.DoesNotExist:
                pass
        
        # Si no se encontró por CUIL, intentar por DNI
        if not agente:
            # Si tiene 11 dígitos, extraer DNI del CUIL (posición 2-9)
            if len(clean_input) == 11:
                dni_from_cuil = clean_input[2:10]
                try:
                    agente = Agente.objects.get(dni=dni_from_cuil, activo=True)
                except Agente.DoesNotExist:
                    pass
            # Si tiene 8 dígitos, es DNI directo
            elif len(clean_input) == 8:
                try:
                    agente = Agente.objects.get(dni=clean_input, activo=True)
                except Agente.DoesNotExist:
                    pass
        
        # Si no se encontró el agente
        if not agente:
            registrar_auditoria(None, "LOGIN_FALLIDO", f"Usuario no encontrado: {cuil_dni}")
            return Response({
                'success': False,
                'message': 'DNI/CUIL o contraseña incorrectos'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Verificar contraseña
        if not agente.check_password(password):
            registrar_auditoria(agente.id_agente, "LOGIN_FALLIDO", "Contraseña incorrecta")
            return Response({
                'success': False,
                'message': 'CUIL o contraseña incorrectos'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Obtener roles del agente
        agente_roles = AgenteRol.objects.filter(id_agente=agente).select_related('id_rol')
        roles = []
        for agente_rol in agente_roles:
            roles.append({
                'id': agente_rol.id_rol.id_rol,
                'nombre': agente_rol.id_rol.nombre,
                'descripcion': agente_rol.id_rol.descripcion
            })

        # Obtener área
        area_info = None
        if agente.id_area:
            area_info = {
                'id': agente.id_area.id_area,
                'nombre': agente.id_area.nombre
            }

        # Verificar si necesita cambiar contraseña (si es igual al DNI)
        requires_password_change = password == agente.dni
        password_reset_reason = ""
        if requires_password_change:
            password_reset_reason = "La contraseña es igual al DNI y debe ser cambiada por seguridad"

        # Preparar respuesta del usuario
        user_data = {
            'id': agente.id_agente,
            'legajo': agente.legajo,
            'nombre': agente.nombre,
            'apellido': agente.apellido,
            'email': agente.email,
            'dni': agente.dni,
            'cuil': agente.cuil,
            'telefono': agente.telefono,
            'roles': roles,
            'area': area_info,
            'username': agente.username,
            'nombre_completo': f"{agente.nombre} {agente.apellido}",
            'first_name': agente.nombre,
            'last_name': agente.apellido,
            'fecha_nacimiento': agente.fecha_nacimiento.isoformat() if agente.fecha_nacimiento else None,
            'direccion': agente.direccion,
            'activo': agente.activo,
            'horario_entrada': agente.horario_entrada.strftime('%H:%M') if agente.horario_entrada else None,
            'horario_salida': agente.horario_salida.strftime('%H:%M') if agente.horario_salida else None
        }

        # Guardar en sesión (simulación de sesión para compatibilidad)
        request.session['user_id'] = agente.id_agente
        request.session['is_authenticated'] = True

        # Registrar login exitoso
        registrar_auditoria(agente.id_agente, "LOGIN_EXITOSO", f"Login desde IP: {request.META.get('REMOTE_ADDR', 'unknown')}")

        return Response({
            'success': True,
            'message': 'Login exitoso',
            'user': user_data,
            'requires_password_change': requires_password_change,
            'password_reset_reason': password_reset_reason
        })

    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    API endpoint para logout
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        user_id = request.session.get('user_id')
        if user_id:
            registrar_auditoria(user_id, "LOGOUT", f"Logout desde IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
        
        # Limpiar sesión
        request.session.flush()
        
        return Response({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        })
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return Response({
            'success': False,
            'message': 'Error al cerrar sesión'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'OPTIONS'])
@permission_classes([IsAuthenticatedGIGA])
def check_session(request):
    """
    Verificar si el usuario tiene una sesión activa
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        user_id = request.session.get('user_id')
        is_authenticated = request.session.get('is_authenticated', False)

        if not user_id or not is_authenticated:
            return Response({
                'authenticated': False,
                'message': 'No hay sesión activa'
            })

        # Verificar que el agente aún existe y está activo
        try:
            agente = Agente.objects.get(id_agente=user_id, activo=True)
        except Agente.DoesNotExist:
            request.session.flush()
            return Response({
                'authenticated': False,
                'message': 'Usuario no encontrado o inactivo'
            })

        # Obtener roles actualizados
        agente_roles = AgenteRol.objects.filter(id_agente=agente).select_related('id_rol')
        roles = []
        for agente_rol in agente_roles:
            roles.append({
                'id': agente_rol.id_rol.id_rol,
                'nombre': agente_rol.id_rol.nombre,
                'descripcion': agente_rol.id_rol.descripcion
            })

        # Obtener área
        area_info = None
        if agente.id_area:
            area_info = {
                'id': agente.id_area.id_area,
                'nombre': agente.id_area.nombre
            }

        # Verificar si requiere cambio de contraseña (mismo chequeo que en login)
        requires_password_change = False
        password_reset_reason = None

        # Verificar si la contraseña actual es igual al DNI
        if agente.check_password(agente.dni):
            requires_password_change = True
            password_reset_reason = "La contraseña es igual al DNI y debe ser cambiada por seguridad"

        user_data = {
            'id': agente.id_agente,
            'legajo': agente.legajo,
            'nombre': agente.nombre,
            'apellido': agente.apellido,
            'email': agente.email,
            'dni': agente.dni,
            'cuil': agente.cuil,
            'telefono': agente.telefono,
            'roles': roles,
            'area': area_info,
            'username': agente.username,
            'nombre_completo': f"{agente.nombre} {agente.apellido}",
            'first_name': agente.nombre,
            'last_name': agente.apellido,
            'fecha_nacimiento': agente.fecha_nacimiento.isoformat() if agente.fecha_nacimiento else None,
            'direccion': agente.direccion,
            'activo': agente.activo,
            'horario_entrada': agente.horario_entrada.strftime('%H:%M') if agente.horario_entrada else None,
            'horario_salida': agente.horario_salida.strftime('%H:%M') if agente.horario_salida else None
        }

        return Response({
            'authenticated': True,
            'user': user_data,
            'requires_password_change': requires_password_change,
            'password_reset_reason': password_reset_reason
        })

    except Exception as e:
        logger.error(f"Error verificando sesión: {e}")
        return Response({
            'authenticated': False,
            'message': 'Error verificando sesión'
        })

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def recover_password(request):
    """
    Recuperar contraseña enviando nueva contraseña al email
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        data = request.data
        cuil = data.get('cuil', '')

        if not cuil:
            return Response({
                'success': False,
                'message': 'CUIL es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Limpiar CUIL y extraer DNI
        clean_cuil_value = clean_cuil(cuil)
        if len(clean_cuil_value) == 11:
            dni = clean_cuil_value[2:10]
        else:
            return Response({
                'success': False,
                'message': 'CUIL debe tener 11 dígitos'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            agente = Agente.objects.get(dni=dni, activo=True)
        except Agente.DoesNotExist:
            # Por seguridad, no revelamos si el usuario existe
            registrar_auditoria(None, "RECUPERACION_FALLIDA", f"CUIL no encontrado: {cuil}")
            return Response({
                'success': True,
                'message': 'Si el CUIL existe, recibirá un email con la nueva contraseña'
            })

        # Resetear contraseña a DNI
        nueva_password = agente.dni
        agente.set_password(nueva_password)
        agente.save()

        # Registrar en auditoría
        registrar_auditoria(
            agente.id_agente, 
            "RECUPERACION_PASSWORD", 
            f"Contraseña reseteada por solicitud del usuario. IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
        )

        # Enviar email
        try:
            send_mail(
                subject='GIGA - Contraseña Restablecida',
                message=f"""
Estimado/a {agente.nombre} {agente.apellido},

Su contraseña ha sido restablecida exitosamente en el sistema GIGA.

Su nueva contraseña temporal es su DNI: {agente.dni}

Por razones de seguridad, será necesario que cambie esta contraseña en su primer inicio de sesión.

Para ingresar al sistema:
1. Vaya a la página de login
2. Ingrese su CUIL: {agente.cuil}
3. Ingrese su nueva contraseña temporal: {agente.dni}
4. El sistema le solicitará cambiar la contraseña

Si usted no solicitó este cambio, por favor contacte al administrador del sistema inmediatamente.

Saludos,
Sistema GIGA - Protección Civil
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agente.email],
            )
            email_sent = True
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            email_sent = False

        return Response({
            'success': True,
            'message': 'Contraseña restablecida. Revise su email para obtener la nueva contraseña.',
            'email_sent': email_sent
        })

    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error en recuperación de contraseña: {e}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'OPTIONS'])
@permission_classes([IsAuthenticatedGIGA])
def update_email(request):
    """
    Actualizar email del usuario autenticado
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        new_email = data.get('new_email', '')
        current_password = data.get('current_password', '')

        if not all([new_email, current_password]):
            return Response({
                'success': False,
                'message': 'Email y contraseña actual son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar formato de email
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', new_email):
            return Response({
                'success': False,
                'message': 'Formato de email inválido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            agente = Agente.objects.get(id_agente=user_id, activo=True)
        except Agente.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar contraseña actual
        if not agente.check_password(current_password):
            registrar_auditoria(agente.id_agente, "CAMBIO_EMAIL_FALLIDO", "Contraseña actual incorrecta")
            return Response({
                'success': False,
                'message': 'Contraseña actual incorrecta'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el email no esté en uso por otro usuario
        if Agente.objects.filter(email=new_email).exclude(id_agente=user_id).exists():
            return Response({
                'success': False,
                'message': 'Este email ya está en uso por otro usuario'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar email
        old_email = agente.email
        agente.email = new_email
        agente.save()

        # Registrar en auditoría
        registrar_auditoria(
            agente.id_agente, 
            "CAMBIO_EMAIL_EXITOSO", 
            f"Email cambiado de {old_email} a {new_email}. IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
        )

        return Response({
            'success': True,
            'message': 'Email actualizado exitosamente'
        })

    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error actualizando email: {e}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'OPTIONS'])
@permission_classes([IsAuthenticatedGIGA])  # Requiere sesión válida
def change_password(request):
    """
    Cambiar contraseña del usuario autenticado
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if not all([current_password, new_password, confirm_password]):
            return Response({
                'success': False,
                'message': 'Todos los campos son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
            return Response({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            agente = Agente.objects.get(id_agente=user_id, activo=True)
        except Agente.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar contraseña actual
        if not agente.check_password(current_password):
            registrar_auditoria(agente.id_agente, "CAMBIO_PASSWORD_FALLIDO", "Contraseña actual incorrecta")
            return Response({
                'success': False,
                'message': 'Contraseña actual incorrecta'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que la nueva contraseña no sea igual al DNI
        if new_password == agente.dni:
            return Response({
                'success': False,
                'message': 'La nueva contraseña no puede ser igual a su DNI'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar contraseña
        agente.set_password(new_password)
        agente.save()

        # Registrar en auditoría
        registrar_auditoria(
            agente.id_agente, 
            "CAMBIO_PASSWORD_EXITOSO", 
            f"Contraseña cambiada por el usuario. IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
        )

        # Enviar email de notificación
        try:
            send_mail(
                subject='GIGA - Contraseña Actualizada',
                message=f"""
Estimado/a {agente.nombre} {agente.apellido},

Le informamos que su contraseña ha sido actualizada exitosamente en el sistema GIGA.

Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Si usted no realizó este cambio, por favor contacte al administrador del sistema inmediatamente.

Saludos,
Sistema GIGA - Protección Civil
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agente.email],
            )
        except Exception as e:
            logger.error(f"Error enviando email de confirmación: {e}")

        return Response({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        })

    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {e}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'OPTIONS'])
def update_profile(request):
    """
    Obtener perfil actualizado del usuario (para verificar cambios de rol)
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            agente = Agente.objects.get(id_agente=user_id, activo=True)
        except Agente.DoesNotExist:
            request.session.flush()
            return Response({
                'success': False,
                'message': 'Usuario no encontrado o inactivo'
            }, status=status.HTTP_404_NOT_FOUND)

        # Obtener roles actualizados
        agente_roles = AgenteRol.objects.filter(id_agente=agente).select_related('id_rol')
        roles = []
        for agente_rol in agente_roles:
            roles.append({
                'id': agente_rol.id_rol.id_rol,
                'nombre': agente_rol.id_rol.nombre,
                'descripcion': agente_rol.id_rol.descripcion
            })

        # Obtener área
        area_info = None
        if agente.id_area:
            area_info = {
                'id': agente.id_area.id_area,
                'nombre': agente.id_area.nombre
            }

        user_data = {
            'id': agente.id_agente,
            'legajo': agente.legajo,
            'nombre': agente.nombre,
            'apellido': agente.apellido,
            'email': agente.email,
            'dni': agente.dni,
            'cuil': agente.cuil,
            'telefono': agente.telefono,
            'roles': roles,
            'area': area_info,
            'username': agente.username,
            'nombre_completo': f"{agente.nombre} {agente.apellido}",
            'first_name': agente.nombre,
            'last_name': agente.apellido,
            'fecha_nacimiento': agente.fecha_nacimiento.isoformat() if agente.fecha_nacimiento else None,
            'direccion': agente.direccion,
            'activo': agente.activo,
            'horario_entrada': agente.horario_entrada.strftime('%H:%M') if agente.horario_entrada else None,
            'horario_salida': agente.horario_salida.strftime('%H:%M') if agente.horario_salida else None
        }

        return Response({
            'success': True,
            'user': user_data
        })

    except Exception as e:
        logger.error(f"Error obteniendo perfil: {e}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)