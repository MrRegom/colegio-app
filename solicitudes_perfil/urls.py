from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_solicitud, name='crear_solicitud_perfil'),
    path('lista/', views.lista_solicitudes, name='lista_solicitudes_perfil'),
]