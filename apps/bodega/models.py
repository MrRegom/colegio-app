from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from core.models import BaseModel


class Bodega(BaseModel):
    """Modelo para gestionar las bodegas del sistema"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    responsable = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bodegas_responsable',
        verbose_name='Responsable'
    )

    class Meta:
        db_table = 'tba_bodega_conf_bodega'
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Categoria(BaseModel):
    """Modelo para gestionar categorías de artículos"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'tba_bodega_conf_categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Articulo(BaseModel):
    """Modelo para gestionar artículos en bodega"""
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    codigo = models.CharField(max_length=50, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name='Marca')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='articulos',
        verbose_name='Categoría'
    )
    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock Actual'
    )
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock Mínimo'
    )
    stock_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Stock Máximo'
    )
    punto_reorden = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Punto de Reorden'
    )
    unidad_medida = models.CharField(max_length=20, verbose_name='Unidad de Medida')
    ubicacion_fisica = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        related_name='articulos',
        verbose_name='Ubicación Física (Bodega)'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'tba_bodega_articulos'
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['sku']

    def __str__(self):
        return f"{self.sku} - {self.nombre}"


class TipoMovimiento(BaseModel):
    """Catálogo de tipos de movimiento de inventario"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    class Meta:
        db_table = 'tba_bodega_conf_tipomovimiento'
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimiento'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Movimiento(BaseModel):
    """Modelo para registrar movimientos de inventario"""
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Artículo'
    )
    tipo = models.ForeignKey(
        TipoMovimiento,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Tipo de Movimiento'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad'
    )
    operacion = models.CharField(
        max_length=20,
        choices=[
            ('ENTRADA', 'Entrada'),
            ('SALIDA', 'Salida'),
        ],
        verbose_name='Operación'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_bodega',
        verbose_name='Usuario'
    )
    motivo = models.TextField(verbose_name='Motivo')
    stock_antes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Antes'
    )
    stock_despues = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Después'
    )

    class Meta:
        db_table = 'tba_bodega_movimientos'
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.operacion} - {self.articulo.sku} - {self.cantidad}"


