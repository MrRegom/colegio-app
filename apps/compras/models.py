from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.contrib.auth.models import User
from apps.activos.models import Activo
from apps.bodega.models import Bodega, Articulo
from core.models import BaseModel


class Proveedor(BaseModel):
    """Modelo para gestionar proveedores"""
    rut = models.CharField(max_length=12, unique=True, verbose_name='RUT')
    razon_social = models.CharField(max_length=255, verbose_name='Razón Social')
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nombre Fantasía')
    giro = models.CharField(max_length=255, blank=True, null=True, verbose_name='Giro')

    # Contacto
    direccion = models.CharField(max_length=255, verbose_name='Dirección')
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comuna')
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ciudad')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(
        validators=[EmailValidator()],
        blank=True,
        null=True,
        verbose_name='Correo Electrónico'
    )
    sitio_web = models.URLField(blank=True, null=True, verbose_name='Sitio Web')

    # Datos comerciales
    condicion_pago = models.CharField(
        max_length=100,
        default='Contado',
        verbose_name='Condición de Pago'
    )
    dias_credito = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Días de Crédito'
    )

    # Control
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')

    class Meta:
        db_table = 'compra_proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']

    def __str__(self):
        return f"{self.rut} - {self.razon_social}"


class EstadoOrdenCompra(models.Model):
    """Catálogo de estados de órdenes de compra"""
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
        db_table = 'compra_estado_orden'
        verbose_name = 'Estado de Orden de Compra'
        verbose_name_plural = 'Estados de Órdenes de Compra'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class OrdenCompra(models.Model):
    """Modelo para gestionar órdenes de compra"""
    numero = models.CharField(max_length=20, unique=True, verbose_name='Número de Orden')
    fecha_orden = models.DateField(verbose_name='Fecha de Orden')
    fecha_entrega_esperada = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Entrega Esperada'
    )
    fecha_entrega_real = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Entrega Real'
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='ordenes_compra',
        verbose_name='Proveedor'
    )
    bodega_destino = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        related_name='ordenes_compra',
        verbose_name='Bodega Destino'
    )
    estado = models.ForeignKey(
        EstadoOrdenCompra,
        on_delete=models.PROTECT,
        related_name='ordenes_compra',
        verbose_name='Estado'
    )
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='ordenes_solicitadas',
        verbose_name='Solicitante'
    )
    aprobador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='ordenes_aprobadas',
        verbose_name='Aprobador',
        blank=True,
        null=True
    )

    # Montos
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    impuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Impuesto (IVA)'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Descuento'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Total'
    )

    # Observaciones
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    notas_internas = models.TextField(blank=True, null=True, verbose_name='Notas Internas')

    # Auditoria
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')

    class Meta:
        db_table = 'compra_orden'
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-fecha_orden', '-numero']

    def __str__(self):
        return f"OC-{self.numero} - {self.proveedor.razon_social}"


class DetalleOrdenCompra(BaseModel):
    """Modelo para el detalle de productos en una orden de compra"""
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Orden de Compra'
    )
    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name='detalles_compra',
        verbose_name='Activo'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio Unitario'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Descuento'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    cantidad_recibida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Recibida'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'compra_orden_detalle'
        verbose_name = 'Detalle de Orden de Compra'
        verbose_name_plural = 'Detalles de Órdenes de Compra'
        ordering = ['orden_compra', 'id']

    def __str__(self):
        return f"{self.orden_compra.numero} - {self.activo.codigo} ({self.cantidad})"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento
        super().save(*args, **kwargs)


class DetalleOrdenCompraArticulo(BaseModel):
    """Modelo para el detalle de artículos de bodega en una orden de compra"""
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='detalles_articulos',
        verbose_name='Orden de Compra'
    )
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='detalles_compra',
        verbose_name='Artículo'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio Unitario'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Descuento'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    cantidad_recibida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Recibida'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'compra_orden_detalle_articulo'
        verbose_name = 'Detalle Orden - Artículo'
        verbose_name_plural = 'Detalles Orden - Artículos'
        ordering = ['orden_compra', 'id']

    def __str__(self):
        return f"{self.orden_compra.numero} - {self.articulo.sku} ({self.cantidad})"

    def save(self, *args, **kwargs):
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento
        super().save(*args, **kwargs)


