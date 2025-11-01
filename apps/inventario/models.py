"""
Modelos para el módulo de inventario.
Incluye modelos faltantes que se requieren para la gestión completa.
"""

from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


class Taller(BaseModel):
    """
    Catálogo de talleres del colegio.
    
    Los talleres son espacios o unidades de trabajo donde se realizan
    actividades específicas y requieren equipamiento e inventario.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ubicación Física',
        help_text='Ubicación física del taller en el colegio'
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='talleres_responsable',
        verbose_name='Responsable',
        blank=True,
        null=True,
        help_text='Persona responsable del taller'
    )
    capacidad_maxima = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Capacidad Máxima',
        help_text='Capacidad máxima de personas que puede albergar'
    )
    equipamiento = models.TextField(
        blank=True,
        null=True,
        verbose_name='Equipamiento',
        help_text='Descripción del equipamiento disponible en el taller'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    class Meta:
        db_table = 'inventario_taller'
        verbose_name = 'Taller'
        verbose_name_plural = 'Talleres'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoEquipo(BaseModel):
    """
    Catálogo de tipos de equipos.
    
    Clasifica los equipos por tipo (computadores, proyectores, herramientas, etc.)
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    requiere_mantenimiento = models.BooleanField(
        default=True,
        verbose_name='Requiere Mantenimiento',
        help_text='Indica si este tipo de equipo requiere mantenimiento regular'
    )
    periodo_mantenimiento_dias = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Período de Mantenimiento (días)',
        help_text='Período recomendado entre mantenimientos en días'
    )

    class Meta:
        db_table = 'inventario_tipo_equipo'
        verbose_name = 'Tipo de Equipo'
        verbose_name_plural = 'Tipos de Equipos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Equipo(BaseModel):
    """
    Catálogo de equipos del colegio.
    
    Representa equipos específicos que pueden ser asignados a talleres,
    departamentos o ubicaciones.
    """
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código/Patrimonio')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    tipo = models.ForeignKey(
        TipoEquipo,
        on_delete=models.PROTECT,
        related_name='equipos',
        verbose_name='Tipo de Equipo'
    )
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name='Marca')
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Serie',
        unique=True
    )
    fecha_adquisicion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Adquisición'
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Valor de Adquisición'
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('DISPONIBLE', 'Disponible'),
            ('EN_USO', 'En Uso'),
            ('MANTENIMIENTO', 'En Mantenimiento'),
            ('DADO_DE_BAJA', 'Dado de Baja'),
            ('PRESTADO', 'Prestado'),
        ],
        default='DISPONIBLE',
        verbose_name='Estado'
    )
    ubicacion_actual = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ubicación Actual',
        help_text='Ubicación física actual del equipo'
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='equipos_responsable',
        verbose_name='Responsable',
        blank=True,
        null=True
    )
    taller = models.ForeignKey(
        Taller,
        on_delete=models.SET_NULL,
        related_name='equipos',
        verbose_name='Taller',
        blank=True,
        null=True,
        help_text='Taller al que pertenece o está asignado el equipo'
    )
    fecha_ultimo_mantenimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Último Mantenimiento'
    )
    fecha_proximo_mantenimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Próximo Mantenimiento'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    class Meta:
        db_table = 'inventario_equipo'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['codigo']
        permissions = [
            ('gestionar_equipos', 'Puede gestionar equipos'),
            ('asignar_equipos', 'Puede asignar equipos a usuarios/talleres'),
            ('ver_mantenimientos', 'Puede ver historial de mantenimientos'),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MantenimientoEquipo(BaseModel):
    """
    Historial de mantenimientos de equipos.
    """
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        verbose_name='Equipo'
    )
    fecha_mantenimiento = models.DateField(verbose_name='Fecha de Mantenimiento')
    tipo_mantenimiento = models.CharField(
        max_length=20,
        choices=[
            ('PREVENTIVO', 'Preventivo'),
            ('CORRECTIVO', 'Correctivo'),
            ('CALIBRACION', 'Calibración'),
            ('REVISION', 'Revisión'),
        ],
        verbose_name='Tipo de Mantenimiento'
    )
    descripcion = models.TextField(verbose_name='Descripción')
    realizado_por = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Realizado Por',
        help_text='Nombre del técnico o empresa que realizó el mantenimiento'
    )
    costo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Costo'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    proximo_mantenimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Próximo Mantenimiento Programado'
    )

    class Meta:
        db_table = 'inventario_mantenimiento_equipo'
        verbose_name = 'Mantenimiento de Equipo'
        verbose_name_plural = 'Mantenimientos de Equipos'
        ordering = ['-fecha_mantenimiento']

    def __str__(self):
        return f"{self.equipo.codigo} - {self.fecha_mantenimiento} - {self.tipo_mantenimiento}"


# ==================== CATÁLOGOS DE PRODUCTOS ====================

class Marca(BaseModel):
    """
    Catálogo de marcas de productos.
    
    Gestiona las marcas de forma centralizada para mantener consistencia
    en el inventario.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Marca')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    logo_url = models.URLField(blank=True, null=True, verbose_name='URL del Logo')
    
    class Meta:
        db_table = 'inventario_marca'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Modelo(BaseModel):
    """
    Catálogo de modelos de productos, relacionado con Marcas.
    
    Cada modelo pertenece a una marca específica para mantener
    la integridad referencial.
    """
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código del Modelo')
    nombre = models.CharField(max_length=150, verbose_name='Nombre del Modelo')
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='modelos',
        verbose_name='Marca'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    
    class Meta:
        db_table = 'inventario_modelo'
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        ordering = ['marca__nombre', 'nombre']
        unique_together = [['marca', 'nombre']]  # Evita duplicados por marca
    
    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"


class NombreArticulo(BaseModel):
    """
    Catálogo de nombres estándar de artículos para autocompletado.
    
    Permite mantener consistencia en los nombres de productos
    y facilita el autocompletado en formularios.
    """
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código/SKU')
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Artículo')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    categoria_recomendada = models.ForeignKey(
        'bodega.Categoria',
        on_delete=models.SET_NULL,
        related_name='nombres_articulos',
        blank=True,
        null=True,
        verbose_name='Categoría Recomendada'
    )
    
    class Meta:
        db_table = 'inventario_nombre_articulo'
        verbose_name = 'Nombre de Artículo'
        verbose_name_plural = 'Nombres de Artículos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class SectorInventario(BaseModel):
    """
    Catálogo de sectores/áreas de inventario.
    
    Permite organizar el inventario por áreas como:
    - Música
    - Educación Física
    - Laboratorio
    - Biblioteca
    - etc.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Sector')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='sectores_inventario_responsable',
        blank=True,
        null=True,
        verbose_name='Responsable del Sector'
    )
    
    class Meta:
        db_table = 'inventario_sector'
        verbose_name = 'Sector de Inventario'
        verbose_name_plural = 'Sectores de Inventario'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

