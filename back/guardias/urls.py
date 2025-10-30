from django.urls import path
from . import views

app_name = 'guardias'

urlpatterns = [
    path('cronogramas/planificar/', views.PlanificarCronogramaView.as_view(), name='cronogramas_planificar'),
]
