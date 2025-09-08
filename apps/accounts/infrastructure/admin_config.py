from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin
from django.utils.translation import gettext_lazy as _


class CustomAdminSite(admin.AdminSite):
    """
    Configuración personalizada del panel de administración
    para el sistema de envío masivo de correos.
    """
    site_header = "Sistema de Envío Masivo de Correos"
    site_title = "Correos Masivos"
    index_title = "Panel de Administración"
    site_url = None  # Quitar el "View site" link
    
    def get_app_list(self, request):
        """
        Organizar las apps en el orden deseado para mejor UX.
        """
        app_list = super().get_app_list(request)
        
        # Definir el orden deseado de las apps
        app_order = [
            'accounts',      # Gestión de Usuarios y Permisos
            'auth',          # Grupos y Permisos del Sistema  
            'admin',         # Logs del Admin
            'sites',         # Configuración de Sitios
        ]
        
        # Reorganizar según el orden definido
        ordered_apps = []
        for app_name in app_order:
            for app in app_list:
                if app['app_label'] == app_name:
                    ordered_apps.append(app)
                    break
        
        # Agregar cualquier app no especificada al final
        for app in app_list:
            if app not in ordered_apps:
                ordered_apps.append(app)
                
        return ordered_apps

    def index(self, request, extra_context=None):
        """
        Personalizar la página de inicio del admin.
        """
        extra_context = extra_context or {}
        
        # Agregar estadísticas útiles
        from .models import UsuarioSistema, Unidad
        
        stats = {
            'total_usuarios': UsuarioSistema.objects.count(),
            'usuarios_activos': UsuarioSistema.objects.filter(estado='activo').count(),
            'total_unidades': Unidad.objects.count(),
            'unidades_activas': Unidad.objects.filter(estado='activa').count(),
        }
        
        extra_context['stats'] = stats
        return super().index(request, extra_context)


# Crear instancia del admin personalizado
admin_site = CustomAdminSite(name='custom_admin')


class CustomGroupAdmin(GroupAdmin):
    """
    Administración personalizada de Grupos para mejor organización de permisos.
    """
    list_display = ('name', 'get_permissions_count', 'get_users_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permisos'
    
    def get_users_count(self, obj):
        return obj.user_set.count()
    get_users_count.short_description = 'Usuarios'
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Organizar permisos por app en el formulario."""
        if db_field.name == "permissions":
            kwargs["queryset"] = Permission.objects.select_related('content_type').order_by(
                'content_type__app_label', 'content_type__model', 'codename'
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# Re-registrar Group con la configuración personalizada
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
