"""
Entidades de Dominio para Accounts.

Contiene las entidades principales del dominio de gestión de usuarios.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import re


# ENUMS Y VALUE OBJECTS
class EstadoUnidad(Enum):
    """Estados válidos para una unidad."""
    ACTIVA = "activa"
    INACTIVA = "inactiva"


class EstadoUsuario(Enum):
    """Estados válidos para un usuario."""
    ACTIVO = "activo"
    INACTIVO = "inactivo"


class RolUsuario(Enum):
    """Roles válidos para un usuario."""
    ADMIN = "admin"
    USUARIO = "usuario"


class TipoAccion(Enum):
    """Tipos de acciones para auditoría."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREAR_USUARIO = "CREAR_USUARIO"
    ACTUALIZAR_USUARIO = "ACTUALIZAR_USUARIO"
    ELIMINAR_USUARIO = "ELIMINAR_USUARIO"
    CREAR_UNIDAD = "CREAR_UNIDAD"
    ACTUALIZAR_UNIDAD = "ACTUALIZAR_UNIDAD"
    CREAR_CORREO = "CREAR_CORREO"
    ENVIAR_CORREO = "ENVIAR_CORREO"
    CANCELAR_CORREO = "CANCELAR_CORREO"


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
class NombreCompleto:
    """Value Object que representa un nombre completo válido."""
    nombres: str
    apellidos: str

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.nombres or not self.nombres.strip():
            raise ValueError("Los nombres no pueden estar vacíos")
        
        if not self.apellidos or not self.apellidos.strip():
            raise ValueError("Los apellidos no pueden estar vacíos")
        
        # Normalizar espacios
        object.__setattr__(self, 'nombres', self.nombres.strip())
        object.__setattr__(self, 'apellidos', self.apellidos.strip())

    @property
    def completo(self) -> str:
        """Retorna el nombre completo."""
        return f"{self.nombres} {self.apellidos}"

    def __str__(self) -> str:
        return self.completo


# ENTIDADES
@dataclass
class Unidad:
    """
    Entidad de dominio que representa una unidad organizacional.
    
    Las unidades agrupan usuarios y controlan la visibilidad de datos.
    """
    id: Optional[int]
    nombre: str
    estado: EstadoUnidad
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la unidad no puede estar vacío")
        
        # Normalizar nombre
        self.nombre = self.nombre.strip()

    @property
    def is_active(self) -> bool:
        """Verifica si la unidad está activa."""
        return self.estado == EstadoUnidad.ACTIVA

    def activar(self) -> None:
        """Activa la unidad."""
        self.estado = EstadoUnidad.ACTIVA

    def inactivar(self) -> None:
        """Inactiva la unidad."""
        self.estado = EstadoUnidad.INACTIVA

    def cambiar_nombre(self, nuevo_nombre: str) -> None:
        """Cambia el nombre de la unidad."""
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValueError("El nuevo nombre no puede estar vacío")
        self.nombre = nuevo_nombre.strip()

    def __str__(self) -> str:
        return f"Unidad(id={self.id}, nombre={self.nombre}, estado={self.estado.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Unidad):
            return False
        return self.id == other.id if self.id and other.id else False


