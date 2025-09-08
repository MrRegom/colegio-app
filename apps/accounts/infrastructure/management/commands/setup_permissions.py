from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import UsuarioSistema


class Command(BaseCommand):
    help = 'Configura grupos y permisos predeterminados para el sistema de correos masivos'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('Configurando grupos y permisos del sistema...')
        )
        
        # Crear grupos básicos
        grupos_config = {
            'Administradores de Sistema': {
                'description': 'Acceso completo al sistema',
                'permissions': [
                    # Permisos de usuarios
                    'accounts.add_usuariosistema',
                    'accounts.change_usuariosistema', 
                    'accounts.delete_usuariosistema',
                    'accounts.view_usuariosistema',
                    'accounts.can_manage_unit_users',
                    'accounts.can_view_unit_reports',
                    'accounts.can_create_mass_emails',
                    'accounts.can_manage_email_lists',
                    'accounts.can_view_email_analytics',
                    'accounts.can_manage_email_templates',
                    
                    # Permisos de unidades
                    'accounts.add_unidad',
                    'accounts.change_unidad',
                    'accounts.delete_unidad',
                    'accounts.view_unidad',
                    
                    # Permisos de auditoría
                    'accounts.view_logauditoria',
                    
                    # Permisos de grupos
                    'auth.add_group',
                    'auth.change_group',
                    'auth.delete_group',
                    'auth.view_group',
                ]
            },
            
            'Administradores de Unidad': {
                'description': 'Gestión de usuarios y correos de su unidad',
                'permissions': [
                    'accounts.view_usuariosistema',
                    'accounts.change_usuariosistema',
                    'accounts.can_manage_unit_users',
                    'accounts.can_view_unit_reports',
                    'accounts.can_create_mass_emails',
                    'accounts.can_manage_email_lists',
                    'accounts.can_view_email_analytics',
                    'accounts.view_unidad',
                    'accounts.view_logauditoria',
                ]
            },
            
            'Operadores de Correo': {
                'description': 'Creación y gestión de envíos masivos',
                'permissions': [
                    'accounts.view_usuariosistema',
                    'accounts.can_create_mass_emails',
                    'accounts.can_manage_email_lists',
                    'accounts.can_view_email_analytics',
                    'accounts.view_unidad',
                ]
            },
            
            'Usuarios Básicos': {
                'description': 'Solo consulta de información básica',
                'permissions': [
                    'accounts.view_usuariosistema',
                    'accounts.view_unidad',
                ]
            }
        }
        
        for grupo_name, config in grupos_config.items():
            grupo, created = Group.objects.get_or_create(name=grupo_name)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{grupo_name}" creado.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{grupo_name}" ya existe, actualizando permisos...')
                )
            
            # Limpiar permisos existentes
            grupo.permissions.clear()
            
            # Asignar permisos
            permisos_asignados = 0
            for perm_code in config['permissions']:
                try:
                    app_label, codename = perm_code.split('.')
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    grupo.permissions.add(permission)
                    permisos_asignados += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Permiso no encontrado: {perm_code}')
                    )
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR(f'Formato de permiso inválido: {perm_code}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Grupo "{grupo_name}": {permisos_asignados} permisos asignados.'
                )
            )
        
        # Asignar grupo de administrador al superusuario
        try:
            admin_group = Group.objects.get(name='Administradores de Sistema')
            superusers = UsuarioSistema.objects.filter(is_superuser=True)
            
            for user in superusers:
                user.groups.add(admin_group)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuario "{user.username}" agregado al grupo "Administradores de Sistema".'
                    )
                )
                
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('No se pudo asignar grupo al superusuario.')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Configuración de permisos completada exitosamente.')
        )
