"""
Views Web para Funcionarios siguiendo arquitectura hexagonal.

Maneja las peticiones HTTP y coordina con los use cases.
"""
from typing import Any, Dict

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from ...application.use_cases import (
    ListFuncionariosUseCase,
    GetFuncionarioStatsUseCase,
    GetFuncionarioByIdUseCase,
    CreateFuncionarioUseCase,
    UpdateFuncionarioUseCase,
    DeleteFuncionarioUseCase,
    FuncionarioSearchCriteria
)
from ...application.services import FuncionarioService
from ...infrastructure.repositories import DjangoFuncionarioRepository


class FuncionarioController(LoginRequiredMixin, View):
    """
    Controller principal para funcionarios.
    
    Maneja todas las operaciones HTTP relacionadas con funcionarios
    siguiendo el patrón de arquitectura hexagonal.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection - Se puede hacer con un container DI
        self._setup_dependencies()

    def _setup_dependencies(self):
        """Configura las dependencias del controller."""
        # Repository
        repository = DjangoFuncionarioRepository()
        
        # Service
        service = FuncionarioService(repository)
        
        # Use Cases
        self._list_use_case = ListFuncionariosUseCase(service)
        self._stats_use_case = GetFuncionarioStatsUseCase(service)
        self._get_by_id_use_case = GetFuncionarioByIdUseCase(service)
        self._create_use_case = CreateFuncionarioUseCase(service)
        self._update_use_case = UpdateFuncionarioUseCase(service)
        self._delete_use_case = DeleteFuncionarioUseCase(service)

    def get(self, request: HttpRequest) -> Any:
        """
        Maneja las peticiones GET para listar funcionarios.
        
        Args:
            request: Petición HTTP
            
        Returns:
            Respuesta HTTP con la lista de funcionarios
        """
        # Extraer criterios de búsqueda de la query string
        criteria = self._extract_search_criteria(request)
        
        # Ejecutar use case
        funcionarios = self._list_use_case.execute(criteria)
        stats = self._stats_use_case.execute()
        
        # Paginación
        paginator = Paginator(funcionarios, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Preparar contexto para el template
        context = self._prepare_list_context(page_obj, stats, criteria, request)
        
        return render(request, 'apps/funcionarios/apps-funcionarios-list.html', context)

    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Maneja las peticiones POST para crear funcionarios.
        
        Args:
            request: Petición HTTP
            
        Returns:
            Respuesta JSON con el resultado
        """
        try:
            data = self._extract_funcionario_data(request)
            funcionario = self._create_use_case.execute(
                nombres=data['nombres'],
                apellidos=data['apellidos'],
                email=data['email']
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Funcionario creado exitosamente',
                'funcionario': {
                    'id': funcionario.id,
                    'nombre_completo': funcionario.nombre_completo,
                    'email': funcionario.email.value
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)

    def put(self, request: HttpRequest, funcionario_id: int) -> JsonResponse:
        """
        Maneja las peticiones PUT para actualizar funcionarios.
        
        Args:
            request: Petición HTTP
            funcionario_id: ID del funcionario a actualizar
            
        Returns:
            Respuesta JSON con el resultado
        """
        try:
            data = self._extract_funcionario_data(request)
            funcionario = self._update_use_case.execute(
                funcionario_id=funcionario_id,
                nombres=data['nombres'],
                apellidos=data['apellidos'],
                email=data['email']
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Funcionario actualizado exitosamente',
                'funcionario': {
                    'id': funcionario.id,
                    'nombre_completo': funcionario.nombre_completo,
                    'email': funcionario.email.value
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)

    def delete(self, request: HttpRequest, funcionario_id: int) -> JsonResponse:
        """
        Maneja las peticiones DELETE para eliminar funcionarios.
        
        Args:
            request: Petición HTTP
            funcionario_id: ID del funcionario a eliminar
            
        Returns:
            Respuesta JSON con el resultado
        """
        try:
            success = self._delete_use_case.execute(funcionario_id)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Funcionario eliminado exitosamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudo eliminar el funcionario'
                }, status=400)
                
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)

    def _extract_search_criteria(self, request: HttpRequest) -> FuncionarioSearchCriteria:
        """Extrae los criterios de búsqueda del request."""
        return FuncionarioSearchCriteria(
            search_term=request.GET.get('search', '').strip() or None,
            estado=request.GET.get('estado', '').strip() or None,
            include_deleted=False  # Por ahora no incluir eliminados
        )

    def _extract_funcionario_data(self, request: HttpRequest) -> Dict[str, str]:
        """Extrae los datos del funcionario del request."""
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
            
        return {
            'nombres': data.get('nombres', '').strip(),
            'apellidos': data.get('apellidos', '').strip(),
            'email': data.get('email', '').strip()
        }

    def _prepare_list_context(self, page_obj, stats, criteria, request) -> Dict[str, Any]:
        """Prepara el contexto para el template de lista."""
        return {
            'funcionarios': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            
            # Estadísticas
            'total_funcionarios': stats.total,
            'funcionarios_activos': stats.activos,
            'funcionarios_inactivos': stats.inactivos,
            
            # Filtros actuales
            'current_search': criteria.search_term or '',
            'current_estado': criteria.estado or '',
            
            # Para mantener filtros en paginación
            'query_params': self._build_query_params(criteria)
        }

    def _build_query_params(self, criteria: FuncionarioSearchCriteria) -> str:
        """Construye parámetros de query para mantener filtros."""
        params = []
        if criteria.search_term:
            params.append(f"search={criteria.search_term}")
        if criteria.estado:
            params.append(f"estado={criteria.estado}")
        return '&' + '&'.join(params) if params else ''


# View function para mantener compatibilidad con URLs
funcionarios_list_view = FuncionarioController.as_view()
