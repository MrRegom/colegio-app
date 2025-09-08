from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

# Nota: Funcionario se referenciará como string para evitar importación circular

class FirmaCorreo(models.Model):
    """Modelo para gestionar firmas de correo personalizadas"""
    
    # Información del usuario
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='firmas_correo',
        verbose_name="Usuario"
    )
    
    # Información personal
    nombre_completo = models.CharField(
        max_length=200, 
        verbose_name="Nombre Completo",
        help_text="Nombre que aparecerá en la firma"
    )
    cargo = models.CharField(
        max_length=200, 
        verbose_name="Cargo",
        help_text="Cargo o posición que ocupa"
    )
    
    # Información institucional  
    unidad = models.CharField(
        max_length=300, 
        verbose_name="Unidad/Departamento",
        help_text="Unidad o departamento al que pertenece"
    )
    institucion = models.CharField(
        max_length=300, 
        verbose_name="Institución",
        help_text="Nombre de la institución u organización"
    )
    
    # Información de contacto
    telefono = models.CharField(
        max_length=50, 
        verbose_name="Teléfono",
        help_text="Número de teléfono de contacto"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Dirección de correo electrónico"
    )
    website = models.URLField(
        max_length=300, 
        blank=True, 
        verbose_name="Sitio Web",
        help_text="URL del sitio web institucional"
    )
    
    # Configuración de firma
    plantilla = models.CharField(
        max_length=50,
        choices=[
            ('hospital', 'Firma Hospital'),
            ('ministerio', 'Firma Ministerial'), 
            ('simple', 'Firma Simple'),
            ('personalizada', 'Personalizada'),
        ],
        default='hospital',
        verbose_name="Plantilla"
    )
    
    # HTML generado
    html_firma = models.TextField(
        verbose_name="HTML de la Firma",
        help_text="Código HTML completo de la firma generada"
    )
    
    # Logos personalizados
    logo_gobierno = models.ImageField(
        upload_to='firmas/logos/',
        blank=True,
        null=True,
        verbose_name="Logo Gobierno de Chile",
        help_text="Logo del Gobierno de Chile (recomendado: 80x40px, formato PNG)"
    )
    logo_salud = models.ImageField(
        upload_to='firmas/logos/',
        blank=True,
        null=True,
        verbose_name="Logo Servicio de Salud",
        help_text="Logo del Servicio de Salud (recomendado: 80x40px, formato PNG)"
    )
    logo_hospital = models.ImageField(
        upload_to='firmas/logos/',
        blank=True,
        null=True,
        verbose_name="Logo Hospital",
        help_text="Logo del Hospital (recomendado: 60x40px, formato PNG)"
    )
    
    # Configuraciones adicionales
    incluir_logos = models.BooleanField(
        default=True,
        verbose_name="Incluir Logos Institucionales",
        help_text="Mostrar logos del gobierno, servicio de salud y hospital"
    )
    color_principal = models.CharField(
        max_length=7,
        default='#0066cc',
        verbose_name="Color Principal",
        help_text="Color principal de la firma (formato hex: #ffffff)"
    )
    
    # Estado y control
    es_predeterminada = models.BooleanField(
        default=False,
        verbose_name="Firma Predeterminada",
        help_text="Usar esta firma como predeterminada para correos"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Si la firma está disponible para uso"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Modificación"
    )
    
    class Meta:
        db_table = 'correo_masivo_firma'
        verbose_name = 'Firma de Correo'
        verbose_name_plural = 'Firmas de Correo'
        ordering = ['-es_predeterminada', '-fecha_modificacion']
        indexes = [
            models.Index(fields=['usuario', 'activa']),
            models.Index(fields=['es_predeterminada']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['usuario'],
                condition=models.Q(es_predeterminada=True),
                name='unique_default_signature_per_user'
            )
        ]
    
    def __str__(self):
        estado = "✓" if self.es_predeterminada else ""
        return f"{estado} {self.nombre_completo} - {self.cargo}"
    
    def save(self, *args, **kwargs):
        """Override save para asegurar única firma predeterminada por usuario"""
        if self.es_predeterminada:
            # Desactivar otras firmas predeterminadas del mismo usuario
            FirmaCorreo.objects.filter(
                usuario=self.usuario, 
                es_predeterminada=True
            ).exclude(pk=self.pk).update(es_predeterminada=False)
        
        super().save(*args, **kwargs)
    
    def generar_html_firma(self):
        """Genera el HTML de la firma basado en los datos"""
        
        logos_html = ""
        if self.incluir_logos:
            # URLs de logos (personalizados o por defecto)
            from django.conf import settings
            
            # Usar logos subidos o texto por defecto
            if self.logo_gobierno:
                logo_gobierno_html = f'<img src="{self.logo_gobierno.url}" alt="Gobierno de Chile" style="height: 45px; margin-right: 3px;">'
            else:
                logo_gobierno_html = '<div style="background: #0066cc; color: white; padding: 10px 15px; font-size: 10px; font-weight: bold; margin-right: 3px; height: 25px; display: flex; align-items: center;">GOBIERNO<br>DE CHILE</div>'
                
            if self.logo_salud:
                logo_salud_html = f'<img src="{self.logo_salud.url}" alt="Servicio de Salud" style="height: 45px; margin-right: 3px;">'
            else:
                logo_salud_html = '<div style="background: #dc3545; color: white; padding: 10px 15px; font-size: 10px; font-weight: bold; margin-right: 3px; height: 25px; display: flex; align-items: center;">SERVICIO<br>DE SALUD</div>'
                
            if self.logo_hospital:
                logo_hospital_html = f'<img src="{self.logo_hospital.url}" alt="Hospital" style="height: 45px;">'
            else:
                logo_hospital_html = '<div style="background: #ff9500; color: white; padding: 10px 15px; font-size: 10px; font-weight: bold; height: 25px; display: flex; align-items: center;">HOSPITAL</div>'
            
            logos_html = f'''
        <tr>
            <td style="padding: 15px 0 0 0; text-align: left;">
                <div style="display: flex; align-items: center; justify-content: flex-start; gap: 8px; margin-left: 22px;">
                    {logo_gobierno_html}
                    {logo_salud_html}
                    {logo_hospital_html}
                </div>
            </td>
        </tr>'''
        
        # Construir información personal (solo si no está vacía)
        info_personal = ''
        if self.nombre_completo:
            info_personal += f'<div style="color: #333; font-size: 18px; font-weight: bold; margin-bottom: 3px;">{self.nombre_completo}</div>'
        if self.cargo:
            info_personal += f'<div style="color: #666; font-size: 15px; margin-bottom: 8px;">{self.cargo}</div>'

        # Construir información institucional (tamaño más grande)
        info_institucional = ''
        if self.unidad or self.institucion:
            info_institucional = '<div style="color: #666; font-size: 15px; font-weight: 500; margin-bottom: 10px;">'
            if self.unidad:
                info_institucional += f'{self.unidad}'
                if self.institucion:
                    info_institucional += '<br>'
            if self.institucion:
                info_institucional += f'{self.institucion}'
            info_institucional += '</div>'

        # Construir información de contacto
        info_contacto = ''
        if self.telefono or self.email or self.website:
            info_contacto = f'<div style="color: {self.color_principal}; font-size: 13px;">'
            if self.telefono:
                info_contacto += f'📞 Teléfono: {self.telefono}<br>'
            if self.email:
                info_contacto += f'✉️ {self.email}<br>'
            if self.website:
                website_clean = self.website.replace('http://', '').replace('https://', '')
                info_contacto += f'🌐 <a href="{self.website}" style="color: {self.color_principal}; text-decoration: none;">{website_clean}</a>'
            info_contacto += '</div>'
        
        html_firma = f'''
        <table style="font-family: Arial, sans-serif; border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr>
                <td style="padding: 12px 0; vertical-align: top;">
                    <div style="border-left: 4px solid {self.color_principal}; padding-left: 18px;">
                        {info_personal}
                        {info_institucional}
                        {info_contacto}
                    </div>
                </td>
            </tr>
            {logos_html}
        </table>'''
        
        self.html_firma = html_firma
        return html_firma


