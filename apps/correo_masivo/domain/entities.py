"""
Entidades de Dominio para Correo Masivo.

Contiene las entidades principales del dominio de envío masivo de correos.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import re


# ENUMS Y VALUE OBJECTS
class EstadoCorreo(Enum):
    """Estados válidos para un correo masivo."""
    BORRADOR = "borrador"
    PROGRAMADO = "programado"
    EN_PROCESO = "en_proceso"
    PAUSADO = "pausado"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class TipoDestinatario(Enum):
    """Tipos de destinatarios."""
    FUNCIONARIO = "funcionario"
    EXTERNO = "externo"


class EstadoEnvio(Enum):
    """Estados de envío individual."""
    PENDIENTE = "pendiente"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    FALLIDO = "fallido"
    REBOTADO = "rebotado"


@dataclass(frozen=True)
class Email:
    """Value Object que representa un email válido."""
    value: str

    def __post_init__(self):
        """Validación del email al crear la instancia."""
        if not self.value:
            raise ValueError("El email no puede estar vacío")
        
        # Normalizar a minúsculas
        object.__setattr__(self, 'value', self.value.lower().strip())
        
        # Validar formato
        if not self._is_valid_email(self.value):
            raise ValueError(f"El email '{self.value}' no tiene un formato válido")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Valida el formato del email usando regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class FirmaCorreo:
    """Value Object que representa la firma de un correo."""
    nombre: str
    cargo: str
    organizacion: str
    telefono: Optional[str] = None
    email: Optional[str] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la firma no puede estar vacío")
        
        if not self.cargo or not self.cargo.strip():
            raise ValueError("El cargo no puede estar vacío")
            
        if not self.organizacion or not self.organizacion.strip():
            raise ValueError("La organización no puede estar vacía")

        # Normalizar campos
        object.__setattr__(self, 'nombre', self.nombre.strip())
        object.__setattr__(self, 'cargo', self.cargo.strip())
        object.__setattr__(self, 'organizacion', self.organizacion.strip())

    def generar_html(self) -> str:
        """Genera la firma en formato HTML."""
        html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; color: #333;">
            <p><strong>{self.nombre}</strong><br>
            {self.cargo}<br>
            {self.organizacion}</p>
        """
        
        if self.telefono:
            html += f"<p>Tel: {self.telefono}</p>"
        
        if self.email:
            html += f"<p>Email: <a href='mailto:{self.email}'>{self.email}</a></p>"
        
        html += "</div>"
        return html.strip()

    def __str__(self) -> str:
        return f"{self.nombre} - {self.cargo}"


# ENTIDADES
@dataclass
class Destinatario:
    """
    Entidad que representa un destinatario de correo.
    
    Puede ser un funcionario interno o un contacto externo.
    """
    id: Optional[int]
    email: Email
    nombre_completo: str
    tipo: TipoDestinatario
    funcionario_id: Optional[int] = None  # Si es funcionario interno
    metadatos: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo no puede estar vacío")
        
        # Normalizar nombre
        self.nombre_completo = self.nombre_completo.strip()
        
        # Validar consistencia
        if self.tipo == TipoDestinatario.FUNCIONARIO and not self.funcionario_id:
            raise ValueError("Los destinatarios tipo funcionario deben tener funcionario_id")

    @property
    def is_funcionario(self) -> bool:
        """Verifica si es un funcionario interno."""
        return self.tipo == TipoDestinatario.FUNCIONARIO

    def agregar_metadato(self, clave: str, valor: Any) -> None:
        """Agrega un metadato al destinatario."""
        self.metadatos[clave] = valor

    def __str__(self) -> str:
        return f"Destinatario({self.nombre_completo} - {self.email.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Destinatario):
            return False
        return self.id == other.id if self.id and other.id else False


