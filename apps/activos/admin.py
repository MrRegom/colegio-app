from django.contrib import admin
from .models import (
    CategoriaActivo, UnidadMedida, EstadoActivo, Activo,
    Ubicacion, Proveniencia, TipoMovimientoActivo, MovimientoActivo, UbicacionActual
)


@admin.register(CategoriaActivo)
class CategoriaActivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo', 'eliminado', 'fecha_creacion']
    list_filter = ['activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'simbolo', 'activo', 'eliminado']
    list_filter = ['activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(EstadoActivo)
class EstadoActivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'color', 'es_inicial', 'permite_movimiento', 'activo', 'eliminado']
    list_filter = ['es_inicial', 'permite_movimiento', 'activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'unidad_medida', 'estado', 'stock_minimo', 'activo', 'eliminado']
    list_filter = ['categoria', 'estado', 'activo', 'eliminado', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'marca', 'modelo', 'numero_serie']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria', 'unidad_medida', 'estado')
        }),
        ('Detalles del Producto', {
            'fields': ('marca', 'modelo', 'numero_serie', 'codigo_barras')
        }),
        ('Control de Stock', {
            'fields': ('stock_minimo', 'stock_maximo', 'punto_reorden')
        }),
        ('Precios', {
            'fields': ('precio_unitario', 'costo_promedio')
        }),
        ('Configuración', {
            'fields': ('requiere_serie', 'requiere_lote', 'requiere_vencimiento', 'activo', 'eliminado')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'edificio', 'piso', 'area', 'activo', 'eliminado']
    list_filter = ['activo', 'eliminado', 'edificio']
    search_fields = ['codigo', 'nombre', 'area']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Proveniencia)
class ProvenienciaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo', 'eliminado', 'fecha_creacion']
    list_filter = ['activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(TipoMovimientoActivo)
class TipoMovimientoActivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'requiere_ubicacion', 'requiere_responsable', 'activo', 'eliminado']
    list_filter = ['requiere_ubicacion', 'requiere_responsable', 'activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(MovimientoActivo)
class MovimientoActivoAdmin(admin.ModelAdmin):
    list_display = ['activo', 'tipo_movimiento', 'ubicacion_destino', 'responsable', 'fecha_movimiento', 'fecha_ingreso', 'usuario_registro']
    list_filter = ['tipo_movimiento', 'ubicacion_destino', 'proveniencia', 'fecha_movimiento', 'fecha_ingreso', 'fecha_baja']
    search_fields = ['activo__codigo', 'activo__nombre', 'responsable__username', 'numero_serie', 'lote', 'numero_factura_guia']
    readonly_fields = ['fecha_movimiento', 'usuario_registro']
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('activo', 'tipo_movimiento', 'fecha_movimiento', 'usuario_registro')
        }),
        ('Ubicación y Responsable', {
            'fields': ('ubicacion_destino', 'responsable')
        }),
        ('Información de Ingreso', {
            'fields': ('fecha_ingreso', 'numero_factura_guia', 'proveniencia'),
            'description': 'Datos del ingreso del activo al inventario'
        }),
        ('Detalles del Activo', {
            'fields': ('numero_serie', 'lote', 'fecha_vencimiento'),
            'description': 'Estos campos son opcionales y dependen de la configuración del activo'
        }),
        ('Información de Baja', {
            'fields': ('fecha_baja', 'motivo_baja'),
            'description': 'Completar solo si el activo fue dado de baja',
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)


@admin.register(UbicacionActual)
class UbicacionActualAdmin(admin.ModelAdmin):
    list_display = ['activo', 'ubicacion', 'responsable', 'fecha_ultima_actualizacion']
    list_filter = ['ubicacion', 'fecha_ultima_actualizacion']
    search_fields = ['activo__codigo', 'activo__nombre', 'responsable__username']
    readonly_fields = ['fecha_ultima_actualizacion']