class PlantillaFirma(models.Model):
    """Plantillas predefinidas para firmas"""
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Plantilla"
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción de la plantilla"
    )
    html_template = models.TextField(
        verbose_name="HTML Template",
        help_text="Plantilla HTML con placeholders"
    )
    color_principal = models.CharField(
        max_length=7,
        default='#0066cc',
        verbose_name="Color Principal"
    )
    incluir_logos = models.BooleanField(
        default=True,
        verbose_name="Incluir Logos por Defecto"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Plantilla Activa"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'correo_masivo_plantilla_firma'
        verbose_name = 'Plantilla de Firma'
        verbose_name_plural = 'Plantillas de Firma'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class ListaRemitentes(models.Model):
    """Modelo para gestionar listas de remitentes de correo masivo"""
    
    # Información básica
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre de la Lista",
        help_text="Nombre descriptivo para identificar la lista de remitentes"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción opcional de la lista de remitentes"
    )
    
    # Relación con usuario creador
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listas_remitentes',
        verbose_name="Usuario Creador"
    )
    
    # Unidad del usuario (se guarda automáticamente)
    unidad = models.CharField(
        max_length=100,
        verbose_name="Unidad del Usuario",
        help_text="Unidad organizacional del usuario que creó la lista"
    )
    
    # Nota: No usamos ManyToManyField directo porque Funcionario está en PostgreSQL (solo lectura)
    # La relación se maneja a través de FuncionarioEnLista con funcionario_id
    
    # Estado
    activa = models.BooleanField(
        default=True,
        verbose_name="Lista Activa"
    )
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'correo_masivo_lista_remitentes'
        verbose_name = 'Lista de Remitentes'
        verbose_name_plural = 'Listas de Remitentes'
        ordering = ['-fecha_modificacion']
        unique_together = [['nombre', 'usuario']]  # Evitar nombres duplicados por usuario
    
    def __str__(self):
        return f"{self.nombre} ({self.usuario.get_full_name() or self.usuario.username})"
    
    def total_funcionarios(self):
        """Retorna el número total de funcionarios en la lista"""
        return FuncionarioEnLista.objects.filter(lista_remitentes=self, activo_en_lista=True).count()
    
    def funcionarios_activos(self):
        """Retorna el número de funcionarios activos en la lista"""
        # Para verificar si están activos, necesitamos consultar PostgreSQL
        funcionarios_ids = FuncionarioEnLista.objects.filter(
            lista_remitentes=self, 
            activo_en_lista=True
        ).values_list('funcionario_id', flat=True)
        
        if not funcionarios_ids:
            return 0
            
        from apps.models import Funcionario
        return Funcionario.objects.using('postgres_db').filter(
            id__in=funcionarios_ids,
            estado='activo', 
            eliminado=False
        ).count()
        
    def get_funcionarios(self):
        """Obtener funcionarios de esta lista desde PostgreSQL"""
        funcionarios_ids = FuncionarioEnLista.objects.filter(
            lista_remitentes=self, 
            activo_en_lista=True
        ).values_list('funcionario_id', flat=True)
        
        if not funcionarios_ids:
            return []
            
        from apps.models import Funcionario
        return Funcionario.objects.using('postgres_db').filter(id__in=funcionarios_ids)