@dataclass
class CorreoMasivo:
    """
    Entidad principal que representa un envío masivo de correo.
    
    Coordina el envío a múltiples destinatarios.
    """
    id: Optional[int]
    asunto: str
    contenido_html: str
    contenido_texto: str
    remitente_email: Email
    remitente_nombre: str
    firma: FirmaCorreo
    estado: EstadoCorreo
    usuario_creador_id: int
    unidad_id: int
    programado_para: Optional[datetime] = None
    destinatarios_ids: List[int] = field(default_factory=list)
    adjuntos_paths: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    enviado_at: Optional[datetime] = None
    finalizado_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.asunto or not self.asunto.strip():
            raise ValueError("El asunto no puede estar vacío")
        
        if not self.contenido_html or not self.contenido_html.strip():
            raise ValueError("El contenido HTML no puede estar vacío")
        
        if not self.remitente_nombre or not self.remitente_nombre.strip():
            raise ValueError("El nombre del remitente no puede estar vacío")

        # Normalizar campos
        self.asunto = self.asunto.strip()
        self.remitente_nombre = self.remitente_nombre.strip()

    @property
    def puede_ser_editado(self) -> bool:
        """Verifica si el correo puede ser editado."""
        return self.estado in [EstadoCorreo.BORRADOR, EstadoCorreo.PROGRAMADO, EstadoCorreo.PAUSADO]

    @property
    def puede_ser_enviado(self) -> bool:
        """Verifica si el correo puede ser enviado."""
        return (self.estado in [EstadoCorreo.BORRADOR, EstadoCorreo.PROGRAMADO, EstadoCorreo.PAUSADO] and
                len(self.destinatarios_ids) > 0)

    @property
    def esta_terminado(self) -> bool:
        """Verifica si el envío ya terminó."""
        return self.estado in [EstadoCorreo.FINALIZADO, EstadoCorreo.CANCELADO]

    def programar_envio(self, fecha_programada: datetime) -> None:
        """Programa el correo para envío futuro."""
        if not self.puede_ser_editado:
            raise ValueError(f"No se puede programar un correo en estado {self.estado.value}")
        
        if fecha_programada <= datetime.now():
            raise ValueError("La fecha programada debe ser futura")
        
        self.programado_para = fecha_programada
        self.estado = EstadoCorreo.PROGRAMADO

    def iniciar_envio(self) -> None:
        """Inicia el proceso de envío."""
        if not self.puede_ser_enviado:
            raise ValueError(f"No se puede enviar correo en estado {self.estado.value}")
        
        self.estado = EstadoCorreo.EN_PROCESO
        self.enviado_at = datetime.now()

    def pausar_envio(self) -> None:
        """Pausa el envío en proceso."""
        if self.estado != EstadoCorreo.EN_PROCESO:
            raise ValueError("Solo se pueden pausar envíos en proceso")
        
        self.estado = EstadoCorreo.PAUSADO

    def reanudar_envio(self) -> None:
        """Reanuda un envío pausado."""
        if self.estado != EstadoCorreo.PAUSADO:
            raise ValueError("Solo se pueden reanudar envíos pausados")
        
        self.estado = EstadoCorreo.EN_PROCESO

    def finalizar_envio(self) -> None:
        """Marca el envío como finalizado."""
        if self.estado != EstadoCorreo.EN_PROCESO:
            raise ValueError("Solo se pueden finalizar envíos en proceso")
        
        self.estado = EstadoCorreo.FINALIZADO
        self.finalizado_at = datetime.now()

    def cancelar_envio(self) -> None:
        """Cancela el envío."""
        if self.esta_terminado:
            raise ValueError("No se puede cancelar un envío ya terminado")
        
        self.estado = EstadoCorreo.CANCELADO

    def agregar_destinatario(self, destinatario_id: int) -> None:
        """Agrega un destinatario al correo."""
        if not self.puede_ser_editado:
            raise ValueError("No se pueden agregar destinatarios a un correo no editable")
        
        if destinatario_id not in self.destinatarios_ids:
            self.destinatarios_ids.append(destinatario_id)

    def remover_destinatario(self, destinatario_id: int) -> None:
        """Remueve un destinatario del correo."""
        if not self.puede_ser_editado:
            raise ValueError("No se pueden remover destinatarios de un correo no editable")
        
        if destinatario_id in self.destinatarios_ids:
            self.destinatarios_ids.remove(destinatario_id)

    def agregar_adjunto(self, archivo_path: str) -> None:
        """Agrega un archivo adjunto."""
        if not self.puede_ser_editado:
            raise ValueError("No se pueden agregar adjuntos a un correo no editable")
        
        if archivo_path not in self.adjuntos_paths:
            self.adjuntos_paths.append(archivo_path)

    def generar_contenido_final(self) -> str:
        """Genera el contenido final del correo con firma."""
        contenido_final = self.contenido_html
        
        # Agregar firma al final
        contenido_final += "<br><br>" + self.firma.generar_html()
        
        return contenido_final

    def __str__(self) -> str:
        return f"CorreoMasivo(id={self.id}, asunto={self.asunto}, estado={self.estado.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, CorreoMasivo):
            return False
        return self.id == other.id if self.id and other.id else False


@dataclass
class EnvioIndividual:
    """
    Entidad que representa el envío individual a un destinatario.
    
    Registra el estado y metadatos de cada envío específico.
    """
    id: Optional[int]
    correo_masivo_id: int
    destinatario_id: int
    estado: EstadoEnvio
    intentos: int = 0
    ultimo_error: Optional[str] = None
    enviado_at: Optional[datetime] = None
    entregado_at: Optional[datetime] = None
    abierto_at: Optional[datetime] = None
    click_at: Optional[datetime] = None
    metadatos: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def marcar_como_enviado(self) -> None:
        """Marca el envío como enviado exitosamente."""
        self.estado = EstadoEnvio.ENVIADO
        self.enviado_at = datetime.now()

    def marcar_como_entregado(self) -> None:
        """Marca el envío como entregado."""
        if self.estado != EstadoEnvio.ENVIADO:
            raise ValueError("Solo se pueden marcar como entregados los envíos enviados")
        
        self.estado = EstadoEnvio.ENTREGADO
        self.entregado_at = datetime.now()

    def marcar_como_fallido(self, error: str) -> None:
        """Marca el envío como fallido."""
        self.estado = EstadoEnvio.FALLIDO
        self.ultimo_error = error
        self.intentos += 1

    def marcar_como_rebotado(self, razon: str) -> None:
        """Marca el envío como rebotado."""
        self.estado = EstadoEnvio.REBOTADO
        self.ultimo_error = razon

    def registrar_apertura(self) -> None:
        """Registra que el correo fue abierto."""
        if not self.abierto_at:
            self.abierto_at = datetime.now()

    def registrar_click(self) -> None:
        """Registra que se hizo click en el correo."""
        if not self.click_at:
            self.click_at = datetime.now()

    @property
    def puede_reintentarse(self) -> bool:
        """Verifica si se puede reintentar el envío."""
        return self.estado == EstadoEnvio.FALLIDO and self.intentos < 3

    def __str__(self) -> str:
        return f"EnvioIndividual(correo={self.correo_masivo_id}, destinatario={self.destinatario_id}, estado={self.estado.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, EnvioIndividual):
            return False
        return self.id == other.id if self.id and other.id else False
