from rest_framework import status, serializers
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
from drf_spectacular.utils import extend_schema, OpenApiExample

class UserSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    cuil = serializers.CharField(allow_blank=True, allow_null=True)
    rol_principal = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(read_only=True)
    nombre_completo = serializers.SerializerMethodField()

    def get_rol_principal(self, obj):
        """
        Obtiene el nombre del primer rol asignado al usuario.
        """
        # Usamos 'select_related' para optimizar la consulta a la base de datos.
        asignacion = AgenteRol.objects.filter(usuario=obj).select_related('rol').first()
        if asignacion and asignacion.rol:
            return asignacion.rol.nombre
        return "Sin rol asignado"

    def get_roles(self, obj):
        """
        Obtiene una lista de todos los roles asignados al usuario.
        """
        asignaciones = AgenteRol.objects.filter(usuario=obj).select_related('rol')
        return [asignacion.rol.nombre for asignacion in asignaciones if asignacion.rol]

    def get_nombre_completo(self, obj):
        """Obtiene el nombre completo del usuario."""
        return obj.get_full_name() or obj.username


class LoginRequestSerializer(serializers.Serializer):
    cuil = serializers.CharField(help_text="CUIL sin guiones (11 dígitos)")
    password = serializers.CharField()


class LoginSuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    requires_password_change = serializers.BooleanField()
    password_reset_reason = serializers.CharField(allow_null=True, allow_blank=True)
    user = UserSummarySerializer()


class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()

@extend_schema(
    request=LoginRequestSerializer,
    responses={
        200: LoginSuccessResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Login OK',
            request_only=True,
            value={'cuil': '20123456789', 'password': 'Secreta123'},
        )
    ],
    description='Inicia sesión por CUIL y contraseña. Crea cookie de sesión para usar en el resto de la API.'
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint para login con CUIL y contraseña.
    Utiliza el backend de autenticación personalizado.
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    try:
        data = json.loads(request.body)
        cuil = data.get('cuil', '')
        password = data.get('password', '')

        if not cuil or not password:
            return Response({
                'success': False,
                'message': 'CUIL y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Usar el sistema de autenticación de Django, que a su vez usará
        # nuestro CUILAuthenticationBackend configurado en settings.py
        user = authenticate(request, username=cuil, password=password)

        if user is not None:
            # El usuario es válido, iniciar sesión
            login(request, user)
            
            # Serializar los datos del usuario para la respuesta
            try:
                user_data = UserSummarySerializer(user).data
            except Exception as e:
                # Si la serialización falla, es un error del servidor
                raise e

            return Response({
                'success': True,
                'message': 'Login exitoso',
                'user': user_data
            }, status=status.HTTP_200_OK)
        else:
            # La autenticación falló
            return Response({
                'success': False,
                'message': 'CUIL o contraseña incorrectos.'
            }, status=status.HTTP_401_UNAUTHORIZED)

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
        return Response({
            'authenticated': True,
            # Usamos el mismo serializador que en el login para consistencia
            'user': UserSummarySerializer(request.user).data
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
                # Lógica de extract_dni_from_cuil directamente aquí
                cuil_limpio = ''.join(filter(str.isdigit, str(request.user.cuil)))
                dni = cuil_limpio[2:10] if len(cuil_limpio) == 11 else ''
                if new_password == dni:
                    return Response({
                        'success': False,
                        'message': 'La nueva contraseña no puede ser igual a tu DNI'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                request.user.set_password(new_password)
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
 #           'user': build_user_response_data(request.user, include_password_info=False)
            'user': UserSummarySerializer(request.user).data
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
        cuil_raw = data.get('cuil', '').strip()
        
        if not cuil_raw:
            return Response({
                'success': False,
                'message': 'CUIL es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Limpiar CUIL
        # Lógica de clean_cuil directamente aquí
        cuil_clean = ''.join(filter(str.isdigit, str(cuil_raw)))
        
        if len(cuil_clean) != 11:
            return Response({
                'success': False,
                'message': 'CUIL debe tener 11 dígitos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Buscar usuario por CUIL
            usuario = Usuario.objects.get(cuil=cuil_clean)
            
            # Extraer DNI del CUIL
            # Lógica de extract_dni_from_cuil directamente aquí
            dni = cuil_clean[2:10] if len(cuil_clean) == 11 else ''
            
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
            
            return Response({
                'success': True,
                'message': 'Contraseña restablecida exitosamente',
                # Lógica de mask_email directamente aquí
                'email': (f"{usuario.email.split('@')[0][:2]}***@{usuario.email.split('@')[1]}" 
                          if '@' in usuario.email 
                          else "***@***.***"),
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
