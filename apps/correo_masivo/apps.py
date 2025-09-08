from django.apps import AppConfig


class CorreoMasivoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.correo_masivo'
    # Django automáticamente usará el label basado en el nombre
    verbose_name = 'Sistema de Correo Masivo'
    
    def ready(self):
        """Ejecutar configuraciones cuando la app esté lista."""
        pass
