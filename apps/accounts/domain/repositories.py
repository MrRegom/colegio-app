"""
Repository Interfaces para Accounts.

Define los contratos que deben cumplir las implementaciones
de repositorios de usuarios, unidades y auditoría.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from .entities import (
    UsuarioSistema, 
    Unidad, 
    EventoAuditoria, 
    Email, 
    RolUsuario, 
    EstadoUsuario,
    EstadoUnidad,
    TipoAccion
)


class IUnidadRepository(ABC):
    """
    Interface del repositorio de unidades.
    
    Define todas las operaciones que se pueden realizar
    con unidades sin importar la implementación específica.
    """

    @abstractmethod
    def get_by_id(self, unidad_id: int) -> Optional[Unidad]:
        """Obtiene una unidad por su ID."""
        pass

    @abstractmethod
    def get_by_nombre(self, nombre: str) -> Optional[Unidad]:
        """Obtiene una unidad por su nombre."""
        pass

    @abstractmethod
    def get_all(self) -> List[Unidad]:
        """Obtiene todas las unidades."""
        pass

    @abstractmethod
    def get_activas(self) -> List[Unidad]:
        """Obtiene solo las unidades activas."""
        pass

    @abstractmethod
    def save(self, unidad: Unidad) -> Unidad:
        """Guarda una unidad (crear o actualizar)."""
        pass

    @abstractmethod
    def delete(self, unidad_id: int) -> bool:
        """Elimina una unidad."""
        pass

    @abstractmethod
    def count_total(self) -> int:
        """Cuenta el total de unidades."""
        pass

    @abstractmethod
    def count_activas(self) -> int:
        """Cuenta las unidades activas."""
        pass

    @abstractmethod
    def exists_by_nombre(self, nombre: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe una unidad con el nombre dado."""
        pass


class IUsuarioSistemaRepository(ABC):
    """
    Interface del repositorio de usuarios del sistema.
    
    Define todas las operaciones que se pueden realizar
    con usuarios sin importar la implementación específica.
    """

    @abstractmethod
    def get_by_id(self, usuario_id: int) -> Optional[UsuarioSistema]:
        """Obtiene un usuario por su ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UsuarioSistema]:
        """Obtiene un usuario por su username."""
        pass

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[UsuarioSistema]:
        """Obtiene un usuario por su email."""
        pass

    @abstractmethod
    def get_all(self) -> List[UsuarioSistema]:
        """Obtiene todos los usuarios."""
        pass

    @abstractmethod
    def get_activos(self) -> List[UsuarioSistema]:
        """Obtiene solo los usuarios activos."""
        pass

    @abstractmethod
    def get_by_unidad(self, unidad_id: int) -> List[UsuarioSistema]:
        """Obtiene usuarios de una unidad específica."""
        pass

    @abstractmethod
    def get_by_rol(self, rol: RolUsuario) -> List[UsuarioSistema]:
        """Obtiene usuarios por rol."""
        pass

    @abstractmethod
    def get_administradores(self) -> List[UsuarioSistema]:
        """Obtiene todos los administradores."""
        pass

    @abstractmethod
    def search(self, search_term: str) -> List[UsuarioSistema]:
        """Busca usuarios por username, email o nombre."""
        pass

    @abstractmethod
    def save(self, usuario: UsuarioSistema) -> UsuarioSistema:
        """Guarda un usuario (crear o actualizar)."""
        pass

    @abstractmethod
    def delete(self, usuario_id: int) -> bool:
        """Elimina un usuario."""
        pass

    @abstractmethod
    def count_total(self) -> int:
        """Cuenta el total de usuarios."""
        pass

    @abstractmethod
    def count_by_estado(self, estado: EstadoUsuario) -> int:
        """Cuenta usuarios por estado."""
        pass

    @abstractmethod
    def count_by_unidad(self, unidad_id: int) -> int:
        """Cuenta usuarios de una unidad."""
        pass

    @abstractmethod
    def exists_by_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un usuario con el username dado."""
        pass

    @abstractmethod
    def exists_by_email(self, email: Email, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un usuario con el email dado."""
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[UsuarioSistema]:
        """Autentica un usuario con username y password."""
        pass

    @abstractmethod
    def change_password(self, usuario_id: int, new_password: str) -> bool:
        """Cambia la contraseña de un usuario."""
        pass


class IAuditoriaRepository(ABC):
    """
    Interface del repositorio de auditoría.
    
    Define todas las operaciones que se pueden realizar
    con logs de auditoría sin importar la implementación específica.
    """

    @abstractmethod
    def save(self, evento: EventoAuditoria) -> EventoAuditoria:
        """Guarda un evento de auditoría."""
        pass

    @abstractmethod
    def get_by_usuario(self, usuario_id: int, limit: int = 100) -> List[EventoAuditoria]:
        """Obtiene eventos de auditoría de un usuario."""
        pass

    @abstractmethod
    def get_by_entidad(self, entidad: str, entidad_id: int) -> List[EventoAuditoria]:
        """Obtiene eventos de auditoría de una entidad específica."""
        pass

    @abstractmethod
    def get_by_accion(self, accion: TipoAccion, limit: int = 100) -> List[EventoAuditoria]:
        """Obtiene eventos de auditoría por tipo de acción."""
        pass

    @abstractmethod
    def get_eventos_criticos(self, desde: datetime, hasta: datetime) -> List[EventoAuditoria]:
        """Obtiene eventos críticos en un rango de fechas."""
        pass

    @abstractmethod
    def get_recent(self, limit: int = 50) -> List[EventoAuditoria]:
        """Obtiene los eventos más recientes."""
        pass

    @abstractmethod
    def count_by_accion(self, accion: TipoAccion, desde: datetime, hasta: datetime) -> int:
        """Cuenta eventos por acción en un rango de fechas."""
        pass

    @abstractmethod
    def search(self, search_term: str, limit: int = 100) -> List[EventoAuditoria]:
        """Busca eventos por descripción o entidad."""
        pass

    @abstractmethod
    def cleanup_old_events(self, older_than_days: int) -> int:
        """Limpia eventos antiguos y retorna la cantidad eliminada."""
        pass


class IPermisosRepository(ABC):
    """
    Interface del repositorio de permisos.
    
    Define operaciones para gestionar permisos de usuarios.
    """

    @abstractmethod
    def get_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene todos los permisos de un usuario."""
        pass

    @abstractmethod
    def asignar_permiso(self, usuario_id: int, permiso: str) -> bool:
        """Asigna un permiso a un usuario."""
        pass

    @abstractmethod
    def remover_permiso(self, usuario_id: int, permiso: str) -> bool:
        """Remueve un permiso de un usuario."""
        pass

    @abstractmethod
    def usuario_tiene_permiso(self, usuario_id: int, permiso: str) -> bool:
        """Verifica si un usuario tiene un permiso específico."""
        pass

    @abstractmethod
    def get_usuarios_con_permiso(self, permiso: str) -> List[int]:
        """Obtiene IDs de usuarios que tienen un permiso específico."""
        pass

    @abstractmethod
    def copiar_permisos(self, usuario_origen_id: int, usuario_destino_id: int) -> bool:
        """Copia permisos de un usuario a otro."""
        pass
