from django.contrib import admin
from .models import (
    Departamento, Area, Equipo,
    TipoSolicitud, EstadoSolicitud, Solicitud, DetalleSolicitud, HistorialSolicitud
)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'responsable', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'departamento', 'responsable', 'activo']
    list_filter = ['departamento', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'departamento', 'lider', 'activo']
    list_filter = ['departamento', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(TipoSolicitud)
class TipoSolicitudAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'requiere_aprobacion', 'activo']
    list_filter = ['requiere_aprobacion', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(EstadoSolicitud)
class EstadoSolicitudAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'es_inicial', 'es_final', 'requiere_accion', 'activo']
    list_filter = ['es_inicial', 'es_final', 'requiere_accion', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


class DetalleSolicitudInline(admin.TabularInline):
    model = DetalleSolicitud
    extra = 1
    readonly_fields = ['fecha_creacion']


class HistorialSolicitudInline(admin.TabularInline):
    model = HistorialSolicitud
    extra = 0
    readonly_fields = ['fecha_cambio']
    can_delete = False


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fecha_solicitud', 'tipo_solicitud', 'estado', 'solicitante', 'departamento', 'area']
    list_filter = ['tipo_solicitud', 'estado', 'fecha_solicitud', 'departamento', 'area', 'bodega_origen']
    search_fields = ['numero', 'solicitante__correo', 'area_solicitante', 'titulo_actividad']
    readonly_fields = ['fecha_solicitud', 'fecha_creacion', 'fecha_modificacion']
    inlines = [DetalleSolicitudInline, HistorialSolicitudInline]
    fieldsets = (
        ('Información General', {
            'fields': ('numero', 'fecha_solicitud', 'fecha_requerida', 'tipo_solicitud', 'estado')
        }),
        ('Información de la Actividad', {
            'fields': ('titulo_actividad', 'objetivo_actividad')
        }),
        ('Solicitante', {
            'fields': ('solicitante', 'area_solicitante', 'motivo')
        }),
        ('Estructura Organizacional', {
            'fields': ('departamento', 'area', 'equipo')
        }),
        ('Aprobación', {
            'fields': ('aprobador', 'fecha_aprobacion', 'notas_aprobacion')
        }),
        ('Despacho', {
            'fields': ('despachador', 'fecha_despacho', 'notas_despacho', 'bodega_origen')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion')
        }),
    )


@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'activo', 'cantidad_solicitada', 'cantidad_aprobada', 'cantidad_despachada']
    list_filter = ['solicitud__estado', 'fecha_creacion']
    search_fields = ['solicitud__numero', 'activo__codigo', 'activo__nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(HistorialSolicitud)
class HistorialSolicitudAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio']
    list_filter = ['estado_nuevo', 'fecha_cambio']
    search_fields = ['solicitud__numero', 'usuario__correo']
    readonly_fields = ['fecha_cambio']
