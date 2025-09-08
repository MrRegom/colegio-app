from django.db import models

# Create your models here.

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    puesto_trabajo = models.CharField(max_length=100)
    razon_contacto = models.CharField(max_length=255)
    mensaje = models.TextField()
    foto = models.ImageField(upload_to='contactos_fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
