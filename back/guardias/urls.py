from django.urls import path
from . import views

app_name = 'guardias'

urlpatterns = [
    # URLs para Cronogramas
    path('cronogramas/', views.CronogramaGuardiasListView.as_view(), name='cronograma-list'),
    path('cronogramas/<uuid:pk>/', views.CronogramaGuardiasDetailView.as_view(), name='cronograma-detail'),
    
    # URLs para Guardias
    path('guardias/', views.GuardiaListView.as_view(), name='guardia-list'),
    path('guardias/<uuid:pk>/', views.GuardiaDetailView.as_view(), name='guardia-detail'),
    
    # URLs para Horas de Guardias
    path('horas-guardias/', views.HorasGuardiasListView.as_view(), name='horas-guardias-list'),
    path('horas-guardias/<uuid:pk>/', views.HorasGuardiasDetailView.as_view(), name='horas-guardias-detail'),
    
    # URLs para Feriados
    path('feriados/', views.FeriadoListView.as_view(), name='feriado-list'),
    path('feriados/<uuid:pk>/', views.FeriadoDetailView.as_view(), name='feriado-detail'),
]