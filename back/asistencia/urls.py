from django.urls import path
from . import views

app_name = 'asistencia'

urlpatterns = [
    # URLs para Asistencias
    path('asistencias/', views.AsistenciaListView.as_view(), name='asistencia-list'),
    path('asistencias/<uuid:pk>/', views.AsistenciaDetailView.as_view(), name='asistencia-detail'),
    
    # URLs para Marcas
    path('marcas/', views.MarcaListView.as_view(), name='marca-list'),
    path('marcas/<uuid:pk>/', views.MarcaDetailView.as_view(), name='marca-detail'),
    
    # URLs para Licencias
    path('licencias/', views.LicenciaListView.as_view(), name='licencia-list'),
    path('licencias/<uuid:pk>/', views.LicenciaDetailView.as_view(), name='licencia-detail'),
    
    # URLs para Novedades
    path('novedades/', views.NovedadListView.as_view(), name='novedad-list'),
    path('novedades/<uuid:pk>/', views.NovedadDetailView.as_view(), name='novedad-detail'),
]