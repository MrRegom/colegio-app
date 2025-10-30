from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


class TipoReporte(BaseModel):
    """Catálogo de tipos de reportes"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    modulo = models.CharField(
        max_length=50,
        choices=[
            ('INVENTARIO', 'Inventario'),
            ('COMPRAS', 'Compras'),
            ('SOLICITUDES', 'Solicitudes'),
            ('MOVIMIENTOS', 'Movimientos'),
            ('BAJAS', 'Bajas'),
            ('GENERAL', 'General'),
        ],
        default='GENERAL',
        verbose_name='Módulo'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'reporte_tipo'
        verbose_name = 'Tipo de Reporte'
        verbose_name_plural = 'Tipos de Reportes'
        ordering = ['modulo', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ReporteGenerado(BaseModel):
    """Modelo para registrar reportes generados por los usuarios"""
    tipo_reporte = models.ForeignKey(
        TipoReporte,
        on_delete=models.PROTECT,
        related_name='reportes_generados',
        verbose_name='Tipo de Reporte'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reportes_generados',
        verbose_name='Usuario'
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Generación')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha Inicio (Filtro)')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha Fin (Filtro)')
    parametros = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Parámetros',
        help_text='Parámetros adicionales utilizados para generar el reporte'
    )
    formato = models.CharField(
        max_length=10,
        choices=[
            ('PDF', 'PDF'),
            ('EXCEL', 'Excel'),
            ('CSV', 'CSV'),
            ('HTML', 'HTML'),
        ],
        default='PDF',
        verbose_name='Formato'
    )
    archivo = models.FileField(
        upload_to='reportes/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Archivo Generado'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'reporte_generado'
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.tipo_reporte.nombre} - {self.usuario.correo} ({self.fecha_generacion})"


class MovimientoInventario(BaseModel):
    """Modelo para registrar todos los movimientos de inventario"""
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Movimiento')
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=[
            ('ENTRADA', 'Entrada'),
            ('SALIDA', 'Salida'),
            ('TRASPASO', 'Traspaso'),
            ('AJUSTE', 'Ajuste Positivo'),
            ('AJUSTE_NEG', 'Ajuste Negativo'),
            ('BAJA', 'Baja'),
        ],
        verbose_name='Tipo de Movimiento'
    )

    # Referencias
    activo = models.ForeignKey(
        'activos.Activo',
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Activo'
    )
    bodega_origen = models.ForeignKey(
        'bodega.Bodega',
        on_delete=models.PROTECT,
        related_name='movimientos_origen',
        verbose_name='Bodega Origen',
        blank=True,
        null=True
    )
    bodega_destino = models.ForeignKey(
        'bodega.Bodega',
        on_delete=models.PROTECT,
        related_name='movimientos_destino',
        verbose_name='Bodega Destino',
        blank=True,
        null=True
    )

    # Cantidades
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad'
    )
    stock_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Anterior'
    )
    stock_nuevo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Nuevo'
    )

    # Referencias a documentos
    documento_referencia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Documento de Referencia'
    )
    tipo_documento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Tipo de Documento',
        help_text='Ej: Orden de Compra, Solicitud, Baja, etc.'
    )

    # Usuario y observaciones
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_realizados',
        verbose_name='Usuario'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'reporte_movimiento_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['-fecha_movimiento']),
            models.Index(fields=['activo', '-fecha_movimiento']),
            models.Index(fields=['tipo_movimiento', '-fecha_movimiento']),
        ]

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.activo.codigo} ({self.cantidad}) - {self.fecha_movimiento}"
