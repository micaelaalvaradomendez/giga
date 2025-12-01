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
    path('admin/listar/', views.listar_asistencias_admin, name='listar_asistencias'),
    path('admin/resumen/', views.resumen_asistencias, name='resumen_asistencias'),
    path('admin/corregir/<int:asistencia_id>/', views.corregir_asistencia, name='corregir_asistencia'),
    path('admin/marcar-ausente/<int:asistencia_id>/', views.marcar_como_ausente, name='marcar_como_ausente'),
    
    # Endpoints de licencias
    path('licencias/', views.gestionar_licencias, name='gestionar_licencias'),  # GET y POST
    path('licencias/<int:licencia_id>/', views.eliminar_licencia, name='eliminar_licencia'),  # DELETE
    path('licencias/<int:licencia_id>/aprobar/', views.aprobar_licencia, name='aprobar_licencia'),
    path('licencias/<int:licencia_id>/rechazar/', views.rechazar_licencia, name='rechazar_licencia'),

    # Endpoints para ABM de Tipos de Licencia
    path('admin/tipos-licencia/', views.listar_tipos_licencia, name='listar_tipos_licencia'),
    path('admin/tipos-licencia/crear/', views.crear_tipo_licencia, name='crear_tipo_licencia'),
    path('admin/tipos-licencia/actualizar/<int:tipo_licencia_id>/', views.actualizar_tipo_licencia, name='actualizar_tipo_licencia'),
    path('admin/tipos-licencia/eliminar/<int:tipo_licencia_id>/', views.eliminar_tipo_licencia, name='eliminar_tipo_licencia'),
    
    # Endpoint para cron job
    path('cron/marcar-salidas/', views.ejecutar_marcacion_automatica, name='ejecutar_marcacion_automatica'),
]
