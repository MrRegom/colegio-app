"""
Use Cases para Funcionarios.

Contiene toda la lógica de aplicación relacionada con funcionarios.
"""
from dataclasses import dataclass
from typing import List, Optional

from .services import FuncionarioService
from ..domain.entities import Funcionario, Email, Estado


@dataclass
class FuncionarioSearchCriteria:
    """Criterios de búsqueda para funcionarios."""
    search_term: Optional[str] = None
    estado: Optional[str] = None
    include_deleted: bool = False


@dataclass
class FuncionarioStats:
    """Estadísticas de funcionarios."""
    total: int
    activos: int
    inactivos: int


class ListFuncionariosUseCase:
    """Use Case para listar funcionarios con filtros."""
    
    def __init__(self, funcionario_service: FuncionarioService):
        self._funcionario_service = funcionario_service

    def execute(self, criteria: FuncionarioSearchCriteria) -> List[Funcionario]:
        """
        Ejecuta la búsqueda de funcionarios según los criterios.
        
        Args:
            criteria: Criterios de búsqueda
            
        Returns:
            Lista de funcionarios que cumplen los criterios
        """
        if criteria.search_term:
            funcionarios = self._funcionario_service.search_funcionarios(
                criteria.search_term, 
                criteria.include_deleted
            )
        else:
            funcionarios = self._funcionario_service.get_all_funcionarios(
                criteria.include_deleted
            )

        # Filtrar por estado si se especifica
        if criteria.estado:
            funcionarios = [f for f in funcionarios if f.estado.value == criteria.estado]

        return funcionarios


class GetFuncionarioStatsUseCase:
    """Use Case para obtener estadísticas de funcionarios."""
    
    def __init__(self, funcionario_service: FuncionarioService):
        self._funcionario_service = funcionario_service

    def execute(self) -> FuncionarioStats:
        """
        Obtiene las estadísticas de funcionarios.
        
        Returns:
            Estadísticas de funcionarios
        """
        return FuncionarioStats(
            total=self._funcionario_service.count_total(),
            activos=self._funcionario_service.count_by_estado('activo'),
            inactivos=self._funcionario_service.count_by_estado('inactivo')
        )


class GetFuncionarioByIdUseCase:
    """Use Case para obtener un funcionario por ID."""
    
    def __init__(self, funcionario_service: FuncionarioService):
        self._funcionario_service = funcionario_service

    def execute(self, funcionario_id: int) -> Optional[Funcionario]:
        """
        Obtiene un funcionario por su ID.
        
        Args:
            funcionario_id: ID del funcionario
            
        Returns:
            Funcionario si existe, None si no
        """
        return self._funcionario_service.get_funcionario_by_id(funcionario_id)


class CreateFuncionarioUseCase:
    """Use Case para crear un nuevo funcionario."""
    
    def __init__(self, funcionario_service: FuncionarioService):
        self._funcionario_service = funcionario_service

    def execute(self, nombres: str, apellidos: str, email: str) -> Funcionario:
        """
        Crea un nuevo funcionario.
        
        Args:
            nombres: Nombres del funcionario
            apellidos: Apellidos del funcionario
            email: Email del funcionario
            
        Returns:
            Funcionario creado
            
        Raises:
            ValueError: Si los datos no son válidos o el email ya existe
        """
        email_vo = Email(email)
        
        # Verificar que el email no exista
        if self._funcionario_service.exists_by_email(email_vo):
            raise ValueError(f"Ya existe un funcionario con el email {email}")

        funcionario = Funcionario(
            id=None,
            nombres=nombres,
            apellidos=apellidos,
            email=email_vo,
            estado=Estado.for_funcionario('activo')
        )

        return self._funcionario_service.save_funcionario(funcionario)


class UpdateFuncionarioUseCase:
    """Use Case para actualizar un funcionario."""
    
    def __init__(self, funcionario_service: FuncionarioService):
        self._funcionario_service = funcionario_service

    def execute(self, funcionario_id: int, nombres: str, apellidos: str, email: str) -> Funcionario:
        """
        Actualiza un funcionario existente.
        
        Args:
            funcionario_id: ID del funcionario
            nombres: Nuevos nombres
            apellidos: Nuevos apellidos
            email: Nuevo email
            
        Returns:
            Funcionario actualizado
            
        Raises:
            ValueError: Si el funcionario no existe o los datos no son válidos
        """
        funcionario = self._funcionario_service.get_funcionario_by_id(funcionario_id)
        if not funcionario:
            raise ValueError(f"No existe funcionario con ID {funcionario_id}")

        new_email = Email(email)
        
        # Verificar que el email no exista (excluyendo el funcionario actual)
        if (new_email.value != funcionario.email.value and 
            self._funcionario_service.exists_by_email(new_email, funcionario_id)):
            raise ValueError(f"Ya existe otro funcionario con el email {email}")

        # Actualizar datos
        funcionario.nombres = nombres
        funcionario.apellidos = apellidos
        funcionario.email = new_email

        return self._funcionario_service.save_funcionario(funcionario)


class DeleteFuncionarioUseCase:
    """Use Case para eliminar un funcionario."""
    
    def __init__(self, funcionario_service: FuncionarioService):
        self._funcionario_service = funcionario_service

    def execute(self, funcionario_id: int) -> bool:
        """
        Elimina (soft delete) un funcionario.
        
        Args:
            funcionario_id: ID del funcionario a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            ValueError: Si el funcionario no existe
        """
        funcionario = self._funcionario_service.get_funcionario_by_id(funcionario_id)
        if not funcionario:
            raise ValueError(f"No existe funcionario con ID {funcionario_id}")

        return self._funcionario_service.delete_funcionario(funcionario_id)
