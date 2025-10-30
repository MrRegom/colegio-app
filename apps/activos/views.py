"""
Class-Based Views para el módulo de activos/inventario.

Este archivo implementa todas las vistas usando CBVs siguiendo SOLID y DRY:
- Reutilización de mixins de core.mixins
- Separación de responsabilidades (vistas delgadas, lógica en services)
- Repository Pattern para acceso a datos
- Service Layer para lógica de negocio
- Código limpio y mantenible
- Type hints completos
- Auditoría automática
"""
from typing import Any, Optional
from django.db.models import QuerySet, Q
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.core.exceptions import ValidationError
from core.mixins import (
    BaseAuditedViewMixin, AtomicTransactionMixin, SoftDeleteMixin,
    PaginatedListMixin, FilteredListMixin
)
from .models import (
    Activo, CategoriaActivo, UnidadMedida, EstadoActivo,
    Ubicacion, TipoMovimientoActivo, MovimientoActivo, UbicacionActual
)
from .forms import (
    ActivoForm, CategoriaActivoForm, UnidadMedidaForm, EstadoActivoForm,
    UbicacionForm, TipoMovimientoActivoForm, MovimientoActivoForm,
    FiltroActivosForm
)
from .repositories import (
    ActivoRepository, CategoriaActivoRepository, UnidadMedidaRepository,
    EstadoActivoRepository, UbicacionRepository, TipoMovimientoActivoRepository,
    MovimientoActivoRepository, UbicacionActualRepository
)
from .services import (
    ActivoService, MovimientoActivoService, CategoriaActivoService
)


# ==================== VISTA MENÚ PRINCIPAL ====================

class MenuInventarioView(BaseAuditedViewMixin, TemplateView):
    """
    Vista del menú principal del módulo de inventario (activos).

    Muestra estadísticas y accesos rápidos basados en permisos del usuario.
    Usa repositories para obtener estadísticas de manera eficiente.
    Permisos: activos.view_activo
    """
    template_name = 'activos/menu_inventario.html'
    permission_required = 'activos.view_activo'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega estadísticas al contexto usando repositories."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Usar repositories para obtener estadísticas
        activo_repo = ActivoRepository()
        categoria_repo = CategoriaActivoRepository()
        ubicacion_repo = UbicacionRepository()
        movimiento_repo = MovimientoActivoRepository()

        # Estadísticas del módulo
        context['stats'] = {
            'total_activos': activo_repo.get_all().count(),
            'total_categorias': categoria_repo.get_all().count(),
            'total_movimientos': movimiento_repo.get_all().count(),
            'total_ubicaciones': ubicacion_repo.get_all().count(),
            'activos_en_uso': activo_repo.get_all().filter(
                estado__codigo='EN_USO'
            ).count() if EstadoActivoRepository.get_all().filter(codigo='EN_USO').exists() else 0,
        }

        # Permisos del usuario
        context['permisos'] = {
            'puede_crear': user.has_perm('activos.add_activo'),
            'puede_movimientos': user.has_perm('activos.add_movimientoactivo'),
            'puede_categorias': user.has_perm('activos.add_categoriaactivo'),
            'puede_gestionar': user.has_perm('activos.change_activo'),
        }

        context['titulo'] = 'Módulo de Inventario'
        return context


# ==================== VISTAS DE ACTIVOS ====================

