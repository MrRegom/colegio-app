
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from core.models import BaseModel


class CategoriaActivo(BaseModel):
    """
    Catálogo de categorías de activos.

    Hereda de BaseModel para mantener consistencia con el resto del proyecto
    y aprovechar soft delete, campos de auditoría y estado activo/inactivo.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    class Meta:
        db_table = 'activo_categoria'
        verbose_name = 'Categoría de Activo'
        verbose_name_plural = 'Categorías de Activos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class UnidadMedida(BaseModel):
    """
    Catálogo de unidades de medida.

    Hereda de BaseModel para soft delete y auditoría.
    """
    codigo = models.CharField(max_length=10, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    simbolo = models.CharField(max_length=10, verbose_name='Símbolo')

    class Meta:
        db_table = 'activo_unidad_medida'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.simbolo})"


class EstadoActivo(BaseModel):
    """
    Catálogo de estados de activos.

    Hereda de BaseModel para soft delete y auditoría.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Color (Hex)',
        help_text='Color en formato hexadecimal para visualización'
    )
    es_inicial = models.BooleanField(default=False, verbose_name='Estado Inicial')
    permite_movimiento = models.BooleanField(default=True, verbose_name='Permite Movimiento')

    class Meta:
        db_table = 'activo_estado'
        verbose_name = 'Estado de Activo'
        verbose_name_plural = 'Estados de Activos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Ubicacion(BaseModel):
    """
    Catálogo de ubicaciones físicas para activos.

    Hereda de BaseModel para soft delete y auditoría.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    edificio = models.CharField(max_length=100, blank=True, null=True, verbose_name='Edificio')
    piso = models.CharField(max_length=20, blank=True, null=True, verbose_name='Piso')
    area = models.CharField(max_length=100, blank=True, null=True, verbose_name='Área/Departamento')

    class Meta:
        db_table = 'activo_ubicacion'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Proveniencia(BaseModel):
    """
    Catálogo de proveniencias de activos.

    Indica el origen o procedencia del activo (compra, donación, etc.)
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    class Meta:
        db_table = 'activo_proveniencia'
        verbose_name = 'Proveniencia'
        verbose_name_plural = 'Proveniencias'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoMovimientoActivo(BaseModel):
    """
    Catálogo de tipos de movimiento de activos.

    Hereda de BaseModel para soft delete y auditoría.
    """
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    requiere_ubicacion = models.BooleanField(default=True, verbose_name='Requiere Ubicación')
    requiere_responsable = models.BooleanField(default=True, verbose_name='Requiere Responsable')

    class Meta:
        db_table = 'activo_tipo_movimiento'
        verbose_name = 'Tipo de Movimiento de Activo'
        verbose_name_plural = 'Tipos de Movimiento de Activos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Activo(BaseModel):
    """
    Modelo principal para gestionar activos/productos del inventario.

    Hereda de BaseModel para aprovechar soft delete, auditoría automática
    y campos de control (activo, eliminado, fecha_creacion, fecha_actualizacion).
    """
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código/SKU')
    nombre_articulo = models.ForeignKey(
        'inventario.NombreArticulo',
        on_delete=models.SET_NULL,
        related_name='activos',
        blank=True,
        null=True,
        verbose_name='Nombre de Artículo (Catálogo)',
        help_text='Nombre estándar del catálogo (opcional para autocompletado)'
    )
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    categoria = models.ForeignKey(
        CategoriaActivo,
        on_delete=models.PROTECT,
        related_name='activos',
        verbose_name='Categoría'
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT,
        related_name='activos',
        verbose_name='Unidad de Medida'
    )
    estado = models.ForeignKey(
        EstadoActivo,
        on_delete=models.PROTECT,
        related_name='activos',
        verbose_name='Estado'
    )
    
    # Sector/Taller del inventario (Música, Ed. Física, Laboratorio, etc.)
    sector = models.ForeignKey(
        'inventario.SectorInventario',
        on_delete=models.PROTECT,
        related_name='activos',
        blank=True,
        null=True,
        verbose_name='Sector/Taller',
        help_text='Sector o área del inventario (Música, Ed. Física, Laboratorio, etc.)'
    )

    # Información del producto
    marca = models.ForeignKey(
        'inventario.Marca',
        on_delete=models.PROTECT,
        related_name='activos',
        blank=True,
        null=True,
        verbose_name='Marca'
    )
    modelo = models.ForeignKey(
        'inventario.Modelo',
        on_delete=models.PROTECT,
        related_name='activos',
        blank=True,
        null=True,
        verbose_name='Modelo',
        help_text='Selecciona primero la marca para filtrar modelos'
    )
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Serie')
    codigo_barras = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Código de Barras',
        help_text='Código de barras del producto (dejar vacío para auto-generar desde el código)'
    )

    # Stock y control
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='Stock Mínimo'
    )
    stock_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name='Stock Máximo'
    )
    punto_reorden = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name='Punto de Reorden'
    )

    # Precios
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name='Precio Unitario'
    )
    costo_promedio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name='Costo Promedio'
    )

    # Control adicional (campos de BaseModel ya incluyen activo y fechas)
    requiere_serie = models.BooleanField(default=False, verbose_name='Requiere Número de Serie')
    requiere_lote = models.BooleanField(default=False, verbose_name='Requiere Lote')
    requiere_vencimiento = models.BooleanField(default=False, verbose_name='Requiere Fecha de Vencimiento')
    
    def save(self, *args, **kwargs):
        """Auto-generar código de barras si no se proporciona"""
        if not self.codigo_barras and self.codigo:
            # Generar código de barras desde el código/SKU
            self.codigo_barras = f"COD{self.codigo.replace('-', '').replace('_', '').upper()[:12]}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'activo'
        verbose_name = 'Activo'
        verbose_name_plural = 'Activos'
        ordering = ['codigo']
        permissions = [
            ('gestionar_inventario', 'Puede gestionar inventario de activos'),
            ('ajustar_inventario', 'Puede realizar ajustes de inventario'),
            ('ver_reportes_inventario', 'Puede ver reportes de inventario'),
            ('importar_activos', 'Puede importar activos masivamente'),
            ('exportar_activos', 'Puede exportar listado de activos'),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoActivo(models.Model):
    """
    Modelo para rastrear movimientos individuales de activos.
    Cada activo es único y se rastrea individualmente (no por cantidades).
    """
    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name='movimientos_activo',
        verbose_name='Activo'
    )
    tipo_movimiento = models.ForeignKey(
        TipoMovimientoActivo,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Tipo de Movimiento'
    )
    ubicacion_destino = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name='movimientos_destino',
        verbose_name='Ubicación Destino',
        blank=True,
        null=True,
        help_text='Ubicación física donde se encuentra el activo'
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='activos_responsable',
        verbose_name='Responsable',
        blank=True,
        null=True,
        help_text='Usuario responsable del activo'
    )

    # Campos opcionales según configuración del activo
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Serie',
        help_text='Requerido si el activo requiere número de serie'
    )
    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Lote',
        help_text='Requerido si el activo requiere lote'
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Vencimiento',
        help_text='Requerido si el activo requiere fecha de vencimiento'
    )

    # Información de ingreso del activo
    fecha_ingreso = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Ingreso',
        help_text='Fecha en que el activo ingresó al inventario'
    )
    numero_factura_guia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nº Factura / Guía',
        help_text='Número de factura o guía de remisión'
    )
    proveniencia = models.ForeignKey(
        'Proveniencia',
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Proveniencia',
        blank=True,
        null=True,
        help_text='Origen o procedencia del activo'
    )

    # Información de baja
    fecha_baja = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Baja',
        help_text='Fecha en que el activo fue dado de baja'
    )
    motivo_baja = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo de Baja',
        help_text='Razón por la cual el activo fue dado de baja'
    )

    # Información del movimiento
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Movimiento'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    usuario_registro = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_registrados',
        verbose_name='Usuario que Registró'
    )

    class Meta:
        db_table = 'activo_movimiento'
        verbose_name = 'Movimiento de Activo'
        verbose_name_plural = 'Movimientos de Activos'
        ordering = ['-fecha_movimiento']
        permissions = [
            ('registrar_movimiento', 'Puede registrar movimientos de activos'),
            ('ver_historial_movimientos', 'Puede ver historial de movimientos'),
        ]

    def __str__(self):
        ubicacion = self.ubicacion_destino.nombre if self.ubicacion_destino else 'Sin ubicación'
        responsable = self.responsable.get_full_name() if self.responsable else 'Sin responsable'
        return f"{self.activo.codigo} - {ubicacion} - {responsable}"

    def clean(self):
        """Validar que se incluyan los campos requeridos según configuración del activo"""
        from django.core.exceptions import ValidationError
        errors = {}

        if self.activo.requiere_serie and not self.numero_serie:
            errors['numero_serie'] = 'Este activo requiere número de serie'

        if self.activo.requiere_lote and not self.lote:
            errors['lote'] = 'Este activo requiere lote'

        if self.activo.requiere_vencimiento and not self.fecha_vencimiento:
            errors['fecha_vencimiento'] = 'Este activo requiere fecha de vencimiento'

        if self.tipo_movimiento.requiere_ubicacion and not self.ubicacion_destino:
            errors['ubicacion_destino'] = 'Este tipo de movimiento requiere ubicación destino'

        if self.tipo_movimiento.requiere_responsable and not self.responsable:
            errors['responsable'] = 'Este tipo de movimiento requiere responsable'

        if errors:
            raise ValidationError(errors)


class UbicacionActual(models.Model):
    """
    Modelo para mantener la ubicación actual de cada activo (vista rápida).
    Se actualiza automáticamente con cada movimiento.
    """
    activo = models.OneToOneField(
        Activo,
        on_delete=models.CASCADE,
        related_name='ubicacion_actual',
        verbose_name='Activo',
        primary_key=True
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name='activos_actuales',
        verbose_name='Ubicación Actual',
        blank=True,
        null=True
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='activos_a_cargo',
        verbose_name='Responsable Actual',
        blank=True,
        null=True
    )
    ultimo_movimiento = models.ForeignKey(
        MovimientoActivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Último Movimiento'
    )
    fecha_ultima_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )

    class Meta:
        db_table = 'activo_ubicacion_actual'
        verbose_name = 'Ubicación Actual de Activo'
        verbose_name_plural = 'Ubicaciones Actuales de Activos'

    def __str__(self):
        return f"{self.activo.codigo} - {self.ubicacion.nombre if self.ubicacion else 'Sin ubicación'}"
