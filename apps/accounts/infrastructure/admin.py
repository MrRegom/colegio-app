from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Unidad, UsuarioSistema, LogAuditoria


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    """Administración de Unidades en el panel de Django."""
    list_display = ('nombre', 'estado', 'created_at', 'updated_at')
    list_filter = ('estado', 'created_at')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'estado')
        }),
        (_('Información de Auditoría'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsuarioSistema)
class UsuarioSistemaAdmin(UserAdmin):
    """Administración de Usuarios del Sistema basada en UserAdmin de Django."""
    
    # Campos mostrados en la lista
    list_display = ('username', 'email', 'nombres', 'apellidos', 'unidad', 'rol', 'estado', 'is_active', 'date_joined')
    list_filter = ('rol', 'estado', 'unidad', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'nombres', 'apellidos')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    
    # Configuración de fieldsets personalizada
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Información Personal'), {
            'fields': ('nombres', 'apellidos', 'email')
        }),
        (_('Configuración del Sistema'), {
            'fields': ('unidad', 'rol', 'estado')
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Fechas Importantes'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets para agregar usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        (_('Información Personal'), {
            'fields': ('nombres', 'apellidos')
        }),
        (_('Configuración del Sistema'), {
            'fields': ('unidad', 'rol', 'estado')
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar el formulario según el usuario."""
        form = super().get_form(request, obj, **kwargs)
        
        # Si no es superuser, limitar opciones
        if not request.user.is_superuser:
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'is_staff' in form.base_fields and obj and obj.pk == request.user.pk:
                form.base_fields['is_staff'].disabled = True
                
        return form
    
    def get_queryset(self, request):
        """Filtrar usuarios según permisos."""
        qs = super().get_queryset(request)
        
        # Si no es superuser, solo mostrar usuarios de su unidad
        if not request.user.is_superuser and hasattr(request.user, 'unidad'):
            if request.user.rol == 'admin':
                qs = qs.filter(unidad=request.user.unidad)
            else:
                qs = qs.filter(pk=request.user.pk)  # Solo su propio perfil
                
        return qs


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Administración de Logs de Auditoría (solo lectura)."""
    list_display = ('usuario', 'accion', 'entidad', 'entidad_id', 'created_at', 'ip_usuario')
    list_filter = ('accion', 'entidad', 'created_at')
    search_fields = ('usuario__username', 'accion', 'entidad', 'descripcion')
    ordering = ('-created_at',)
    readonly_fields = ('usuario', 'accion', 'entidad', 'entidad_id', 'descripcion', 
                      'valores_previos', 'valores_nuevos', 'ip_usuario', 'user_agent', 'created_at')
    
    # Solo lectura - no permitir agregar/editar/eliminar
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        (_('Información del Evento'), {
            'fields': ('usuario', 'accion', 'entidad', 'entidad_id', 'descripcion', 'created_at')
        }),
        (_('Datos del Cambio'), {
            'fields': ('valores_previos', 'valores_nuevos'),
            'classes': ('collapse',)
        }),
        (_('Información Técnica'), {
            'fields': ('ip_usuario', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filtrar logs según permisos del usuario."""
        qs = super().get_queryset(request)
        
        # Si no es superuser, solo mostrar logs de su unidad
        if not request.user.is_superuser and hasattr(request.user, 'unidad'):
            if request.user.rol == 'admin':
                # Admin de unidad ve logs de usuarios de su unidad
                usuarios_unidad = UsuarioSistema.objects.filter(unidad=request.user.unidad)
                qs = qs.filter(usuario__in=usuarios_unidad)
            else:
                # Usuario normal solo ve sus propios logs
                qs = qs.filter(usuario=request.user)
                
        return qs