"""
URL configuration for giga project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .health_views import health_check, simple_health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/personas/', include('personas.urls')),
    path('api/guardias/', include('guardias.urls')),
    path('api/auditoria/', include('auditoria.urls')),
    # Health check endpoints
    path('health/', simple_health, name='health'),
    path('api/health/', health_check, name='api_health'),
]