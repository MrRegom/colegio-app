from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


class TipoNotificacion(BaseModel):
    """Catálogo de tipos de notificaciones"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    icono = models.CharField(
        max_length=50,
        default='bell',
        verbose_name='Icono',
        help_text='Nombre del icono a mostrar'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Color (Hex)'
    )
    prioridad = models.CharField(
        max_length=10,
        choices=[
            ('BAJA', 'Baja'),
            ('MEDIA', 'Media'),
            ('ALTA', 'Alta'),
            ('URGENTE', 'Urgente'),
        ],
        default='MEDIA',
        verbose_name='Prioridad'
    )
    enviar_email = models.BooleanField(
        default=False,
        verbose_name='Enviar Email',
        help_text='Indica si se debe enviar email además de notificación en el sistema'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        db_table = 'notificacion_tipo'
        verbose_name = 'Tipo de Notificación'
        verbose_name_plural = 'Tipos de Notificaciones'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Notificacion(BaseModel):
    """Modelo para gestionar notificaciones del sistema"""
    tipo = models.ForeignKey(
        TipoNotificacion,
        on_delete=models.PROTECT,
        related_name='notificaciones',
        verbose_name='Tipo'
    )
    usuario_destino = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones_recibidas',
        verbose_name='Usuario Destino'
    )
    usuario_origen = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='notificaciones_enviadas',
        verbose_name='Usuario Origen',
        blank=True,
        null=True
    )

    # Contenido
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje')
    enlace = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Enlace',
        help_text='URL a la que debe redirigir la notificación'
    )

    # Referencias
    modulo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Módulo',
        help_text='Módulo del sistema relacionado (compras, solicitudes, etc.)'
    )
    referencia_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='ID de Referencia',
        help_text='ID del objeto relacionado'
    )
    referencia_tipo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Tipo de Referencia',
        help_text='Tipo de objeto relacionado (OrdenCompra, Solicitud, etc.)'
    )

    # Estado
    leida = models.BooleanField(default=False, verbose_name='Leída')
    fecha_lectura = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Lectura'
    )
    archivada = models.BooleanField(default=False, verbose_name='Archivada')

    # Email
    email_enviado = models.BooleanField(default=False, verbose_name='Email Enviado')
    fecha_envio_email = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Envío Email'
    )

    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_expiracion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Expiración',
        help_text='Fecha después de la cual la notificación se oculta automáticamente'
    )

    class Meta:
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario_destino', '-fecha_creacion']),
            models.Index(fields=['usuario_destino', 'leida']),
            models.Index(fields=['tipo', '-fecha_creacion']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario_destino.correo}"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            from django.utils import timezone
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])


class ConfiguracionNotificacion(BaseModel):
    """Modelo para configurar preferencias de notificaciones por usuario"""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='configuracion_notificaciones',
        verbose_name='Usuario'
    )
    tipo_notificacion = models.ForeignKey(
        TipoNotificacion,
        on_delete=models.CASCADE,
        related_name='configuraciones',
        verbose_name='Tipo de Notificación'
    )

    # Configuración
    notificacion_sistema = models.BooleanField(
        default=True,
        verbose_name='Notificación en Sistema',
        help_text='Recibir notificaciones en el sistema'
    )
    notificacion_email = models.BooleanField(
        default=True,
        verbose_name='Notificación por Email',
        help_text='Recibir notificaciones por correo electrónico'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')

    class Meta:
        db_table = 'notificacion_configuracion'
        verbose_name = 'Configuración de Notificación'
        verbose_name_plural = 'Configuraciones de Notificaciones'
        unique_together = [['usuario', 'tipo_notificacion']]
        ordering = ['usuario', 'tipo_notificacion']

    def __str__(self):
        return f"{self.usuario.correo} - {self.tipo_notificacion.nombre}"
