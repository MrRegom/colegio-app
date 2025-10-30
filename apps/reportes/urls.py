from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('tipos/', views.lista_reportes, name='lista_reportes'),
    path('historial/', views.historial_reportes, name='historial_reportes'),
    path('inventario-actual/', views.reporte_inventario_actual, name='inventario_actual'),
    path('movimientos/', views.reporte_movimientos, name='movimientos'),
]
