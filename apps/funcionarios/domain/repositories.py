"""
Repository Interfaces para Funcionarios.

Define los contratos que deben cumplir las implementaciones
de repositorios de funcionarios.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import Funcionario, Email


class IFuncionarioRepository(ABC):
    """
    Interface del repositorio de funcionarios.
    
    Define todas las operaciones que se pueden realizar
    con funcionarios sin importar la implementación específica.
    """

    @abstractmethod
    def get_by_id(self, funcionario_id: int) -> Optional[Funcionario]:
        """Obtiene un funcionario por su ID."""
        pass

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[Funcionario]:
        """Obtiene un funcionario por su email."""
        pass

    @abstractmethod
    def get_all(self, include_deleted: bool = False) -> List[Funcionario]:
        """Obtiene todos los funcionarios."""
        pass

    @abstractmethod
    def get_active(self) -> List[Funcionario]:
        """Obtiene solo los funcionarios activos."""
        pass

    @abstractmethod
    def search(self, search_term: str, include_deleted: bool = False) -> List[Funcionario]:
        """Busca funcionarios por nombres, apellidos o email."""
        pass

    @abstractmethod
    def save(self, funcionario: Funcionario) -> Funcionario:
        """Guarda un funcionario (crear o actualizar)."""
        pass

    @abstractmethod
    def delete(self, funcionario_id: int) -> bool:
        """Elimina (soft delete) un funcionario."""
        pass

    @abstractmethod
    def count_total(self) -> int:
        """Cuenta el total de funcionarios (excluyendo eliminados)."""
        pass

    @abstractmethod
    def count_by_estado(self, estado: str) -> int:
        """Cuenta funcionarios por estado."""
        pass

    @abstractmethod
    def exists_by_email(self, email: Email, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un funcionario con el email dado."""
        pass
