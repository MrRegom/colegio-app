from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.accounts.models import Unidad, UsuarioSistema


class Command(BaseCommand):
    help = 'Configura datos iniciales: unidad principal y superusuario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username para el superusuario (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@hospital.local',
            help='Email para el superusuario (default: admin@hospital.local)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password para el superusuario (default: admin123)'
        )
        parser.add_argument(
            '--unidad',
            type=str,
            default='Administración',
            help='Nombre de la unidad principal (default: Administración)'
        )

    def handle(self, *args, **options):
        # Crear unidad principal si no existe
        unidad_principal, created = Unidad.objects.get_or_create(
            nombre=options['unidad'],
            defaults={
                'estado': 'activa'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Unidad "{unidad_principal.nombre}" creada exitosamente.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Unidad "{unidad_principal.nombre}" ya existe.')
            )

        # Verificar si ya existe un superusuario
        if UsuarioSistema.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Ya existe un superusuario en el sistema.')
            )
            return

        # Crear superusuario
        try:
            superuser = UsuarioSistema.objects.create_superuser(
                username=options['username'],
                email=options['email'],
                password=options['password'],
                unidad=unidad_principal,
                nombres='Administrador',
                apellidos='del Sistema',
                rol='admin',
                estado='activo'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuario "{superuser.username}" creado exitosamente.\n'
                    f'Email: {superuser.email}\n'
                    f'Unidad: {superuser.unidad.nombre}\n'
                    f'Para acceder al admin panel: http://localhost:8000/admin/'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear superusuario: {str(e)}')
            )
