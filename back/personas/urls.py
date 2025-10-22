from django.urls import path
from . import views
from . import views_auth

app_name = 'personas'

urlpatterns = [
    # URLs de autenticación
    path('auth/login/', views_auth.login_view, name='login'),
    path('auth/logout/', views_auth.logout_view, name='logout'),
    path('auth/check-session/', views_auth.check_session, name='check_session'),
    
    # URLs falta hacer porque hay que hacer los serializers
]