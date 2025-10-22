"""
URLs para autenticación
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views_auth

urlpatterns = [
    path('login/', csrf_exempt(views_auth.login_view), name='api_login'),
    path('logout/', csrf_exempt(views_auth.logout_view), name='api_logout'),
    path('check-session/', csrf_exempt(views_auth.check_session), name='api_check_session'),
]