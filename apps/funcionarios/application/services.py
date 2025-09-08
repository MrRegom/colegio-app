"""
Services para Funcionarios.

Contiene la lógica de aplicación para operaciones de funcionarios.
"""
from typing import List, Optional

from ..domain.entities import Funcionario, Email
from ..domain.repositories import IFuncionarioRepository


class FuncionarioService:
    """
    Service de aplicación para funcionarios.
    
    Coordina las operaciones del dominio y maneja la lógica de aplicación.
    """

    def __init__(self, funcionario_repository: IFuncionarioRepository):
        self._funcionario_repository = funcionario_repository

    def get_funcionario_by_id(self, funcionario_id: int) -> Optional[Funcionario]:
        """Obtiene un funcionario por ID."""
        return self._funcionario_repository.get_by_id(funcionario_id)

    def get_funcionario_by_email(self, email: Email) -> Optional[Funcionario]:
        """Obtiene un funcionario por email."""
        return self._funcionario_repository.get_by_email(email)

    def get_all_funcionarios(self, include_deleted: bool = False) -> List[Funcionario]:
        """Obtiene todos los funcionarios."""
        return self._funcionario_repository.get_all(include_deleted)

    def get_active_funcionarios(self) -> List[Funcionario]:
        """Obtiene solo los funcionarios activos."""
        return self._funcionario_repository.get_active()

    def search_funcionarios(self, search_term: str, include_deleted: bool = False) -> List[Funcionario]:
        """Busca funcionarios por término."""
        if not search_term or not search_term.strip():
            return self.get_all_funcionarios(include_deleted)
        
        return self._funcionario_repository.search(search_term.strip(), include_deleted)

    def save_funcionario(self, funcionario: Funcionario) -> Funcionario:
        """Guarda un funcionario."""
        return self._funcionario_repository.save(funcionario)

    def delete_funcionario(self, funcionario_id: int) -> bool:
        """Elimina un funcionario."""
        return self._funcionario_repository.delete(funcionario_id)

    def count_total(self) -> int:
        """Cuenta el total de funcionarios activos."""
        return self._funcionario_repository.count_total()

    def count_by_estado(self, estado: str) -> int:
        """Cuenta funcionarios por estado."""
        return self._funcionario_repository.count_by_estado(estado)

    def exists_by_email(self, email: Email, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un funcionario con el email."""
        return self._funcionario_repository.exists_by_email(email, exclude_id)
