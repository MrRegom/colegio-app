"""
URLs para el módulo de inventario.
"""

from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Talleres
    path('talleres/', views.taller_list, name='taller_list'),
    path('talleres/crear/', views.taller_create, name='taller_create'),
    path('talleres/<int:pk>/editar/', views.taller_update, name='taller_update'),
    path('talleres/<int:pk>/eliminar/', views.taller_delete, name='taller_delete'),
    
    # Tipos de Equipo
    path('tipos-equipo/', views.tipo_equipo_list, name='tipo_equipo_list'),
    path('tipos-equipo/crear/', views.tipo_equipo_create, name='tipo_equipo_create'),
    path('tipos-equipo/<int:pk>/editar/', views.tipo_equipo_update, name='tipo_equipo_update'),
    path('tipos-equipo/<int:pk>/eliminar/', views.tipo_equipo_delete, name='tipo_equipo_delete'),
    
    # Equipos
    path('equipos/', views.equipo_list, name='equipo_list'),
    path('equipos/crear/', views.equipo_create, name='equipo_create'),
    path('equipos/<int:pk>/', views.equipo_detail, name='equipo_detail'),
    path('equipos/<int:pk>/editar/', views.equipo_update, name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.equipo_delete, name='equipo_delete'),
    
    # Mantenimientos
    path('equipos/<int:equipo_id>/mantenimiento/', views.mantenimiento_create, name='mantenimiento_create'),
    
    # Menú principal
    path('menu-gestores/', views.menu_gestores, name='menu_gestores'),
    
    # Bodegas
    path('bodegas/', views.bodega_list, name='bodega_list'),
    path('bodegas/crear/', views.bodega_create, name='bodega_create'),
    path('bodegas/<int:pk>/editar/', views.bodega_update, name='bodega_update'),
    path('bodegas/<int:pk>/eliminar/', views.bodega_delete, name='bodega_delete'),
    
    # Estados de Orden de Compra
    path('estados-orden-compra/', views.estado_orden_compra_list, name='estado_orden_compra_list'),
    path('estados-orden-compra/crear/', views.estado_orden_compra_create, name='estado_orden_compra_create'),
    path('estados-orden-compra/<int:pk>/editar/', views.estado_orden_compra_update, name='estado_orden_compra_update'),
    path('estados-orden-compra/<int:pk>/eliminar/', views.estado_orden_compra_delete, name='estado_orden_compra_delete'),
    
    # Estados de Recepción
    path('estados-recepcion/', views.estado_recepcion_list, name='estado_recepcion_list'),
    path('estados-recepcion/crear/', views.estado_recepcion_create, name='estado_recepcion_create'),
    path('estados-recepcion/<int:pk>/editar/', views.estado_recepcion_update, name='estado_recepcion_update'),
    path('estados-recepcion/<int:pk>/eliminar/', views.estado_recepcion_delete, name='estado_recepcion_delete'),
    
    # Proveniencias
    path('proveniencias/', views.proveniencia_list, name='proveniencia_list'),
    path('proveniencias/crear/', views.proveniencia_create, name='proveniencia_create'),
    path('proveniencias/<int:pk>/editar/', views.proveniencia_update, name='proveniencia_update'),
    path('proveniencias/<int:pk>/eliminar/', views.proveniencia_delete, name='proveniencia_delete'),
    
    # Departamentos
    path('departamentos/', views.departamento_list, name='departamento_list'),
    path('departamentos/crear/', views.departamento_create, name='departamento_create'),
    path('departamentos/<int:pk>/editar/', views.departamento_update, name='departamento_update'),
    path('departamentos/<int:pk>/eliminar/', views.departamento_delete, name='departamento_delete'),
    
    # Marcas
    path('marcas/', views.marca_list, name='marca_list'),
    path('marcas/crear/', views.marca_create, name='marca_create'),
    path('marcas/<int:pk>/editar/', views.marca_update, name='marca_update'),
    path('marcas/<int:pk>/eliminar/', views.marca_delete, name='marca_delete'),
    
    # Modelos
    path('modelos/', views.modelo_list, name='modelo_list'),
    path('modelos/crear/', views.modelo_create, name='modelo_create'),
    path('modelos/<int:pk>/editar/', views.modelo_update, name='modelo_update'),
    path('modelos/<int:pk>/eliminar/', views.modelo_delete, name='modelo_delete'),
    
    # Nombres de Artículos
    path('nombres-articulos/', views.nombre_articulo_list, name='nombre_articulo_list'),
    path('nombres-articulos/crear/', views.nombre_articulo_create, name='nombre_articulo_create'),
    path('nombres-articulos/<int:pk>/editar/', views.nombre_articulo_update, name='nombre_articulo_update'),
    path('nombres-articulos/<int:pk>/eliminar/', views.nombre_articulo_delete, name='nombre_articulo_delete'),
    
    # Sectores de Inventario
    path('sectores/', views.sector_inventario_list, name='sector_inventario_list'),
    path('sectores/crear/', views.sector_inventario_create, name='sector_inventario_create'),
    path('sectores/<int:pk>/editar/', views.sector_inventario_update, name='sector_inventario_update'),
    path('sectores/<int:pk>/eliminar/', views.sector_inventario_delete, name='sector_inventario_delete'),
    
    # API AJAX
    path('ajax/filtrar-modelos/', views.ajax_filtrar_modelos, name='ajax_filtrar_modelos'),
]

