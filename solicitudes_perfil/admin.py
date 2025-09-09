from django.contrib import admin
from .models import SolicitudPerfil

@admin.register(SolicitudPerfil)
class SolicitudPerfilAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'rut', 'email', 'fecha_creacion', 'estado')
    search_fields = ('nombre', 'apellidos', 'rut', 'email')
    list_filter = ('estado', 'fecha_creacion')
