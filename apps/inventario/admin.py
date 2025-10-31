from django.contrib import admin
from .models import (
    Taller, TipoEquipo, Equipo, MantenimientoEquipo,
    Marca, Modelo, NombreArticulo, SectorInventario
)


@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'responsable', 'ubicacion', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'eliminado', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'ubicacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Ubicación y Responsable', {
            'fields': ('ubicacion', 'responsable', 'capacidad_maxima')
        }),
        ('Equipamiento', {
            'fields': ('equipamiento', 'observaciones')
        }),
        ('Estado', {
            'fields': ('activo', 'eliminado', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(TipoEquipo)
class TipoEquipoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'requiere_mantenimiento', 'periodo_mantenimiento_dias', 'activo']
    list_filter = ['requiere_mantenimiento', 'activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'estado', 'responsable', 'taller', 'activo']
    list_filter = ['tipo', 'estado', 'taller', 'activo', 'eliminado', 'fecha_adquisicion']
    search_fields = ['codigo', 'nombre', 'marca', 'modelo', 'numero_serie']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo')
        }),
        ('Detalles del Equipo', {
            'fields': ('marca', 'modelo', 'numero_serie')
        }),
        ('Adquisición', {
            'fields': ('fecha_adquisicion', 'valor_adquisicion')
        }),
        ('Ubicación y Asignación', {
            'fields': ('estado', 'ubicacion_actual', 'responsable', 'taller')
        }),
        ('Mantenimiento', {
            'fields': ('fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Estado', {
            'fields': ('activo', 'eliminado', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(MantenimientoEquipo)
class MantenimientoEquipoAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'fecha_mantenimiento', 'tipo_mantenimiento', 'realizado_por', 'costo']
    list_filter = ['tipo_mantenimiento', 'fecha_mantenimiento', 'activo']
    search_fields = ['equipo__codigo', 'equipo__nombre', 'realizado_por', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_mantenimiento'


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'marca', 'activo']
    list_filter = ['marca', 'activo', 'eliminado']
    search_fields = ['codigo', 'nombre', 'marca__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(NombreArticulo)
class NombreArticuloAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria_recomendada', 'activo']
    list_filter = ['categoria_recomendada', 'activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(SectorInventario)
class SectorInventarioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'responsable', 'activo']
    list_filter = ['activo', 'eliminado']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

