"""
URLs para Correo Masivo Web.
"""
from django.urls import path
from .views import (
    ListaFuncionariosView,
    GestionarFirmaView,
    EnviarCorreoView
)

app_name = 'correo_masivo'

urlpatterns = [
    path('funcionarios/', ListaFuncionariosView.as_view(), name='lista_funcionarios'),
    path('firma/', GestionarFirmaView.as_view(), name='gestionar_firma'),
    path('enviar/', EnviarCorreoView.as_view(), name='enviar_correo'),
]