# ==================== RECEPCIÓN DE ARTÍCULOS ====================

class EstadoRecepcion(BaseModel):
    """Catálogo de estados de recepción"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='Color (Hex)')
    es_inicial = models.BooleanField(default=False, verbose_name='Estado Inicial')
    es_final = models.BooleanField(default=False, verbose_name='Estado Final')

    class Meta:
        db_table = 'compra_estado_recepcion'
        verbose_name = 'Estado de Recepción'
        verbose_name_plural = 'Estados de Recepción'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class RecepcionArticulo(BaseModel):
    """Modelo para gestionar recepciones de artículos de bodega"""
    numero = models.CharField(max_length=20, unique=True, verbose_name='Número de Recepción')
    fecha_recepcion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Recepción')
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.PROTECT,
        related_name='recepciones_articulos',
        verbose_name='Orden de Compra',
        blank=True,
        null=True
    )
    bodega = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        related_name='recepciones_articulos',
        verbose_name='Bodega'
    )
    estado = models.ForeignKey(
        EstadoRecepcion,
        on_delete=models.PROTECT,
        related_name='recepciones_articulos',
        verbose_name='Estado'
    )
    recibido_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recepciones_articulos_recibidas',
        verbose_name='Recibido Por'
    )
    documento_referencia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Documento Referencia (Guía/Factura)'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'compra_recepcion_articulo'
        verbose_name = 'Recepción de Artículo'
        verbose_name_plural = 'Recepciones de Artículos'
        ordering = ['-fecha_recepcion']

    def __str__(self):
        return f"REC-ART-{self.numero} - {self.fecha_recepcion.strftime('%d/%m/%Y')}"


class DetalleRecepcionArticulo(BaseModel):
    """Detalle de artículos recibidos"""
    recepcion = models.ForeignKey(
        RecepcionArticulo,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Recepción'
    )
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='recepciones',
        verbose_name='Artículo'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad Recibida'
    )
    lote = models.CharField(max_length=50, blank=True, null=True, verbose_name='Lote')
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'compra_recepcion_articulo_detalle'
        verbose_name = 'Detalle Recepción Artículo'
        verbose_name_plural = 'Detalles Recepción Artículos'
        ordering = ['recepcion', 'id']

    def __str__(self):
        return f"{self.recepcion.numero} - {self.articulo.sku} ({self.cantidad})"


# ==================== RECEPCIÓN DE BIENES (ACTIVOS) ====================

class RecepcionActivo(BaseModel):
    """Modelo para gestionar recepciones de bienes/activos fijos"""
    numero = models.CharField(max_length=20, unique=True, verbose_name='Número de Recepción')
    fecha_recepcion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Recepción')
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.PROTECT,
        related_name='recepciones_activos',
        verbose_name='Orden de Compra',
        blank=True,
        null=True
    )
    estado = models.ForeignKey(
        EstadoRecepcion,
        on_delete=models.PROTECT,
        related_name='recepciones_activos',
        verbose_name='Estado'
    )
    recibido_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recepciones_activos_recibidas',
        verbose_name='Recibido Por'
    )
    documento_referencia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Documento Referencia (Guía/Factura)'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'compra_recepcion_activo'
        verbose_name = 'Recepción de Bien/Activo'
        verbose_name_plural = 'Recepciones de Bienes/Activos'
        ordering = ['-fecha_recepcion']

    def __str__(self):
        return f"REC-ACT-{self.numero} - {self.fecha_recepcion.strftime('%d/%m/%Y')}"


class DetalleRecepcionActivo(BaseModel):
    """Detalle de activos/bienes recibidos"""
    recepcion = models.ForeignKey(
        RecepcionActivo,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Recepción'
    )
    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name='recepciones',
        verbose_name='Activo/Bien'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad Recibida'
    )
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Serie')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'compra_recepcion_activo_detalle'
        verbose_name = 'Detalle Recepción Activo'
        verbose_name_plural = 'Detalles Recepción Activos'
        ordering = ['recepcion', 'id']

    def __str__(self):
        return f"{self.recepcion.numero} - {self.activo.codigo} ({self.cantidad})"
