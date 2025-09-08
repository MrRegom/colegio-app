from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.utils import timezone


class Unidad(models.Model):
    """
    Catálogo de unidades (Informática, Esterilización, etc.).
    Equivale a la tabla 'unidad' del esquema SQL.
    """
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]
    
    nombre = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nombre único de la unidad."
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='activa',
        help_text="Estado lógico de la unidad: activa o inactiva."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha/hora de creación del registro."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha/hora de última actualización."
    )

    class Meta:
        db_table = 'unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.estado})"


class UsuarioSistema(AbstractUser):
    """
    Cuentas que acceden al sistema; cada una asociada a una unidad.
    Extiende AbstractUser de Django para aprovechar el sistema de autenticación.
    Equivale a la tabla 'usuario_sistema' del esquema SQL.
    """
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    # Campos adicionales al User estándar de Django
    nombres = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombres del usuario."
    )
    apellidos = models.CharField(
        max_length=255,
        blank=True,
        help_text="Apellidos del usuario."
    )
    unidad = models.ForeignKey(
        Unidad,
        on_delete=models.RESTRICT,
        help_text="FK a unidad; determina visibilidad de listas y envíos."
    )
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        default='usuario',
        help_text="Rol de acceso: admin o usuario."
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='activo',
        help_text="Estado de la cuenta: activo o inactivo."
    )
    
    # Sobrescribir el campo email para hacerlo obligatorio
    email = models.EmailField(
        unique=True,
        validators=[validate_email],
        help_text="Correo del usuario (único)."
    )
    
    # Timestamps adicionales
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha/hora de creación."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha/hora de última actualización."
    )

    class Meta:
        db_table = 'usuario_sistema'
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'
        ordering = ['username']
        permissions = [
            ("can_manage_unit_users", "Puede gestionar usuarios de su unidad"),
            ("can_view_unit_reports", "Puede ver reportes de su unidad"),
            ("can_create_mass_emails", "Puede crear envíos masivos de correo"),
            ("can_manage_email_lists", "Puede gestionar listas de correo"),
            ("can_view_email_analytics", "Puede ver analíticas de envíos"),
            ("can_manage_email_templates", "Puede gestionar plantillas de correo"),
        ]

    def __str__(self):
        nombre_completo = f"{self.nombres} {self.apellidos}".strip()
        if nombre_completo:
            return f"{self.username} - {nombre_completo} ({self.unidad.nombre})"
        return f"{self.username} ({self.unidad.nombre})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombres} {self.apellidos}".strip()
    
    def is_admin(self):
        """Verifica si el usuario tiene rol de administrador."""
        return self.rol == 'admin'
    
    def is_active_user(self):
        """Verifica si el usuario está activo."""
        return self.estado == 'activo' and self.is_active


# Modelo auxiliar para auditoría de acciones de usuario
class LogAuditoria(models.Model):
    """
    Registro detallado de acciones de usuarios para trazabilidad.
    Equivale a la tabla 'log_auditoria' del esquema SQL.
    """
    usuario = models.ForeignKey(
        UsuarioSistema,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que ejecutó la acción."
    )
    accion = models.CharField(
        max_length=100,
        help_text="Tipo de acción ejecutada (LOGIN, CREAR_LISTA, etc.)."
    )
    entidad = models.CharField(
        max_length=100,
        help_text="Entidad afectada (tabla/objeto lógico)."
    )
    entidad_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Identificador de la entidad afectada."
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción legible para auditoría."
    )
    valores_previos = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos previos (JSON) antes del cambio."
    )
    valores_nuevos = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos nuevos (JSON) después del cambio."
    )
    ip_remota = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP desde donde se ejecutó la acción."
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Agente de usuario (navegador/cliente)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha/hora de registro del evento."
    )

    class Meta:
        db_table = 'log_auditoria'
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entidad', 'entidad_id'], name='idx_log_entidad'),
            models.Index(fields=['usuario', '-created_at'], name='idx_log_usuario'),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'Sistema'
        return f"{usuario_str} - {self.accion} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"