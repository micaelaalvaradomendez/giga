"""
Django settings for GIGA project.

Configurado para conectarse a PostgreSQL externo (contenedor) usando modelos no gestionados
siguiendo la estrategia de "Database First" para preservar la integridad de la BD existente.

Basado en Django 4.2.7 con arquitectura de contenedores separados:
- Backend Django (este contenedor)
- Base de datos PostgreSQL (contenedor bd/giga-postgres)  
- Frontend Svelte (contenedor front)
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Helper function for environment variables
def config(key, default=None, cast=None):
    """Simple config function to replace decouple temporarily"""
    value = os.environ.get(key, default)
    if cast and value is not None:
        if cast == bool:
            # Si el valor ya es booleano, devolverlo directamente
            if isinstance(value, bool):
                return value
            # Si es string, convertir
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
        return cast(value)
    return value

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-@06dt19af&dnhw3py_w!paj09bph#6e6f3%p5f@y_6rhr$)2km')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'django_filters',
    
    # Common utilities - RBAC System
    'common',
    
    # Local apps - GIGA System Apps
    'personas',
    'auditoria', 
    'guardias',
    'asistencia',
    'incidencias',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'giga.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'giga.wsgi.application'


# Database - PostgreSQL External Container
# Configuración para conectarse al contenedor giga-postgres
# Usando estrategia "Database First" con modelos no gestionados (managed = False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='giga'),
        'USER': config('DB_USER', default='giga_user'),
        'PASSWORD': config('DB_PASSWORD', default='giga2025'),
        'HOST': config('DB_HOST', default='giga-postgres'),  # Nombre del contenedor de BD
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
            'options': '-c search_path=public'
        },
        'CONN_MAX_AGE': 600,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization - Configurado para Argentina
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================================
# SESSION CONFIGURATION - Control de Sesiones
# ============================================================================

# Sesión NO PERSISTENTE: Se cierra al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Tiempo de expiración: 1 hora de inactividad
SESSION_COOKIE_AGE = 3600  # 1 hora en segundos

# Renovar cookie en cada request para mantener sesión activa
SESSION_SAVE_EVERY_REQUEST = True

# Nombre de la cookie de sesión
SESSION_COOKIE_NAME = 'sessionid'

# Cookie solo HTTPS en producción
SESSION_COOKIE_SECURE = not DEBUG

# Cookie no accesible desde JavaScript (seguridad)
SESSION_COOKIE_HTTPONLY = True

# SameSite para CSRF protection
SESSION_COOKIE_SAMESITE = 'Lax'


# =============================================================================
# CONFIGURACIÓN DATABASE FIRST - MODELOS NO GESTIONADOS
# =============================================================================
# 
# IMPORTANTE: Este proyecto usa la estrategia "Database First" donde:
# - La estructura de BD está definida en scripts SQL (bd/init-scripts/)
# - Los modelos Django tienen managed=False (no gestionados)
# - Django puede hacer CRUD sobre los datos, pero NO modificar estructura
# - Se usa el User model estándar de Django para autenticación
# - Los datos del sistema están en las tablas con managed=False
#
# NO usar AUTH_USER_MODEL personalizado con managed=False ya que causa conflictos
# AUTH_USER_MODEL = 'personas.Agente'  # NO USAR con managed=False
# Usaremos User estándar + relación OneToOne con Agente

# ============================================================================
# CONFIGURACIONES ESPECÍFICAS PARA GIGA
# ============================================================================

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'personas.authentication.CustomSessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# CORS Settings - Para conectar con el frontend Svelte
# Leer de variable de entorno, con fallback a localhost para desarrollo
cors_origins_env = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://127.0.0.1')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_env.split(',')]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default='False', cast=bool)

# Headers adicionales para CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET', 
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ============================================================================
# CONFIGURACIÓN PARA MODELOS NO GESTIONADOS (DATABASE FIRST STRATEGY)
# ============================================================================

# Configurar Django para trabajar con BD externa usando inspectdb
# Los modelos generados tendrán managed = False para evitar conflictos
# con la estructura existente de PostgreSQL

# Logging para debug de conexión BD
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'handlers': ['console'],
        },
    },
}

# ============================================================================
# EMAIL CONFIGURATION - Gmail SMTP
# ============================================================================

# Backend de email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configuración Gmail SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Credenciales (usar variables de entorno en producción)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='giga.sistema.untdf.25@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # App password de Gmail

# Remitente por defecto
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Sistema GIGA <giga.sistema.untdf.25@gmail.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Para desarrollo: mostrar emails en consola si no hay password configurada
if not EMAIL_HOST_PASSWORD and DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# URL del frontend para links en emails
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
