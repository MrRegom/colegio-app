from django.contrib import admin
from .models import Bodega, Categoria, Articulo, TipoMovimiento, Movimiento


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'responsable', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ['sku', 'codigo', 'nombre', 'categoria', 'stock_actual', 'stock_minimo', 'ubicacion_fisica', 'activo']
    list_filter = ['categoria', 'ubicacion_fisica', 'activo']
    search_fields = ['sku', 'codigo', 'nombre', 'marca']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Información General', {
            'fields': ('sku', 'codigo', 'nombre', 'descripcion', 'marca', 'categoria')
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo', 'punto_reorden', 'unidad_medida')
        }),
        ('Ubicación', {
            'fields': ('ubicacion_fisica',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Estado', {
            'fields': ('activo', 'eliminado', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['articulo', 'tipo', 'operacion', 'cantidad', 'usuario', 'stock_antes', 'stock_despues', 'fecha_creacion']
    list_filter = ['operacion', 'tipo', 'fecha_creacion']
    search_fields = ['articulo__sku', 'articulo__nombre', 'usuario__correo', 'motivo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_creacion'
