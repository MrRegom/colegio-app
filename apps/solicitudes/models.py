from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from apps.activos.models import Activo
from apps.bodega.models import Bodega, Articulo
from core.models import BaseModel


class Departamento(BaseModel):
    """Catálogo de departamentos de la institución"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='departamentos_responsable',
        verbose_name='Responsable',
        blank=True,
        null=True
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'solicitud_departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Area(BaseModel):
    """Catálogo de áreas dentro de los departamentos"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='areas',
        verbose_name='Departamento'
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='areas_responsable',
        verbose_name='Responsable',
        blank=True,
        null=True
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'solicitud_area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Equipo(BaseModel):
    """Catálogo de equipos de trabajo"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='equipos',
        verbose_name='Departamento'
    )
    lider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='equipos_lider',
        verbose_name='Líder',
        blank=True,
        null=True
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'solicitud_equipo'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoSolicitud(BaseModel):
    """Catálogo de tipos de solicitud"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    requiere_aprobacion = models.BooleanField(default=True, verbose_name='Requiere Aprobación')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'solicitud_tipo'
        verbose_name = 'Tipo de Solicitud'
        verbose_name_plural = 'Tipos de Solicitud'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class EstadoSolicitud(BaseModel):
    """Catálogo de estados de solicitudes"""
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
    requiere_accion = models.BooleanField(default=False, verbose_name='Requiere Acción')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'solicitud_estado'
        verbose_name = 'Estado de Solicitud'
        verbose_name_plural = 'Estados de Solicitudes'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Solicitud(BaseModel):
    """Modelo para gestionar solicitudes de materiales/activos"""

    TIPO_CHOICES = [
        ('ACTIVO', 'Solicitud de Activos/Bienes'),
        ('ARTICULO', 'Solicitud de Artículos'),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='ARTICULO',
        verbose_name='Tipo',
        help_text='Define si la solicitud es de activos (bienes) o artículos'
    )
    numero = models.CharField(max_length=20, unique=True, verbose_name='Número de Solicitud')
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')
    fecha_requerida = models.DateField(verbose_name='Fecha Requerida')

    tipo_solicitud = models.ForeignKey(
        TipoSolicitud,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Tipo de Solicitud'
    )
    estado = models.ForeignKey(
        EstadoSolicitud,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Estado'
    )

    # Información de la actividad
    titulo_actividad = models.CharField(
        max_length=200,
        verbose_name='Título de la Actividad',
        help_text='Título descriptivo de la actividad para la cual se solicitan los materiales',
        blank=True,
        null=True
    )
    objetivo_actividad = models.TextField(
        verbose_name='Objetivo de la Actividad',
        help_text='Objetivo que se busca alcanzar con esta actividad',
        blank=True,
        null=True
    )

    # Solicitante y responsables
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='solicitudes_realizadas',
        verbose_name='Solicitante'
    )
    area_solicitante = models.CharField(max_length=100, verbose_name='Área Solicitante')

    # Referencias a las nuevas estructuras organizacionales
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Departamento',
        blank=True,
        null=True
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Área',
        blank=True,
        null=True
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Equipo',
        blank=True,
        null=True
    )

    aprobador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='solicitudes_aprobadas',
        verbose_name='Aprobador',
        blank=True,
        null=True
    )
    fecha_aprobacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Aprobación'
    )

    despachador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='solicitudes_despachadas',
        verbose_name='Despachador',
        blank=True,
        null=True
    )
    fecha_despacho = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Despacho'
    )

    # Bodega (solo para solicitudes de artículos)
    bodega_origen = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        related_name='solicitudes_origen',
        verbose_name='Bodega Origen',
        blank=True,
        null=True,
        help_text='Solo requerido para solicitudes de artículos. Las solicitudes de activos no tienen bodega.'
    )

    # Descripción y observaciones
    motivo = models.TextField(verbose_name='Motivo de la Solicitud')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    notas_aprobacion = models.TextField(blank=True, null=True, verbose_name='Notas de Aprobación')
    notas_despacho = models.TextField(blank=True, null=True, verbose_name='Notas de Despacho')

    # Auditoria
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')

    class Meta:
        db_table = 'solicitud'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_solicitud', '-numero']
        permissions = [
            ('aprobar_solicitud', 'Puede aprobar solicitudes'),
            ('rechazar_solicitud', 'Puede rechazar solicitudes'),
            ('despachar_solicitud', 'Puede despachar solicitudes'),
            ('change_any_solicitud', 'Puede editar cualquier solicitud'),
            ('delete_any_solicitud', 'Puede eliminar cualquier solicitud'),
            ('ver_todas_solicitudes', 'Puede ver todas las solicitudes'),
        ]

    def __str__(self):
        return f"SOL-{self.numero} - {self.solicitante.correo}"


class DetalleSolicitud(BaseModel):
    """Modelo para el detalle de artículos o bienes solicitados"""
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Solicitud'
    )
    # FK a Artículo de Bodega (para solicitudes de artículos)
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='detalles_solicitud',
        verbose_name='Artículo',
        blank=True,
        null=True
    )
    # FK a Activo/Bien de Inventario (para solicitudes de bienes)
    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name='detalles_solicitud',
        verbose_name='Bien/Activo',
        blank=True,
        null=True
    )
    cantidad_solicitada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Cantidad Solicitada'
    )
    cantidad_aprobada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Aprobada'
    )
    cantidad_despachada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Despachada'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'solicitud_detalle'
        verbose_name = 'Detalle de Solicitud'
        verbose_name_plural = 'Detalles de Solicitudes'
        ordering = ['solicitud', 'id']

    def __str__(self):
        producto = self.articulo or self.activo
        codigo = producto.sku if self.articulo else producto.codigo
        return f"{self.solicitud.numero} - {codigo} ({self.cantidad_solicitada})"

    def clean(self):
        """Validar que solo uno de articulo o activo esté presente"""
        from django.core.exceptions import ValidationError

        if not self.articulo and not self.activo:
            raise ValidationError('Debe especificar un artículo o un bien/activo')

        if self.articulo and self.activo:
            raise ValidationError('No puede especificar tanto artículo como bien/activo simultáneamente')

    @property
    def producto_nombre(self):
        """Retorna el nombre del producto (artículo o activo)"""
        return self.articulo.nombre if self.articulo else self.activo.nombre

    @property
    def producto_codigo(self):
        """Retorna el código del producto (artículo o activo)"""
        return self.articulo.sku if self.articulo else self.activo.codigo


class HistorialSolicitud(BaseModel):
    """Modelo para el historial de cambios de estado de solicitudes"""
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Solicitud'
    )
    estado_anterior = models.ForeignKey(
        EstadoSolicitud,
        on_delete=models.PROTECT,
        related_name='historiales_anterior',
        verbose_name='Estado Anterior',
        blank=True,
        null=True
    )
    estado_nuevo = models.ForeignKey(
        EstadoSolicitud,
        on_delete=models.PROTECT,
        related_name='historiales_nuevo',
        verbose_name='Estado Nuevo'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cambios_estado_solicitud',
        verbose_name='Usuario'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Cambio')

    class Meta:
        db_table = 'solicitud_historial'
        verbose_name = 'Historial de Solicitud'
        verbose_name_plural = 'Historial de Solicitudes'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"{self.solicitud.numero} - {self.estado_nuevo.nombre} ({self.fecha_cambio})"
