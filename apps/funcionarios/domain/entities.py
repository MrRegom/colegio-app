"""
Entidades de Dominio para Funcionarios.

Contiene las entidades principales del dominio de funcionarios.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


# VALUE OBJECTS
@dataclass(frozen=True)
class Email:
    """
    Value Object que representa un email válido.
    
    Los Value Objects son inmutables y se definen por su valor,
    no por su identidad.
    """
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

    @property
    def domain(self) -> str:
        """Retorna el dominio del email."""
        return self.value.split('@')[1]

    @property
    def local_part(self) -> str:
        """Retorna la parte local del email (antes del @)."""
        return self.value.split('@')[0]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Estado:
    """
    Value Object que representa un estado válido del sistema.
    
    Puede ser usado para funcionarios, unidades, etc.
    """
    value: str

    # Estados válidos para diferentes entidades
    ESTADOS_FUNCIONARIO = ['activo', 'inactivo']

    def __post_init__(self):
        """Validación del estado al crear la instancia."""
        if not self.value:
            raise ValueError("El estado no puede estar vacío")
        
        # Normalizar a minúsculas
        object.__setattr__(self, 'value', self.value.lower().strip())

    @classmethod
    def for_funcionario(cls, value: str) -> 'Estado':
        """Crea un estado válido para funcionario."""
        estado = cls(value)
        if estado.value not in cls.ESTADOS_FUNCIONARIO:
            raise ValueError(f"Estado '{value}' no válido para funcionario. Estados válidos: {cls.ESTADOS_FUNCIONARIO}")
        return estado

    def is_active(self) -> bool:
        """Verifica si el estado representa algo activo."""
        return self.value in ['activo', 'activa', 'en_proceso']

    def __str__(self) -> str:
        return self.value


# ENTITIES
@dataclass
class Funcionario:
    """
    Entidad de dominio que representa un funcionario.
    
    Esta clase encapsula toda la lógica de negocio relacionada 
    con un funcionario del sistema.
    """
    id: Optional[int]
    nombres: str
    apellidos: str
    email: Email
    estado: Estado
    eliminado: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.nombres or not self.nombres.strip():
            raise ValueError("Los nombres no pueden estar vacíos")
        
        if not self.apellidos or not self.apellidos.strip():
            raise ValueError("Los apellidos no pueden estar vacíos")

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del funcionario."""
        return f"{self.nombres.strip()} {self.apellidos.strip()}"

    @property
    def is_active(self) -> bool:
        """Verifica si el funcionario está activo."""
        return self.estado.value == 'activo' and not self.eliminado

    def activar(self) -> None:
        """Activa el funcionario."""
        self.estado = Estado.for_funcionario('activo')

    def inactivar(self) -> None:
        """Inactiva el funcionario."""
        self.estado = Estado.for_funcionario('inactivo')

    def eliminar(self) -> None:
        """Marca el funcionario como eliminado (soft delete)."""
        self.eliminado = True
        self.inactivar()

    def cambiar_email(self, nuevo_email: str) -> None:
        """Cambia el email del funcionario."""
        self.email = Email(nuevo_email)

    def __str__(self) -> str:
        return f"Funcionario(id={self.id}, nombre={self.nombre_completo})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Funcionario):
            return False
        return self.id == other.id if self.id and other.id else False