@dataclass
class UsuarioSistema:
    """
    Entidad de dominio que representa un usuario del sistema.
    
    Los usuarios pertenecen a una unidad y tienen roles específicos.
    """
    id: Optional[int]
    username: str
    email: Email
    nombre_completo: NombreCompleto
    unidad_id: int  # Referencia a Unidad (evitar dependencia circular)
    rol: RolUsuario
    estado: EstadoUsuario
    is_django_active: bool = True  # Para compatibilidad con Django auth
    permisos_especiales: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.username or not self.username.strip():
            raise ValueError("El username no puede estar vacío")
        
        # Normalizar username
        self.username = self.username.strip().lower()
        
        if len(self.username) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")

    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo."""
        return (self.estado == EstadoUsuario.ACTIVO and 
                self.is_django_active)

    @property
    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador."""
        return self.rol == RolUsuario.ADMIN

    def activar(self) -> None:
        """Activa el usuario."""
        self.estado = EstadoUsuario.ACTIVO

    def inactivar(self) -> None:
        """Inactiva el usuario."""
        self.estado = EstadoUsuario.INACTIVO

    def cambiar_rol(self, nuevo_rol: RolUsuario) -> None:
        """Cambia el rol del usuario."""
        self.rol = nuevo_rol

    def cambiar_email(self, nuevo_email: str) -> None:
        """Cambia el email del usuario."""
        self.email = Email(nuevo_email)

    def cambiar_nombre(self, nombres: str, apellidos: str) -> None:
        """Cambia el nombre del usuario."""
        self.nombre_completo = NombreCompleto(nombres, apellidos)

    def asignar_unidad(self, unidad_id: int) -> None:
        """Asigna el usuario a una unidad."""
        if unidad_id <= 0:
            raise ValueError("El ID de unidad debe ser positivo")
        self.unidad_id = unidad_id

    def agregar_permiso(self, permiso: str) -> None:
        """Agrega un permiso especial al usuario."""
        if permiso and permiso not in self.permisos_especiales:
            self.permisos_especiales.append(permiso)

    def remover_permiso(self, permiso: str) -> None:
        """Remueve un permiso especial del usuario."""
        if permiso in self.permisos_especiales:
            self.permisos_especiales.remove(permiso)

    def tiene_permiso(self, permiso: str) -> bool:
        """Verifica si el usuario tiene un permiso específico."""
        # Los admins tienen todos los permisos
        if self.is_admin:
            return True
        
        return permiso in self.permisos_especiales

    def puede_gestionar_unidad(self) -> bool:
        """Verifica si puede gestionar usuarios de su unidad."""
        return self.tiene_permiso("can_manage_unit_users")

    def puede_crear_correos_masivos(self) -> bool:
        """Verifica si puede crear envíos masivos."""
        return self.tiene_permiso("can_create_mass_emails")

    def puede_ver_reportes_unidad(self) -> bool:
        """Verifica si puede ver reportes de su unidad."""
        return self.tiene_permiso("can_view_unit_reports")

    def __str__(self) -> str:
        return f"Usuario(id={self.id}, username={self.username}, rol={self.rol.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, UsuarioSistema):
            return False
        return self.id == other.id if self.id and other.id else False


@dataclass
class EventoAuditoria:
    """
    Entidad de dominio que representa un evento de auditoría.
    
    Registra todas las acciones importantes del sistema para trazabilidad.
    """
    id: Optional[int]
    usuario_id: Optional[int]  # Referencia a UsuarioSistema
    accion: TipoAccion
    entidad: str  # Tipo de entidad afectada
    entidad_id: Optional[int]  # ID de la entidad afectada
    descripcion: str
    valores_previos: Optional[Dict[str, Any]] = None
    valores_nuevos: Optional[Dict[str, Any]] = None
    ip_remota: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.entidad or not self.entidad.strip():
            raise ValueError("La entidad no puede estar vacía")
        
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")
        
        # Normalizar campos
        self.entidad = self.entidad.strip()
        self.descripcion = self.descripcion.strip()

    @classmethod
    def crear_evento_login(cls, usuario_id: int, ip_remota: str, user_agent: str) -> 'EventoAuditoria':
        """Factory method para crear evento de login."""
        return cls(
            id=None,
            usuario_id=usuario_id,
            accion=TipoAccion.LOGIN,
            entidad="UsuarioSistema",
            entidad_id=usuario_id,
            descripcion=f"Usuario logueado desde IP {ip_remota}",
            ip_remota=ip_remota,
            user_agent=user_agent
        )

    @classmethod
    def crear_evento_usuario(cls, usuario_id: int, accion: TipoAccion, 
                           usuario_afectado_id: int, descripcion: str,
                           valores_previos: Optional[Dict] = None,
                           valores_nuevos: Optional[Dict] = None) -> 'EventoAuditoria':
        """Factory method para crear eventos relacionados con usuarios."""
        return cls(
            id=None,
            usuario_id=usuario_id,
            accion=accion,
            entidad="UsuarioSistema",
            entidad_id=usuario_afectado_id,
            descripcion=descripcion,
            valores_previos=valores_previos,
            valores_nuevos=valores_nuevos
        )

    def es_evento_critico(self) -> bool:
        """Verifica si es un evento crítico que requiere atención."""
        eventos_criticos = [
            TipoAccion.CREAR_USUARIO,
            TipoAccion.ELIMINAR_USUARIO,
            TipoAccion.CREAR_UNIDAD
        ]
        return self.accion in eventos_criticos

    def __str__(self) -> str:
        usuario_str = f"Usuario({self.usuario_id})" if self.usuario_id else "Sistema"
        return f"Evento({self.accion.value}, {usuario_str}, {self.entidad})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, EventoAuditoria):
            return False
        return self.id == other.id if self.id and other.id else False
