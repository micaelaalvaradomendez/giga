"""
URLs para el módulo asistencia
"""
from django.urls import path
from . import views

urlpatterns = [
    # Endpoints para usuarios
    path('marcar/', views.marcar_asistencia, name='marcar_asistencia'),
    path('estado/', views.obtener_estado_asistencia, name='obtener_estado_asistencia'),
    
    # Endpoints para administradores
    path('admin/listar/', views.listar_asistencias, name='listar_asistencias'),
    path('admin/resumen/', views.resumen_asistencias, name='resumen_asistencias'),
    path('admin/corregir/<int:asistencia_id>/', views.corregir_asistencia, name='corregir_asistencia'),
    path('admin/licencias/', views.listar_licencias, name='listar_licencias'),
    
    # Endpoint para cron job
    path('cron/marcar-salidas/', views.ejecutar_marcacion_automatica, name='ejecutar_marcacion_automatica'),
]
