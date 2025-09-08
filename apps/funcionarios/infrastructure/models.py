"""
Modelos Django para Funcionarios.

Define la representación de datos en la base de datos.
"""
from django.db import models


class Funcionario(models.Model):
    """
    Modelo Django para Funcionario.
    
    Este modelo se conecta a una tabla existente en PostgreSQL
    y NO es manejado por Django (no se crean migraciones).
    """
    id = models.AutoField(primary_key=True)
    nombres = models.TextField()
    apellidos = models.TextField()
    email = models.TextField()
    estado = models.TextField(default='activo')
    eliminado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'funcionarios'  # Usar search_path en settings para el esquema
        managed = False  # Django no manejará esta tabla (no creará migraciones)
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def is_active(self):
        return self.estado == 'activo' and not self.eliminado
