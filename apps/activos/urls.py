from django.urls import path
from . import views

app_name = 'activos'

urlpatterns = [
    # Menú principal de inventario
    path('', views.MenuInventarioView.as_view(), name='menu_inventario'),

    # ==================== ACTIVOS ====================
    # Listar y detalle
    path('listado/', views.ActivoListView.as_view(), name='lista_activos'),
    path('<int:pk>/', views.ActivoDetailView.as_view(), name='detalle_activo'),

    # CRUD Activos
    path('crear/', views.ActivoCreateView.as_view(), name='crear_activo'),
    path('<int:pk>/editar/', views.ActivoUpdateView.as_view(), name='editar_activo'),
    path('<int:pk>/eliminar/', views.ActivoDeleteView.as_view(), name='eliminar_activo'),

    # ==================== MOVIMIENTOS Y UBICACIONES ====================
    path('movimientos/', views.MovimientoListView.as_view(), name='lista_movimientos'),
    path('movimientos/registrar/', views.MovimientoCreateView.as_view(), name='registrar_movimiento'),
    path('movimientos/<int:pk>/', views.MovimientoDetailView.as_view(), name='detalle_movimiento'),
    path('ubicacion-actual/', views.UbicacionActualListView.as_view(), name='ubicacion_actual'),

    # ==================== CATEGORÍAS ====================
    path('categorias/', views.CategoriaListView.as_view(), name='lista_categorias'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='eliminar_categoria'),

    # ==================== UNIDADES DE MEDIDA ====================
    path('unidades/', views.UnidadMedidaListView.as_view(), name='lista_unidades'),
    path('unidades/crear/', views.UnidadMedidaCreateView.as_view(), name='crear_unidad'),
    path('unidades/<int:pk>/editar/', views.UnidadMedidaUpdateView.as_view(), name='editar_unidad'),
    path('unidades/<int:pk>/eliminar/', views.UnidadMedidaDeleteView.as_view(), name='eliminar_unidad'),

    # ==================== ESTADOS DE ACTIVO ====================
    path('estados/', views.EstadoActivoListView.as_view(), name='lista_estados'),
    path('estados/crear/', views.EstadoActivoCreateView.as_view(), name='crear_estado'),
    path('estados/<int:pk>/editar/', views.EstadoActivoUpdateView.as_view(), name='editar_estado'),
    path('estados/<int:pk>/eliminar/', views.EstadoActivoDeleteView.as_view(), name='eliminar_estado'),

    # ==================== UBICACIONES ====================
    path('ubicaciones/', views.UbicacionListView.as_view(), name='lista_ubicaciones'),
    path('ubicaciones/crear/', views.UbicacionCreateView.as_view(), name='crear_ubicacion'),
    path('ubicaciones/<int:pk>/editar/', views.UbicacionUpdateView.as_view(), name='editar_ubicacion'),
    path('ubicaciones/<int:pk>/eliminar/', views.UbicacionDeleteView.as_view(), name='eliminar_ubicacion'),

    # ==================== TIPOS DE MOVIMIENTO ====================
    path('tipos-movimiento/', views.TipoMovimientoListView.as_view(), name='lista_tipos_movimiento'),
    path('tipos-movimiento/crear/', views.TipoMovimientoCreateView.as_view(), name='crear_tipo_movimiento'),
    path('tipos-movimiento/<int:pk>/editar/', views.TipoMovimientoUpdateView.as_view(), name='editar_tipo_movimiento'),
    path('tipos-movimiento/<int:pk>/eliminar/', views.TipoMovimientoDeleteView.as_view(), name='eliminar_tipo_movimiento'),
]
