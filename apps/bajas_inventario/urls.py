from django.urls import path
from . import views

app_name = 'bajas_inventario'

urlpatterns = [
    # Menú principal de bajas de inventario
    path('', views.MenuBajasView.as_view(), name='menu_bajas'),

    # ==================== LISTADOS ====================
    path('listado/', views.BajaInventarioListView.as_view(), name='lista_bajas'),
    path('mis-bajas/', views.MisBajasListView.as_view(), name='mis_bajas'),
    path('por-autorizar/', views.BajasPorAutorizarListView.as_view(), name='bajas_por_autorizar'),

    # ==================== CRUD ====================
    path('crear/', views.BajaInventarioCreateView.as_view(), name='crear_baja'),
    path('<int:pk>/', views.BajaInventarioDetailView.as_view(), name='detalle_baja'),
    path('<int:pk>/editar/', views.BajaInventarioUpdateView.as_view(), name='editar_baja'),
    path('<int:pk>/eliminar/', views.BajaInventarioDeleteView.as_view(), name='eliminar_baja'),

    # ==================== FLUJO DE AUTORIZACIÓN ====================
    path('<int:pk>/autorizar/', views.BajaInventarioAutorizarView.as_view(), name='autorizar_baja'),
    path('<int:pk>/rechazar/', views.BajaInventarioRechazarView.as_view(), name='rechazar_baja'),
]