class FuncionarioEnLista(models.Model):
    """Modelo intermedio para la relación entre ListaRemitentes y Funcionario"""
    
    lista_remitentes = models.ForeignKey(
        ListaRemitentes,
        on_delete=models.CASCADE,
        verbose_name="Lista de Remitentes"
    )
    funcionario_id = models.IntegerField(
        verbose_name="ID del Funcionario", 
        help_text="ID del funcionario en PostgreSQL",
        null=True,  # Temporal para migración
        blank=True
    )
    
    # Información adicional
    fecha_agregado = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Agregado"
    )
    agregado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Agregado por"
    )
    activo_en_lista = models.BooleanField(
        default=True,
        verbose_name="Activo en Lista"
    )
    
    class Meta:
        db_table = 'correo_masivo_funcionario_en_lista'
        verbose_name = 'Funcionario en Lista'
        verbose_name_plural = 'Funcionarios en Lista'
        unique_together = [['lista_remitentes', 'funcionario_id']]  # Evitar duplicados
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"Funcionario ID {self.funcionario_id} en {self.lista_remitentes.nombre}"
        
    def get_funcionario(self):
        """Obtener el objeto funcionario desde PostgreSQL"""
        from apps.models import Funcionario
        try:
            return Funcionario.objects.using('postgres_db').get(id=self.funcionario_id)
        except Funcionario.DoesNotExist:
            return None
