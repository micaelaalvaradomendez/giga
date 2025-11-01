"""
URLs   para el módulo convenio_ia
"""
from core.urls import create_standard_urls
from .views import ConvenioViewSet, ConsultaConvenioViewSet, IndiceConvenioViewSet

app_name = 'convenio_ia'

urlpatterns = create_standard_urls(app_name, [
    ('convenios', ConvenioViewSet),
    ('consultas', ConsultaConvenioViewSet),
    ('indices', IndiceConvenioViewSet),
])