class ActivoListView(BaseAuditedViewMixin, PaginatedListMixin, FilteredListMixin, ListView):
    """
    Vista para listar activos con filtros y paginación.

    Permisos: activos.view_activo
    Filtros: Categoría, estado, búsqueda por texto
    Usa ActivoRepository para acceso optimizado a datos
    """
    model = Activo
    template_name = 'activos/lista_activos.html'
    context_object_name = 'activos'
    permission_required = 'activos.view_activo'
    paginate_by = 25
    filter_form_class = FiltroActivosForm

    def get_queryset(self) -> QuerySet[Activo]:
        """Retorna activos usando repository con optimización N+1."""
        repo = ActivoRepository()
        queryset = repo.get_all()

        # Aplicar filtros del formulario
        form = self.filter_form_class(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data

            # Filtro por categoría
            if data.get('categoria'):
                queryset = queryset.filter(categoria=data['categoria'])

            # Filtro por estado
            if data.get('estado'):
                queryset = queryset.filter(estado=data['estado'])

            # Filtro de búsqueda por texto
            if data.get('buscar'):
                q = data['buscar']
                queryset = queryset.filter(
                    Q(codigo__icontains=q) |
                    Q(nombre__icontains=q) |
                    Q(marca__icontains=q) |
                    Q(modelo__icontains=q)
                )

        return queryset.order_by('codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de Activos'
        context['form'] = self.filter_form_class(self.request.GET)
        return context


class ActivoDetailView(BaseAuditedViewMixin, DetailView):
    """
    Vista para ver el detalle de un activo con su historial.

    Permisos: activos.view_activo
    """
    model = Activo
    template_name = 'activos/detalle_activo.html'
    context_object_name = 'activo'
    permission_required = 'activos.view_activo'

    def get_queryset(self) -> QuerySet:
        """Optimiza consultas con select_related."""
        return super().get_queryset().select_related(
            'categoria', 'unidad_medida', 'estado'
        )

    def get_context_data(self, **kwargs) -> dict:
        """Agrega ubicación actual y movimientos recientes al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Activo {self.object.codigo}'

        # Obtener ubicación actual del activo
        try:
            context['ubicacion_actual'] = UbicacionActual.objects.select_related(
                'ubicacion', 'responsable', 'ultimo_movimiento'
            ).get(activo=self.object)
        except UbicacionActual.DoesNotExist:
            context['ubicacion_actual'] = None

        # Últimos 10 movimientos del activo
        context['movimientos'] = MovimientoActivo.objects.filter(
            activo=self.object
        ).select_related(
            'tipo_movimiento', 'ubicacion_destino', 'responsable', 'usuario_registro'
        ).order_by('-fecha_movimiento')[:10]

        return context


class ActivoCreateView(BaseAuditedViewMixin, AtomicTransactionMixin, CreateView):
    """
    Vista para crear un nuevo activo.

    Permisos: activos.add_activo
    Auditoría: Registra acción CREAR automáticamente
    Transacción atómica: Garantiza integridad de datos
    """
    model = Activo
    form_class = ActivoForm
    template_name = 'activos/form_activo.html'
    permission_required = 'activos.add_activo'

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó activo {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Activo {obj.codigo} creado exitosamente.'

    def get_success_url(self) -> str:
        """Redirige al detalle del activo creado."""
        return reverse_lazy('activos:detalle_activo', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Activo'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class ActivoUpdateView(BaseAuditedViewMixin, AtomicTransactionMixin, UpdateView):
    """
    Vista para editar un activo existente.

    Permisos: activos.change_activo
    Auditoría: Registra acción EDITAR automáticamente
    Transacción atómica: Garantiza integridad de datos
    """
    model = Activo
    form_class = ActivoForm
    template_name = 'activos/form_activo.html'
    permission_required = 'activos.change_activo'

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó activo {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Activo {obj.codigo} actualizado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar activos no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_success_url(self) -> str:
        """Redirige al detalle del activo editado."""
        return reverse_lazy('activos:detalle_activo', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Activo {self.object.codigo}'
        context['action'] = 'Editar'
        context['activo'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class ActivoDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) un activo.

    Permisos: activos.delete_activo
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete (marca como eliminado, no borra físicamente)
    """
    model = Activo
    template_name = 'activos/eliminar_activo.html'
    permission_required = 'activos.delete_activo'
    success_url = reverse_lazy('activos:lista_activos')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó activo {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Activo {obj.codigo} eliminado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar activos no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Activo {self.object.codigo}'
        context['activo'] = self.object
        # Verificar si tiene movimientos
        context['tiene_movimientos'] = MovimientoActivo.objects.filter(activo=self.object).exists()
        return context


# ==================== VISTAS DE MOVIMIENTOS ====================

class MovimientoListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para ver el historial de movimientos de inventario con todos los detalles.

    Permisos: activos.view_movimientoactivo

    Campos mostrados:
    - Código, Categoría, Marca, Modelo, Nº Serie
    - Estado, Responsable, Ubicación
    - Fecha de Ingreso, Nº Factura/Guía, Proveniencia
    - Fecha de Baja, Observaciones, Motivo de Baja
    """
    model = MovimientoActivo
    template_name = 'activos/lista_movimientos.html'
    context_object_name = 'movimientos'
    permission_required = 'activos.view_movimientoactivo'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna movimientos con relaciones optimizadas incluyendo proveniencia."""
        queryset = super().get_queryset().select_related(
            'activo', 'activo__categoria', 'activo__estado', 'activo__unidad_medida',
            'tipo_movimiento', 'ubicacion_destino', 'responsable', 'usuario_registro',
            'proveniencia'
        )

        # Filtros opcionales
        activo_id = self.request.GET.get('activo')
        if activo_id:
            queryset = queryset.filter(activo_id=activo_id)

        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(activo__categoria_id=categoria_id)

        estado_id = self.request.GET.get('estado')
        if estado_id:
            queryset = queryset.filter(activo__estado_id=estado_id)

        # Filtro de búsqueda
        buscar = self.request.GET.get('buscar')
        if buscar:
            queryset = queryset.filter(
                Q(activo__codigo__icontains=buscar) |
                Q(activo__nombre__icontains=buscar) |
                Q(activo__marca__icontains=buscar) |
                Q(activo__modelo__icontains=buscar) |
                Q(numero_serie__icontains=buscar) |
                Q(numero_factura_guia__icontains=buscar)
            )

        return queryset.order_by('-fecha_movimiento')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Movimientos de Inventario'
        # Agregar catálogos para filtros
        context['categorias'] = CategoriaActivo.objects.filter(activo=True)
        context['estados'] = EstadoActivo.objects.filter(activo=True)
        return context


class MovimientoDetailView(BaseAuditedViewMixin, DetailView):
    """
    Vista para ver el detalle de un movimiento.

    Permisos: activos.ver_historial_movimientos
    """
    model = MovimientoActivo
    template_name = 'activos/detalle_movimiento.html'
    context_object_name = 'movimiento'
    permission_required = 'activos.ver_historial_movimientos'

    def get_queryset(self) -> QuerySet:
        """Optimiza consultas con select_related."""
        return super().get_queryset().select_related(
            'activo', 'tipo_movimiento', 'ubicacion_destino',
            'responsable', 'usuario_registro'
        )

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detalle de Movimiento'
        return context


class MovimientoCreateView(BaseAuditedViewMixin, AtomicTransactionMixin, CreateView):
    """
    Vista para registrar un nuevo movimiento de activo.

    Permisos: activos.registrar_movimiento
    Auditoría: Registra acción CREAR automáticamente
    Transacción atómica: Garantiza que el movimiento y la actualización
    de ubicación se realicen de forma atómica
    """
    model = MovimientoActivo
    form_class = MovimientoActivoForm
    template_name = 'activos/form_movimiento.html'
    permission_required = 'activos.registrar_movimiento'
    success_url = reverse_lazy('activos:lista_movimientos')

    # Configuración de auditoría
    audit_action = 'CREAR'
    success_message = 'Movimiento de activo registrado exitosamente.'

    def form_valid(self, form):
        """
        Procesa el formulario válido con transacción atómica.

        Actualiza la ubicación actual del activo automáticamente.
        """
        movimiento = form.save(commit=False)
        movimiento.usuario_registro = self.request.user
        movimiento.save()

        # Actualizar ubicación actual del activo
        ubicacion_actual, created = UbicacionActual.objects.get_or_create(
            activo=movimiento.activo
        )
        ubicacion_actual.ubicacion = movimiento.ubicacion_destino
        ubicacion_actual.responsable = movimiento.responsable
        ubicacion_actual.ultimo_movimiento = movimiento
        ubicacion_actual.save()

        self.object = movimiento

        # Generar descripción para auditoría
        descripcion = f'Registró movimiento de activo: {movimiento.activo.codigo}'
        if movimiento.ubicacion_destino:
            descripcion += f' a {movimiento.ubicacion_destino.nombre}'
        if movimiento.responsable:
            descripcion += f' - Responsable: {movimiento.responsable.get_full_name()}'

        self.audit_description_template = descripcion

        # Continuar con el flujo normal (mensaje y redirección)
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar Movimiento de Activo'
        context['action'] = 'Registrar'
        return context


class UbicacionActualListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para ver la ubicación actual de todos los activos.

    Permisos: activos.view_activo
    """
    model = UbicacionActual
    template_name = 'activos/ubicacion_actual.html'
    context_object_name = 'ubicaciones'
    permission_required = 'activos.view_activo'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna ubicaciones con relaciones optimizadas."""
        return super().get_queryset().select_related(
            'activo', 'activo__categoria', 'activo__estado',
            'ubicacion', 'responsable'
        ).order_by('activo__codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Ubicación Actual de Activos'
        return context


# ==================== VISTAS DE CATEGORÍAS ====================

class CategoriaListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar categorías de activos.

    Permisos: activos.view_categoriaactivo
    """
    model = CategoriaActivo
    template_name = 'activos/lista_categorias.html'
    context_object_name = 'categorias'
    permission_required = 'activos.view_categoriaactivo'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo categorías no eliminadas."""
        return super().get_queryset().filter(eliminado=False).order_by('codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Categorías de Activos'
        return context


class CategoriaCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear una nueva categoría de activo.

    Permisos: activos.add_categoriaactivo
    Auditoría: Registra acción CREAR automáticamente
    """
    model = CategoriaActivo
    form_class = CategoriaActivoForm
    template_name = 'activos/form_categoria.html'
    permission_required = 'activos.add_categoriaactivo'
    success_url = reverse_lazy('activos:lista_categorias')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó categoría {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Categoría {obj.nombre} creada exitosamente.'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Categoría'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class CategoriaUpdateView(BaseAuditedViewMixin, UpdateView):
    """
    Vista para editar una categoría de activo existente.

    Permisos: activos.change_categoriaactivo
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = CategoriaActivo
    form_class = CategoriaActivoForm
    template_name = 'activos/form_categoria.html'
    permission_required = 'activos.change_categoriaactivo'
    success_url = reverse_lazy('activos:lista_categorias')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó categoría {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Categoría {obj.nombre} actualizada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar categorías no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Categoría {self.object.codigo}'
        context['action'] = 'Editar'
        context['categoria'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class CategoriaDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) una categoría de activo.

    Permisos: activos.delete_categoriaactivo
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete
    """
    model = CategoriaActivo
    template_name = 'activos/eliminar_categoria.html'
    permission_required = 'activos.delete_categoriaactivo'
    success_url = reverse_lazy('activos:lista_categorias')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó categoría {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Categoría {obj.codigo} eliminada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar categorías no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Categoría {self.object.codigo}'
        context['categoria'] = self.object
        return context


# ==================== VISTAS DE UNIDADES DE MEDIDA ====================

class UnidadMedidaListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar unidades de medida.

    Permisos: activos.view_unidadmedida
    """
    model = UnidadMedida
    template_name = 'activos/lista_unidades.html'
    context_object_name = 'unidades'
    permission_required = 'activos.view_unidadmedida'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo unidades no eliminadas."""
        return super().get_queryset().filter(eliminado=False).order_by('codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Unidades de Medida'
        return context


class UnidadMedidaCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear una nueva unidad de medida.

    Permisos: activos.add_unidadmedida
    Auditoría: Registra acción CREAR automáticamente
    """
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'activos/form_unidad.html'
    permission_required = 'activos.add_unidadmedida'
    success_url = reverse_lazy('activos:lista_unidades')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó unidad de medida {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Unidad {obj.nombre} creada exitosamente.'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Unidad de Medida'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class UnidadMedidaUpdateView(BaseAuditedViewMixin, UpdateView):
    """
    Vista para editar una unidad de medida existente.

    Permisos: activos.change_unidadmedida
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'activos/form_unidad.html'
    permission_required = 'activos.change_unidadmedida'
    success_url = reverse_lazy('activos:lista_unidades')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó unidad de medida {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Unidad {obj.nombre} actualizada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar unidades no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Unidad {self.object.codigo}'
        context['action'] = 'Editar'
        context['unidad'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class UnidadMedidaDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) una unidad de medida.

    Permisos: activos.delete_unidadmedida
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete
    """
    model = UnidadMedida
    template_name = 'activos/eliminar_unidad.html'
    permission_required = 'activos.delete_unidadmedida'
    success_url = reverse_lazy('activos:lista_unidades')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó unidad de medida {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Unidad {obj.codigo} eliminada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar unidades no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Unidad {self.object.codigo}'
        context['unidad'] = self.object
        return context


# ==================== VISTAS DE ESTADOS ====================

class EstadoActivoListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar estados de activos.

    Permisos: activos.view_estadoactivo
    """
    model = EstadoActivo
    template_name = 'activos/lista_estados.html'
    context_object_name = 'estados'
    permission_required = 'activos.view_estadoactivo'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo estados no eliminados."""
        return super().get_queryset().filter(eliminado=False).order_by('codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Estados de Activos'
        return context


class EstadoActivoCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear un nuevo estado de activo.

    Permisos: activos.add_estadoactivo
    Auditoría: Registra acción CREAR automáticamente
    """
    model = EstadoActivo
    form_class = EstadoActivoForm
    template_name = 'activos/form_estado.html'
    permission_required = 'activos.add_estadoactivo'
    success_url = reverse_lazy('activos:lista_estados')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó estado de activo {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Estado {obj.nombre} creado exitosamente.'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Estado de Activo'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class EstadoActivoUpdateView(BaseAuditedViewMixin, UpdateView):
    """
    Vista para editar un estado de activo existente.

    Permisos: activos.change_estadoactivo
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = EstadoActivo
    form_class = EstadoActivoForm
    template_name = 'activos/form_estado.html'
    permission_required = 'activos.change_estadoactivo'
    success_url = reverse_lazy('activos:lista_estados')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó estado de activo {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Estado {obj.nombre} actualizado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar estados no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Estado {self.object.codigo}'
        context['action'] = 'Editar'
        context['estado'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class EstadoActivoDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) un estado de activo.

    Permisos: activos.delete_estadoactivo
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete
    """
    model = EstadoActivo
    template_name = 'activos/eliminar_estado.html'
    permission_required = 'activos.delete_estadoactivo'
    success_url = reverse_lazy('activos:lista_estados')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó estado de activo {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Estado {obj.codigo} eliminado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar estados no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Estado {self.object.codigo}'
        context['estado'] = self.object
        return context


# ==================== VISTAS DE UBICACIONES ====================

class UbicacionListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar ubicaciones físicas.

    Permisos: activos.view_ubicacion
    """
    model = Ubicacion
    template_name = 'activos/lista_ubicaciones.html'
    context_object_name = 'ubicaciones'
    permission_required = 'activos.view_ubicacion'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo ubicaciones no eliminadas."""
        return super().get_queryset().filter(eliminado=False).order_by('codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Ubicaciones Físicas'
        return context


class UbicacionCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear una nueva ubicación física.

    Permisos: activos.add_ubicacion
    Auditoría: Registra acción CREAR automáticamente
    """
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'activos/form_ubicacion.html'
    permission_required = 'activos.add_ubicacion'
    success_url = reverse_lazy('activos:lista_ubicaciones')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó ubicación {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Ubicación {obj.nombre} creada exitosamente.'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Ubicación'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class UbicacionUpdateView(BaseAuditedViewMixin, UpdateView):
    """
    Vista para editar una ubicación física existente.

    Permisos: activos.change_ubicacion
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'activos/form_ubicacion.html'
    permission_required = 'activos.change_ubicacion'
    success_url = reverse_lazy('activos:lista_ubicaciones')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó ubicación {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Ubicación {obj.nombre} actualizada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar ubicaciones no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Ubicación {self.object.codigo}'
        context['action'] = 'Editar'
        context['ubicacion'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class UbicacionDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) una ubicación física.

    Permisos: activos.delete_ubicacion
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete
    """
    model = Ubicacion
    template_name = 'activos/eliminar_ubicacion.html'
    permission_required = 'activos.delete_ubicacion'
    success_url = reverse_lazy('activos:lista_ubicaciones')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó ubicación {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Ubicación {obj.codigo} eliminada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar ubicaciones no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Ubicación {self.object.codigo}'
        context['ubicacion'] = self.object
        return context


# ==================== VISTAS DE TIPOS DE MOVIMIENTO ====================

class TipoMovimientoListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar tipos de movimiento de activos.

    Permisos: activos.view_tipomovimientoactivo
    """
    model = TipoMovimientoActivo
    template_name = 'activos/lista_tipos_movimiento.html'
    context_object_name = 'tipos_movimiento'
    permission_required = 'activos.view_tipomovimientoactivo'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo tipos de movimiento no eliminados."""
        return super().get_queryset().filter(eliminado=False).order_by('codigo')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Tipos de Movimiento de Activos'
        return context


class TipoMovimientoCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear un nuevo tipo de movimiento de activo.

    Permisos: activos.add_tipomovimientoactivo
    Auditoría: Registra acción CREAR automáticamente
    """
    model = TipoMovimientoActivo
    form_class = TipoMovimientoActivoForm
    template_name = 'activos/form_tipo_movimiento.html'
    permission_required = 'activos.add_tipomovimientoactivo'
    success_url = reverse_lazy('activos:lista_tipos_movimiento')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó tipo de movimiento {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Tipo de movimiento {obj.nombre} creado exitosamente.'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Tipo de Movimiento'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class TipoMovimientoUpdateView(BaseAuditedViewMixin, UpdateView):
    """
    Vista para editar un tipo de movimiento de activo existente.

    Permisos: activos.change_tipomovimientoactivo
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = TipoMovimientoActivo
    form_class = TipoMovimientoActivoForm
    template_name = 'activos/form_tipo_movimiento.html'
    permission_required = 'activos.change_tipomovimientoactivo'
    success_url = reverse_lazy('activos:lista_tipos_movimiento')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó tipo de movimiento {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Tipo de movimiento {obj.nombre} actualizado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar tipos de movimiento no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Tipo de Movimiento {self.object.codigo}'
        context['action'] = 'Editar'
        context['tipo_movimiento'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class TipoMovimientoDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) un tipo de movimiento de activo.

    Permisos: activos.delete_tipomovimientoactivo
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete
    """
    model = TipoMovimientoActivo
    template_name = 'activos/eliminar_tipo_movimiento.html'
    permission_required = 'activos.delete_tipomovimientoactivo'
    success_url = reverse_lazy('activos:lista_tipos_movimiento')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó tipo de movimiento {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Tipo de movimiento {obj.codigo} eliminado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar tipos de movimiento no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Tipo de Movimiento {self.object.codigo}'
        context['tipo_movimiento'] = self.object
        return context
