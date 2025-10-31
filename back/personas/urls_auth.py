"""
URLs para autenticación
"""
from django.urls import path
from . import views_auth

urlpatterns = [
    path('login/', views_auth.login_view, name='api_login'),
    path('logout/', views_auth.logout_view, name='api_logout'),
    path('check-session/', views_auth.check_session, name='api_check_session'),
    path('update-profile/', views_auth.update_profile, name='api_update_profile'),
    path('recover-password/', views_auth.recover_password, name='api_recover_password'),
]

