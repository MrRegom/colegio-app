from django.contrib import admin
from .models import (
    Proveedor, EstadoOrdenCompra, OrdenCompra, DetalleOrdenCompra, DetalleOrdenCompraArticulo,
    EstadoRecepcion, RecepcionArticulo, DetalleRecepcionArticulo,
    RecepcionActivo, DetalleRecepcionActivo
)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['rut', 'razon_social', 'nombre_fantasia', 'telefono', 'email', 'activo']
    list_filter = ['activo', 'ciudad']
    search_fields = ['rut', 'razon_social', 'nombre_fantasia']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(EstadoOrdenCompra)
class EstadoOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'es_inicial', 'es_final', 'permite_edicion', 'activo']
    list_filter = ['es_inicial', 'es_final', 'permite_edicion', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(EstadoRecepcion)
class EstadoRecepcionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'es_inicial', 'es_final', 'activo']
    list_filter = ['es_inicial', 'es_final', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


class DetalleOrdenCompraInline(admin.TabularInline):
    model = DetalleOrdenCompra
    extra = 1
    readonly_fields = ['subtotal']


class DetalleOrdenCompraArticuloInline(admin.TabularInline):
    model = DetalleOrdenCompraArticulo
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fecha_orden', 'proveedor', 'estado', 'total', 'solicitante']
    list_filter = ['estado', 'fecha_orden', 'bodega_destino']
    search_fields = ['numero', 'proveedor__razon_social']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    inlines = [DetalleOrdenCompraArticuloInline, DetalleOrdenCompraInline]


class DetalleRecepcionArticuloInline(admin.TabularInline):
    model = DetalleRecepcionArticulo
    extra = 1


@admin.register(RecepcionArticulo)
class RecepcionArticuloAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fecha_recepcion', 'orden_compra', 'bodega', 'estado', 'recibido_por']
    list_filter = ['estado', 'bodega', 'fecha_recepcion']
    search_fields = ['numero', 'documento_referencia']
    readonly_fields = ['fecha_recepcion', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [DetalleRecepcionArticuloInline]


class DetalleRecepcionActivoInline(admin.TabularInline):
    model = DetalleRecepcionActivo
    extra = 1


@admin.register(RecepcionActivo)
class RecepcionActivoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fecha_recepcion', 'orden_compra', 'estado', 'recibido_por']
    list_filter = ['estado', 'fecha_recepcion']
    search_fields = ['numero', 'documento_referencia']
    readonly_fields = ['fecha_recepcion', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [DetalleRecepcionActivoInline]
