"""
Implementación Django del repositorio de funcionarios.

Adapter que conecta el dominio con la base de datos usando Django ORM.
"""
from typing import List, Optional
from django.db import models as django_models

from ..domain.entities import Funcionario, Email, Estado
from ..domain.repositories import IFuncionarioRepository
from .models import Funcionario as DjangoFuncionario


class DjangoFuncionarioRepository(IFuncionarioRepository):
    """
    Implementación del repositorio de funcionarios usando Django ORM.
    
    Este adapter traduce entre las entidades de dominio y los modelos Django.
    """

    def get_by_id(self, funcionario_id: int) -> Optional[Funcionario]:
        """Obtiene un funcionario por su ID."""
        try:
            django_funcionario = DjangoFuncionario.objects.using('postgres_db').get(id=funcionario_id)
            return self._to_domain_entity(django_funcionario)
        except DjangoFuncionario.DoesNotExist:
            return None

    def get_by_email(self, email: Email) -> Optional[Funcionario]:
        """Obtiene un funcionario por su email."""
        try:
            django_funcionario = DjangoFuncionario.objects.using('postgres_db').get(
                email=email.value, 
                eliminado=False
            )
            return self._to_domain_entity(django_funcionario)
        except DjangoFuncionario.DoesNotExist:
            return None

    def get_all(self, include_deleted: bool = False) -> List[Funcionario]:
        """Obtiene todos los funcionarios."""
        queryset = DjangoFuncionario.objects.using('postgres_db')
        
        if not include_deleted:
            queryset = queryset.filter(eliminado=False)
            
        django_funcionarios = queryset.order_by('apellidos', 'nombres')
        return [self._to_domain_entity(f) for f in django_funcionarios]

    def get_active(self) -> List[Funcionario]:
        """Obtiene solo los funcionarios activos."""
        django_funcionarios = DjangoFuncionario.objects.using('postgres_db').filter(
            estado='activo',
            eliminado=False
        ).order_by('apellidos', 'nombres')
        
        return [self._to_domain_entity(f) for f in django_funcionarios]

    def search(self, search_term: str, include_deleted: bool = False) -> List[Funcionario]:
        """Busca funcionarios por nombres, apellidos o email."""
        queryset = DjangoFuncionario.objects.using('postgres_db')
        
        if not include_deleted:
            queryset = queryset.filter(eliminado=False)
        
        # Buscar en nombres, apellidos y email
        queryset = queryset.filter(
            django_models.Q(nombres__icontains=search_term) |
            django_models.Q(apellidos__icontains=search_term) |
            django_models.Q(email__icontains=search_term)
        ).order_by('apellidos', 'nombres')
        
        return [self._to_domain_entity(f) for f in queryset]

    def save(self, funcionario: Funcionario) -> Funcionario:
        """Guarda un funcionario (crear o actualizar)."""
        if funcionario.id:
            # Actualizar existente
            django_funcionario = DjangoFuncionario.objects.using('postgres_db').get(id=funcionario.id)
            self._update_django_model(django_funcionario, funcionario)
        else:
            # Crear nuevo
            django_funcionario = self._to_django_model(funcionario)
        
        django_funcionario.save(using='postgres_db')
        return self._to_domain_entity(django_funcionario)

    def delete(self, funcionario_id: int) -> bool:
        """Elimina (soft delete) un funcionario."""
        try:
            django_funcionario = DjangoFuncionario.objects.using('postgres_db').get(id=funcionario_id)
            django_funcionario.eliminado = True
            django_funcionario.estado = 'inactivo'
            django_funcionario.save(using='postgres_db')
            return True
        except DjangoFuncionario.DoesNotExist:
            return False

    def count_total(self) -> int:
        """Cuenta el total de funcionarios (excluyendo eliminados)."""
        return DjangoFuncionario.objects.using('postgres_db').filter(eliminado=False).count()

    def count_by_estado(self, estado: str) -> int:
        """Cuenta funcionarios por estado."""
        return DjangoFuncionario.objects.using('postgres_db').filter(
            estado=estado,
            eliminado=False
        ).count()

    def exists_by_email(self, email: Email, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un funcionario con el email dado."""
        queryset = DjangoFuncionario.objects.using('postgres_db').filter(
            email=email.value,
            eliminado=False
        )
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()

    def _to_domain_entity(self, django_funcionario: DjangoFuncionario) -> Funcionario:
        """Convierte un modelo Django a entidad de dominio."""
        return Funcionario(
            id=django_funcionario.id,
            nombres=django_funcionario.nombres,
            apellidos=django_funcionario.apellidos,
            email=Email(django_funcionario.email),
            estado=Estado.for_funcionario(django_funcionario.estado),
            eliminado=django_funcionario.eliminado,
            created_at=django_funcionario.created_at,
            updated_at=django_funcionario.updated_at
        )

    def _to_django_model(self, funcionario: Funcionario) -> DjangoFuncionario:
        """Convierte una entidad de dominio a modelo Django."""
        return DjangoFuncionario(
            nombres=funcionario.nombres,
            apellidos=funcionario.apellidos,
            email=funcionario.email.value,
            estado=funcionario.estado.value,
            eliminado=funcionario.eliminado
        )

    def _update_django_model(self, django_funcionario: DjangoFuncionario, funcionario: Funcionario):
        """Actualiza un modelo Django con datos de la entidad de dominio."""
        django_funcionario.nombres = funcionario.nombres
        django_funcionario.apellidos = funcionario.apellidos
        django_funcionario.email = funcionario.email.value
        django_funcionario.estado = funcionario.estado.value
        django_funcionario.eliminado = funcionario.eliminado
