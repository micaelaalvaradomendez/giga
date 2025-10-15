from django.urls import path
from . import views

app_name = 'convenio_ia'

urlpatterns = [
    # URLs para Convenios
    path('convenios/', views.ConvenioListView.as_view(), name='convenio-list'),
    path('convenios/<uuid:pk>/', views.ConvenioDetailView.as_view(), name='convenio-detail'),
    
    # URLs para Consultas de Convenio
    path('consultas/', views.ConsultaConvenioListView.as_view(), name='consulta-list'),
    path('consultas/<uuid:pk>/', views.ConsultaConvenioDetailView.as_view(), name='consulta-detail'),
    
    # URL para realizar consultas
    path('consultar/', views.ConsultarConvenioView.as_view(), name='consultar-convenio'),
]