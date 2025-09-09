from django.db import models

# Create your models here.

class SolicitudPerfil(models.Model):
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    rut = models.CharField(max_length=20)
    email = models.EmailField()
    unidad = models.CharField(max_length=255)
    estamento = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    nombre_jefatura = models.CharField(max_length=255)
    apellidos_jefatura = models.CharField(max_length=255)
    rut_jefatura = models.CharField(max_length=20)
    email_jefatura = models.EmailField()
    unidad_jefatura = models.CharField(max_length=255)
    estamento_jefatura = models.CharField(max_length=255)
    cargo_jefatura = models.CharField(max_length=255)
    sistemas = models.JSONField()  # Usa TextField si tu versión de Django no soporta JSONField
    permisos = models.TextField(blank=True)
    homologacion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='pendiente')

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.rut}"
