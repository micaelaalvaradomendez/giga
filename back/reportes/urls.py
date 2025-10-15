from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # URLs para Reportes
    path('reportes/', views.ReporteListView.as_view(), name='reporte-list'),
    path('reportes/<uuid:pk>/', views.ReporteDetailView.as_view(), name='reporte-detail'),
    
    # URLs para Notificaciones
    path('notificaciones/', views.NotificacionListView.as_view(), name='notificacion-list'),
    path('notificaciones/<uuid:pk>/', views.NotificacionDetailView.as_view(), name='notificacion-detail'),
    
    # URLs para Plantillas de Correo
    path('plantillas-correo/', views.PlantillaCorreoListView.as_view(), name='plantilla-correo-list'),
    path('plantillas-correo/<uuid:pk>/', views.PlantillaCorreoDetailView.as_view(), name='plantilla-correo-detail'),
]