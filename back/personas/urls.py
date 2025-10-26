from django.urls import path
from . import views

app_name = 'personas'

urlpatterns = [
    path('subordinados/', views.subordinados, name='api_subordinados'),
]
