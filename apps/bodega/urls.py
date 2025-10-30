from django.urls import path
from . import views

app_name = 'bodega'

urlpatterns = [
    # Menú principal de bodega
    path('', views.MenuBodegaView.as_view(), name='menu_bodega'),

    # Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),

    # Artículos
    path('articulos/', views.ArticuloListView.as_view(), name='articulo_lista'),
    path('articulos/crear/', views.ArticuloCreateView.as_view(), name='articulo_crear'),
    path('articulos/<int:pk>/', views.ArticuloDetailView.as_view(), name='articulo_detalle'),
    path('articulos/<int:pk>/editar/', views.ArticuloUpdateView.as_view(), name='articulo_editar'),

    # Movimientos
    path('movimientos/', views.MovimientoListView.as_view(), name='movimiento_lista'),
    path('movimientos/crear/', views.MovimientoCreateView.as_view(), name='movimiento_crear'),
    path('movimientos/<int:pk>/', views.MovimientoDetailView.as_view(), name='movimiento_detalle'),
]
