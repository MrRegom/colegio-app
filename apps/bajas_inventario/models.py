from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from apps.activos.models import Activo
from apps.bodega.models import Bodega
from core.models import BaseModel


class MotivoBaja(BaseModel):
    """Catálogo de motivos de baja de inventario"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    requiere_autorizacion = models.BooleanField(
        default=True,
        verbose_name='Requiere Autorización'
    )
    requiere_documento = models.BooleanField(
        default=False,
        verbose_name='Requiere Documento',
        help_text='Indica si se debe adjuntar un documento de respaldo'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'baja_motivo'
        verbose_name = 'Motivo de Baja'
        verbose_name_plural = 'Motivos de Baja'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class EstadoBaja(BaseModel):
    """Catálogo de estados de bajas de inventario"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Color (Hex)'
    )
    es_inicial = models.BooleanField(default=False, verbose_name='Estado Inicial')
    es_final = models.BooleanField(default=False, verbose_name='Estado Final')
    permite_edicion = models.BooleanField(default=True, verbose_name='Permite Edición')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'baja_estado'
        verbose_name = 'Estado de Baja'
        verbose_name_plural = 'Estados de Bajas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class BajaInventario(BaseModel):
    """Modelo para gestionar bajas de inventario"""
    numero = models.CharField(max_length=20, unique=True, verbose_name='Número de Baja')
    fecha_baja = models.DateField(verbose_name='Fecha de Baja')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')

    motivo = models.ForeignKey(
        MotivoBaja,
        on_delete=models.PROTECT,
        related_name='bajas',
        verbose_name='Motivo'
    )
    estado = models.ForeignKey(
        EstadoBaja,
        on_delete=models.PROTECT,
        related_name='bajas',
        verbose_name='Estado'
    )
    bodega = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        related_name='bajas_inventario',
        verbose_name='Bodega'
    )

    # Responsables
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bajas_solicitadas',
        verbose_name='Solicitante'
    )
    autorizador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bajas_autorizadas',
        verbose_name='Autorizador',
        blank=True,
        null=True
    )
    fecha_autorizacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Autorización'
    )

    # Información adicional
    descripcion = models.TextField(verbose_name='Descripción')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    notas_autorizacion = models.TextField(blank=True, null=True, verbose_name='Notas de Autorización')

    # Documento
    documento = models.FileField(
        upload_to='bajas_inventario/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Documento de Respaldo'
    )

    # Total
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Valor Total'
    )

    # Auditoria
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')

    class Meta:
        db_table = 'baja_inventario'
        verbose_name = 'Baja de Inventario'
        verbose_name_plural = 'Bajas de Inventario'
        ordering = ['-fecha_baja', '-numero']

    def __str__(self):
        return f"BAJA-{self.numero} - {self.motivo.nombre}"


class DetalleBaja(BaseModel):
    """Modelo para el detalle de activos dados de baja"""
    baja = models.ForeignKey(
        BajaInventario,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Baja'
    )
    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name='detalles_baja',
        verbose_name='Activo'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad'
    )
    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor Unitario'
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor Total'
    )
    lote = models.CharField(max_length=50, blank=True, null=True, verbose_name='Lote')
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Serie')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'baja_detalle'
        verbose_name = 'Detalle de Baja'
        verbose_name_plural = 'Detalles de Bajas'
        ordering = ['baja', 'id']

    def __str__(self):
        return f"{self.baja.numero} - {self.activo.codigo} ({self.cantidad})"

    def save(self, *args, **kwargs):
        # Calcular valor total automáticamente
        self.valor_total = self.cantidad * self.valor_unitario
        super().save(*args, **kwargs)


class HistorialBaja(BaseModel):
    """Modelo para el historial de cambios de estado de bajas"""
    baja = models.ForeignKey(
        BajaInventario,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Baja'
    )
    estado_anterior = models.ForeignKey(
        EstadoBaja,
        on_delete=models.PROTECT,
        related_name='historiales_anterior',
        verbose_name='Estado Anterior',
        blank=True,
        null=True
    )
    estado_nuevo = models.ForeignKey(
        EstadoBaja,
        on_delete=models.PROTECT,
        related_name='historiales_nuevo',
        verbose_name='Estado Nuevo'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cambios_estado_baja',
        verbose_name='Usuario'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Cambio')

    class Meta:
        db_table = 'baja_historial'
        verbose_name = 'Historial de Baja'
        verbose_name_plural = 'Historial de Bajas'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"{self.baja.numero} - {self.estado_nuevo.nombre} ({self.fecha_cambio})"
