from django.contrib import admin
from .models import TipoNotificacion, Notificacion, ConfiguracionNotificacion


@admin.register(TipoNotificacion)
class TipoNotificacionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'prioridad', 'enviar_email', 'activo']
    list_filter = ['prioridad', 'enviar_email', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'usuario_destino', 'tipo', 'leida',
        'email_enviado', 'fecha_creacion'
    ]
    list_filter = ['tipo', 'leida', 'email_enviado', 'archivada', 'fecha_creacion']
    search_fields = ['titulo', 'mensaje', 'usuario_destino__correo']
    readonly_fields = ['fecha_creacion', 'fecha_lectura', 'fecha_envio_email']
    date_hierarchy = 'fecha_creacion'
    fieldsets = (
        ('Información General', {
            'fields': ('tipo', 'usuario_destino', 'usuario_origen')
        }),
        ('Contenido', {
            'fields': ('titulo', 'mensaje', 'enlace')
        }),
        ('Referencias', {
            'fields': ('modulo', 'referencia_id', 'referencia_tipo')
        }),
        ('Estado', {
            'fields': ('leida', 'fecha_lectura', 'archivada')
        }),
        ('Email', {
            'fields': ('email_enviado', 'fecha_envio_email')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_expiracion')
        }),
    )


@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_notificacion', 'notificacion_sistema', 'notificacion_email']
    list_filter = ['tipo_notificacion', 'notificacion_sistema', 'notificacion_email']
    search_fields = ['usuario__correo', 'tipo_notificacion__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
