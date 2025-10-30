from django.contrib import admin
from .models import (
    MotivoBaja, EstadoBaja, BajaInventario,
    DetalleBaja, HistorialBaja
)


@admin.register(MotivoBaja)
class MotivoBajaAdmin(admin.ModelAdmin):
    """Admin para motivos de baja"""
    list_display = [
        'codigo', 'nombre', 'requiere_autorizacion',
        'requiere_documento', 'activo', 'fecha_creacion'
    ]
    list_filter = ['activo', 'requiere_autorizacion', 'requiere_documento']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['codigo']
    readonly_fields = ['fecha_creacion']


@admin.register(EstadoBaja)
class EstadoBajaAdmin(admin.ModelAdmin):
    """Admin para estados de baja"""
    list_display = [
        'codigo', 'nombre', 'color', 'es_inicial',
        'es_final', 'permite_edicion', 'activo'
    ]
    list_filter = ['activo', 'es_inicial', 'es_final', 'permite_edicion']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    readonly_fields = ['fecha_creacion']


class DetalleBajaInline(admin.TabularInline):
    """Inline para detalles de baja"""
    model = DetalleBaja
    extra = 1
    fields = [
        'activo', 'cantidad', 'valor_unitario',
        'valor_total', 'lote', 'numero_serie'
    ]
    readonly_fields = ['valor_total']


class HistorialBajaInline(admin.TabularInline):
    """Inline para historial de baja"""
    model = HistorialBaja
    extra = 0
    fields = [
        'estado_anterior', 'estado_nuevo', 'usuario',
        'observaciones', 'fecha_cambio'
    ]
    readonly_fields = ['fecha_cambio']
    can_delete = False


@admin.register(BajaInventario)
class BajaInventarioAdmin(admin.ModelAdmin):
    """Admin para bajas de inventario"""
    list_display = [
        'numero', 'fecha_baja', 'motivo', 'estado',
        'bodega', 'solicitante', 'autorizador',
        'valor_total', 'activo'
    ]
    list_filter = [
        'estado', 'motivo', 'fecha_baja',
        'activo', 'eliminado'
    ]
    search_fields = [
        'numero', 'descripcion', 'solicitante__username',
        'autorizador__username'
    ]
    ordering = ['-fecha_baja', '-numero']
    readonly_fields = [
        'numero', 'fecha_registro', 'fecha_modificacion',
        'fecha_autorizacion'
    ]
    inlines = [DetalleBajaInline, HistorialBajaInline]

    fieldsets = (
        ('Información General', {
            'fields': (
                'numero', 'fecha_baja', 'motivo', 'estado', 'bodega'
            )
        }),
        ('Responsables', {
            'fields': (
                'solicitante', 'autorizador', 'fecha_autorizacion'
            )
        }),
        ('Detalles', {
            'fields': (
                'descripcion', 'observaciones', 'notas_autorizacion', 'documento'
            )
        }),
        ('Totales', {
            'fields': ('valor_total',)
        }),
        ('Control', {
            'fields': (
                'activo', 'eliminado', 'fecha_registro', 'fecha_modificacion'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Hacer campos readonly según el estado"""
        readonly = list(self.readonly_fields)

        if obj and obj.estado and obj.estado.es_final:
            # Si está en estado final, hacer todo readonly excepto notas
            readonly.extend([
                'fecha_baja', 'motivo', 'bodega', 'descripcion',
                'observaciones', 'documento'
            ])

        return readonly


@admin.register(DetalleBaja)
class DetalleBajaAdmin(admin.ModelAdmin):
    """Admin para detalles de baja"""
    list_display = [
        'baja', 'activo', 'cantidad', 'valor_unitario',
        'valor_total', 'lote', 'numero_serie'
    ]
    list_filter = ['baja__estado', 'baja__motivo']
    search_fields = [
        'baja__numero', 'activo__codigo', 'activo__nombre',
        'lote', 'numero_serie'
    ]
    readonly_fields = ['valor_total', 'fecha_creacion']


@admin.register(HistorialBaja)
class HistorialBajaAdmin(admin.ModelAdmin):
    """Admin para historial de bajas"""
    list_display = [
        'baja', 'estado_anterior', 'estado_nuevo',
        'usuario', 'fecha_cambio'
    ]
    list_filter = ['estado_nuevo', 'fecha_cambio']
    search_fields = ['baja__numero', 'usuario__username', 'observaciones']
    readonly_fields = ['fecha_cambio']
    ordering = ['-fecha_cambio']
