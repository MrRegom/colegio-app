from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista_notificaciones'),
    path('marcar-leida/<int:pk>/', views.marcar_como_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('archivar/<int:pk>/', views.archivar_notificacion, name='archivar'),
    path('configuracion/', views.configuracion_notificaciones, name='configuracion'),
    path('contador/', views.contador_notificaciones, name='contador'),
]
