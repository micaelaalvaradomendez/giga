from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from auditoria.models import Auditoria
from .models import Usuario, Agente, AgenteRol
import json

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint para login con CUIL y contraseña
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        data = json.loads(request.body)
        cuil = data.get('cuil', '').replace('-', '')  # Remover guiones del CUIL
        password = data.get('password', '')
        
        if not cuil or not password:
            return Response({
                'success': False,
                'message': 'CUIL y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario por CUIL
        try:
            usuario = Usuario.objects.get(cuil=cuil)
        except Usuario.DoesNotExist:
            return Response({
                'success': False,
                'message': 'CUIL no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar contraseña
        if not usuario.check_password(password):
            return Response({
                'success': False,
                'message': 'Contraseña incorrecta'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que el usuario esté activo
        if not usuario.is_active:
            return Response({
                'success': False,
                'message': 'Usuario inactivo'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Obtener información del agente y sus roles
        try:
            agente = Agente.objects.get(usuario=usuario)
            agente_roles = AgenteRol.objects.filter(usuario=usuario).select_related('rol')
            
            roles = [agente_rol.rol.nombre for agente_rol in agente_roles]
            rol_principal = roles[0] if roles else 'Sin rol'
            
        except Agente.DoesNotExist:
            rol_principal = 'Sin rol'
            roles = []
        
        # Verificar si la contraseña es igual al DNI (extraer DNI del CUIL)
        dni = cuil[2:10] if len(cuil) == 11 else ''
        password_equals_dni = (password == dni)
        
        # Verificar si necesita cambio obligatorio de contraseña
        requires_password_change = usuario.password_reset or password_equals_dni
        
        # Login exitoso - crear sesión
        # Especificar el backend de autenticación para evitar conflictos
        usuario.backend = 'personas.backends.CUILAuthenticationBackend'
        login(request, usuario)
        
        return Response({
            'success': True,
            'message': 'Login exitoso',
            'requires_password_change': requires_password_change,
            'password_reset_reason': 'Contraseña temporal por seguridad' if requires_password_change else None,
            'user': {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'cuil': usuario.cuil,
                'rol_principal': rol_principal,
                'roles': roles,
                'nombre_completo': f"{usuario.first_name} {usuario.last_name}",
                'password_reset': usuario.password_reset
            }
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    API endpoint para logout
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        from django.contrib.auth import logout
        logout(request)
        return Response({
            'success': True,
            'message': 'Logout exitoso'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al cerrar sesión: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'OPTIONS'])
@permission_classes([AllowAny])
def check_session(request):
    """
    Verificar si el usuario tiene una sesión activa
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    if request.user.is_authenticated:
        try:
            agente = Agente.objects.get(usuario=request.user)
            agente_roles = AgenteRol.objects.filter(usuario=request.user).select_related('rol')
            
            roles = [agente_rol.rol.nombre for agente_rol in agente_roles]
            rol_principal = roles[0] if roles else 'Sin rol'
            
        except Agente.DoesNotExist:
            rol_principal = 'Sin rol'
            roles = []
        
        # Verificar si la contraseña es igual al DNI
        dni = request.user.cuil[2:10] if request.user.cuil and len(request.user.cuil) == 11 else ''
        requires_password_change = request.user.password_reset
        
        return Response({
            'authenticated': True,
            'requires_password_change': requires_password_change,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'cuil': request.user.cuil,
                'rol_principal': rol_principal,
                'roles': roles,
                'nombre_completo': f"{request.user.first_name} {request.user.last_name}",
                'password_reset': request.user.password_reset
            }
        })
    else:
        return Response({
            'authenticated': False
        })


@api_view(['POST', 'OPTIONS'])
def update_profile(request):
    """
    Actualizar email y/o contraseña del usuario autenticado
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    # Verificar que el usuario esté autenticado
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'message': 'Usuario no autenticado'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = json.loads(request.body)
        new_email = data.get('email', '').strip()
        new_password = data.get('password', '').strip()
        current_password = data.get('current_password', '').strip()
        
        # Verificar que se proporcione la contraseña actual
        if not current_password:
            return Response({
                'success': False,
                'message': 'Contraseña actual requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar la contraseña actual
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'Contraseña actual incorrecta'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que al menos se quiera cambiar algo
        if not new_email and not new_password:
            return Response({
                'success': False,
                'message': 'Debe proporcionar al menos email o contraseña nueva'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        changes_made = []
        email_changed = False
        password_changed = False
        old_email = request.user.email
        
        with transaction.atomic():
            # Cambiar email si se proporciona
            if new_email and new_email != request.user.email:
                # Verificar que el email no esté en uso
                if Usuario.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    return Response({
                        'success': False,
                        'message': 'El email ya está en uso por otro usuario'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                request.user.email = new_email
                changes_made.append('email')
                email_changed = True
                
                # Registrar en auditoría
                Auditoria.objects.create(
                    creado_por=request.user,
                    nombre_tabla='Usuario',
                    pk_afectada=str(request.user.id),
                    accion='update',
                    valor_previo={'email': old_email},
                    valor_nuevo={'email': new_email}
                )
            
            # Cambiar contraseña si se proporciona
            if new_password:
                # Validar longitud mínima de contraseña
                if len(new_password) < 6:
                    return Response({
                        'success': False,
                        'message': 'La contraseña debe tener al menos 6 caracteres'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Verificar que no use el DNI como contraseña
                dni = request.user.cuil[2:10] if request.user.cuil and len(request.user.cuil) == 11 else ''
                if new_password == dni:
                    return Response({
                        'success': False,
                        'message': 'La nueva contraseña no puede ser igual a tu DNI'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                request.user.set_password(new_password)
                request.user.password_reset = False  # Ya no requiere cambio obligatorio
                changes_made.append('contraseña')
                password_changed = True
                
                # Registrar en auditoría
                Auditoria.objects.create(
                    creado_por=request.user,
                    nombre_tabla='Usuario',
                    pk_afectada=str(request.user.id),
                    accion='update',
                    valor_previo={'password': 'password_changed'},
                    valor_nuevo={'password': 'password_updated'}
                )
            
            # Guardar cambios
            request.user.save()
        
        # Enviar notificaciones por email
        try:
            # Email por cambio de contraseña
            if password_changed:
                send_mail(
                    'Cambio de contraseña - Sistema GIGA',
                    f'Hola {request.user.first_name},\n\n'
                    'Tu contraseña ha sido actualizada exitosamente en el Sistema GIGA.\n\n'
                    'Si no realizaste este cambio, contacta al administrador inmediatamente.\n\n'
                    'Saludos,\nEquipo GIGA',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
            
            # Email por cambio de email
            if email_changed:
                # Email al email anterior
                send_mail(
                    'Cambio de email - Sistema GIGA',
                    f'Hola {request.user.first_name},\n\n'
                    f'Tu email en el Sistema GIGA ha sido cambiado de {old_email} a {new_email}.\n\n'
                    'Si no realizaste este cambio, contacta al administrador inmediatamente.\n\n'
                    'Saludos,\nEquipo GIGA',
                    settings.DEFAULT_FROM_EMAIL,
                    [old_email],
                    fail_silently=True,
                )
                
                # Email al email nuevo
                send_mail(
                    'Email actualizado - Sistema GIGA',
                    f'Hola {request.user.first_name},\n\n'
                    'Tu email ha sido actualizado exitosamente en el Sistema GIGA.\n\n'
                    'Ahora recibirás todas las notificaciones en esta dirección.\n\n'
                    'Saludos,\nEquipo GIGA',
                    settings.DEFAULT_FROM_EMAIL,
                    [new_email],
                    fail_silently=True,
                )
        
        except Exception as e:
            print(f"Error enviando emails de notificación: {str(e)}")
            # No fallar la operación por problemas de email
        
        return Response({
            'success': True,
            'message': f'Perfil actualizado exitosamente: {", ".join(changes_made)}',
            'changes': changes_made,
            'password_changed': password_changed,
            'email_changed': email_changed,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'cuil': request.user.cuil,
                'nombre_completo': f"{request.user.first_name} {request.user.last_name}"
            }
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def recover_password(request):
    """
    Recuperar contraseña enviando nueva contraseña al email
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        data = json.loads(request.body)
        cuil = data.get('cuil', '').strip()
        
        if not cuil:
            return Response({
                'success': False,
                'message': 'CUIL es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Limpiar CUIL (remover guiones, espacios, etc.)
        clean_cuil = ''.join(filter(str.isdigit, cuil))
        
        if len(clean_cuil) != 11:
            return Response({
                'success': False,
                'message': 'CUIL debe tener 11 dígitos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar usuario por CUIL
            usuario = Usuario.objects.get(cuil=clean_cuil)
            
            # Extraer DNI del CUIL (dígitos 3 al 10)
            dni = clean_cuil[2:10]
            
            with transaction.atomic():
                # Cambiar contraseña al DNI
                usuario.set_password(dni)
                usuario.password_reset = True
                usuario.save()
                
                # Registrar en auditoría
                Auditoria.objects.create(
                    creado_por=None,  # Operación automática del sistema
                    nombre_tabla='Usuario',
                    pk_afectada=str(usuario.id),
                    accion='update',
                    valor_previo={'password_reset': False},
                    valor_nuevo={'password_reset': True, 'action': 'password_recovery'}
                )
            
            # Enviar email de confirmación
            try:
                send_mail(
                    'Contraseña restablecida - Sistema GIGA',
                    f'Hola {usuario.first_name or usuario.username},\n\n'
                    'Tu contraseña ha sido restablecida exitosamente.\n\n'
                    f'Tu nueva contraseña temporal es: {dni}\n\n'
                    'Por razones de seguridad, deberás cambiar esta contraseña en tu primer inicio de sesión.\n\n'
                    'Si no solicitaste este cambio, contacta al administrador inmediatamente.\n\n'
                    'Saludos,\nEquipo GIGA',
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error enviando email de recuperación: {str(e)}")
                # No fallar la operación por problemas de email
            
            # Ocultar parcialmente el email para la respuesta
            email_parts = usuario.email.split('@')
            if len(email_parts) == 2:
                masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"
            else:
                masked_email = "***@***.***"
            
            return Response({
                'success': True,
                'message': 'Contraseña restablecida exitosamente',
                'email': masked_email,
                'user_found': True
            }, status=status.HTTP_200_OK)
            
        except Usuario.DoesNotExist:
            # No revelar si el usuario existe o no por seguridad
            return Response({
                'success': True,
                'message': 'Si el CUIL existe en el sistema, se enviará un email con la nueva contraseña',
                'email': '***@***.***',
                'user_found': False
            }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
