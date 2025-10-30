"""
Class-Based Views para el módulo de bodega.

Implementa las mejores prácticas con CBVs siguiendo SOLID y DRY:
- Reutilización de mixins
- Separación de responsabilidades (vistas delgadas, lógica en services)
- Repository Pattern para acceso a datos
- Service Layer para lógica de negocio
- Código más limpio y mantenible
- Type hints completos
- Paginación automática
- Auditoría automática
"""
from typing import Any, Optional
from django.db.models import QuerySet, Q, Sum, Count
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from core.mixins import (
    BaseAuditedViewMixin, AtomicTransactionMixin, SoftDeleteMixin,
    PaginatedListMixin, FilteredListMixin
)
from .models import Bodega, Categoria, Articulo, TipoMovimiento, Movimiento
from .forms import CategoriaForm, ArticuloForm, MovimientoForm, ArticuloFiltroForm
from .repositories import (
    BodegaRepository, CategoriaRepository, ArticuloRepository,
    TipoMovimientoRepository, MovimientoRepository
)
from .services import CategoriaService, ArticuloService, MovimientoService


# ==================== MENÚ PRINCIPAL ====================

class MenuBodegaView(LoginRequiredMixin, TemplateView):
    """
    Vista del menú principal de bodega con estadísticas.

    Muestra cards con resumen de bodega según las mejores prácticas de Django 5.2.
    Usa repositories para obtener estadísticas de manera eficiente.
    """
    template_name = 'bodega/menu_bodega.html'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega estadísticas al contexto usando repositories."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Usar repositories para obtener estadísticas
        articulo_repo = ArticuloRepository()
        categoria_repo = CategoriaRepository()
        bodega_repo = BodegaRepository()
        movimiento_repo = MovimientoRepository()

        # Estadísticas para el módulo de bodega
        context['stats'] = {
            'total_articulos': articulo_repo.get_all().count(),
            'total_categorias': categoria_repo.get_all().count(),
            'total_movimientos': movimiento_repo.get_all().count(),
            'bodegas_activas': bodega_repo.get_active().count(),
            'stock_total': articulo_repo.get_all().aggregate(
                total=Sum('stock_actual')
            )['total'] or 0,
        }

        # Permisos del usuario
        context['permisos'] = {
            'puede_crear_articulo': user.has_perm('bodega.add_articulo'),
            'puede_crear_categoria': user.has_perm('bodega.add_categoria'),
            'puede_crear_movimiento': user.has_perm('bodega.add_movimiento'),
            'puede_gestionar': user.has_perm('bodega.change_articulo'),
        }

        context['titulo'] = 'Módulo de Bodega'
        return context


# ==================== VISTAS DE CATEGORÍA ====================

class CategoriaListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar categorías con paginación y filtros.

    Permisos: bodega.view_categoria
    Usa CategoriaRepository para acceso a datos
    """
    model = Categoria
    template_name = 'bodega/categoria/lista.html'
    context_object_name = 'categorias'
    permission_required = 'bodega.view_categoria'
    paginate_by = 25

    def get_queryset(self) -> QuerySet[Categoria]:
        """Retorna categorías usando repository."""
        repo = CategoriaRepository()

        # Filtro de búsqueda
        q: str = self.request.GET.get('q', '').strip()
        if q:
            return repo.search(q)

        return repo.get_all()

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Categorías'
        context['query'] = self.request.GET.get('q', '')
        return context


class CategoriaCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear una nueva categoría.

    Permisos: bodega.add_categoria
    Auditoría: Registra acción CREAR automáticamente
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = 'bodega/categoria/form.html'
    permission_required = 'bodega.add_categoria'
    success_url = reverse_lazy('bodega:categoria_lista')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Categoría creada: {obj.codigo} - {obj.nombre}'

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
    Vista para editar una categoría existente.

    Permisos: bodega.change_categoria
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = 'bodega/categoria/form.html'
    permission_required = 'bodega.change_categoria'
    success_url = reverse_lazy('bodega:categoria_lista')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Categoría actualizada: {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Categoría {obj.nombre} actualizada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar categorías no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Categoría: {self.object.nombre}'
        context['action'] = 'Actualizar'
        context['categoria'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class CategoriaDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) una categoría.

    Permisos: bodega.delete_categoria
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete (marca como eliminado, no borra físicamente)
    """
    model = Categoria
    template_name = 'bodega/categoria/eliminar.html'
    permission_required = 'bodega.delete_categoria'
    success_url = reverse_lazy('bodega:categoria_lista')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Categoría eliminada: {obj.codigo} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Categoría {obj.nombre} eliminada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar categorías no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Categoría: {self.object.nombre}'
        context['categoria'] = self.object
        # Verificar si tiene artículos
        context['tiene_articulos'] = self.object.articulos.filter(eliminado=False).exists()
        return context


# ==================== VISTAS DE ARTÍCULO ====================

class ArticuloListView(BaseAuditedViewMixin, PaginatedListMixin, FilteredListMixin, ListView):
    """
    Vista para listar artículos con paginación y filtros.

    Permisos: bodega.view_articulo
    Filtros: Categoría, bodega, búsqueda por texto, estado activo
    """
    model = Articulo
    template_name = 'bodega/articulo/lista.html'
    context_object_name = 'articulos'
    permission_required = 'bodega.view_articulo'
    paginate_by = 25
    filter_form_class = ArticuloFiltroForm

    def get_queryset(self) -> QuerySet:
        """
        Retorna artículos no eliminados con relaciones optimizadas.

        Optimización N+1: Usa select_related para evitar queries adicionales.
        """
        queryset = super().get_queryset().filter(
            eliminado=False
        ).select_related(
            'categoria', 'ubicacion_fisica'
        )

        # Aplicar filtros del formulario
        form = self.filter_form_class(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data

            # Filtro de búsqueda por texto
            if data.get('q'):
                q = data['q']
                queryset = queryset.filter(
                    Q(sku__icontains=q) |
                    Q(codigo__icontains=q) |
                    Q(nombre__icontains=q) |
                    Q(marca__icontains=q)
                )

            # Filtro por categoría
            if data.get('categoria'):
                queryset = queryset.filter(categoria=data['categoria'])

            # Filtro por bodega
            if data.get('bodega'):
                queryset = queryset.filter(ubicacion_fisica=data['bodega'])

            # Filtro por estado activo
            if data.get('activo') != '':
                queryset = queryset.filter(activo=(data['activo'] == '1'))

        return queryset.order_by('sku')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Artículos'
        return context


class ArticuloCreateView(BaseAuditedViewMixin, CreateView):
    """
    Vista para crear un nuevo artículo.

    Permisos: bodega.add_articulo
    Auditoría: Registra acción CREAR automáticamente
    """
    model = Articulo
    form_class = ArticuloForm
    template_name = 'bodega/articulo/form.html'
    permission_required = 'bodega.add_articulo'
    success_url = reverse_lazy('bodega:articulo_lista')

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Artículo creado: {obj.sku} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Artículo {obj.sku} creado exitosamente.'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Artículo'
        context['action'] = 'Crear'
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class ArticuloUpdateView(BaseAuditedViewMixin, UpdateView):
    """
    Vista para editar un artículo existente.

    Permisos: bodega.change_articulo
    Auditoría: Registra acción EDITAR automáticamente
    """
    model = Articulo
    form_class = ArticuloForm
    template_name = 'bodega/articulo/form.html'
    permission_required = 'bodega.change_articulo'
    success_url = reverse_lazy('bodega:articulo_lista')

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Artículo actualizado: {obj.sku} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Artículo {obj.sku} actualizado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite editar artículos no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Artículo: {self.object.sku}'
        context['action'] = 'Actualizar'
        context['articulo'] = self.object
        return context

    def form_valid(self, form):
        """Procesa el formulario válido con log de auditoría."""
        response = super().form_valid(form)
        self.log_action(self.object, self.request)
        return response


class ArticuloDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) un artículo.

    Permisos: bodega.delete_articulo
    Auditoría: Registra acción ELIMINAR automáticamente
    """
    model = Articulo
    template_name = 'bodega/articulo/eliminar.html'
    permission_required = 'bodega.delete_articulo'
    success_url = reverse_lazy('bodega:articulo_lista')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Artículo eliminado: {obj.sku} - {obj.nombre}'

    # Mensaje de éxito
    success_message = 'Artículo {obj.sku} eliminado exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Solo permite eliminar artículos no eliminados."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Artículo: {self.object.sku}'
        context['articulo'] = self.object
        return context


class ArticuloDetailView(BaseAuditedViewMixin, DetailView):
    """
    Vista para ver el detalle de un artículo con su historial de movimientos.

    Permisos: bodega.view_articulo
    Usa repositories para acceso optimizado a datos
    """
    model = Articulo
    template_name = 'bodega/articulo/detalle.html'
    context_object_name = 'articulo'
    permission_required = 'bodega.view_articulo'

    def get_queryset(self) -> QuerySet[Articulo]:
        """Usa repository para consultas optimizadas."""
        return ArticuloRepository().get_all()

    def get_context_data(self, **kwargs) -> dict:
        """Agrega movimientos recientes usando MovimientoService."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Detalle Artículo {self.object.sku}'

        # Usar service para obtener historial
        service = MovimientoService()
        context['movimientos'] = service.obtener_historial_articulo(
            self.object, limit=20
        )

        return context


# ==================== VISTAS DE MOVIMIENTO ====================

class MovimientoListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para listar movimientos de inventario.

    Permisos: bodega.view_movimiento
    """
    model = Movimiento
    template_name = 'bodega/movimiento/lista.html'
    context_object_name = 'movimientos'
    permission_required = 'bodega.view_movimiento'
    paginate_by = 50

    def get_queryset(self) -> QuerySet:
        """Retorna movimientos con relaciones optimizadas."""
        queryset = super().get_queryset().filter(
            eliminado=False
        ).select_related(
            'articulo', 'tipo', 'usuario'
        )

        # Filtros opcionales
        operacion = self.request.GET.get('operacion', '')
        tipo_id = self.request.GET.get('tipo', '')
        articulo_id = self.request.GET.get('articulo', '')

        if operacion:
            queryset = queryset.filter(operacion=operacion)

        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)

        if articulo_id:
            queryset = queryset.filter(articulo_id=articulo_id)

        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Movimientos de Inventario'
        context['tipos'] = TipoMovimiento.objects.filter(activo=True, eliminado=False)
        context['operacion'] = self.request.GET.get('operacion', '')
        context['tipo_id'] = self.request.GET.get('tipo', '')
        return context


class MovimientoCreateView(BaseAuditedViewMixin, AtomicTransactionMixin, CreateView):
    """
    Vista para crear un nuevo movimiento de inventario.

    Permisos: bodega.add_movimiento
    Auditoría: Registra acción CREAR automáticamente
    Transacción atómica: Garantiza que la creación del movimiento
    y actualización del stock se realicen de forma atómica
    Delega lógica de negocio a MovimientoService
    """
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'bodega/movimiento/form.html'
    permission_required = 'bodega.add_movimiento'
    success_url = reverse_lazy('bodega:movimiento_lista')

    # Configuración de auditoría
    audit_action = 'CREAR'
    success_message = 'Movimiento registrado exitosamente. Stock actualizado: {obj.stock_despues} {obj.articulo.unidad_medida}'

    def form_valid(self, form):
        """
        Procesa el formulario válido usando MovimientoService.

        El servicio maneja toda la lógica de negocio:
        - Validaciones de stock
        - Actualización atómica
        - Cálculo de stocks
        """
        try:
            # Delegar a MovimientoService
            service = MovimientoService()
            movimiento = service.registrar_movimiento(
                articulo=form.cleaned_data['articulo'],
                tipo=form.cleaned_data['tipo'],
                cantidad=form.cleaned_data['cantidad'],
                operacion=form.cleaned_data['operacion'],
                usuario=self.request.user,
                motivo=form.cleaned_data['motivo']
            )

            self.object = movimiento

            # Continuar con el flujo normal (mensaje y redirección)
            response = super().form_valid(form)
            self.log_action(self.object, self.request)
            return response

        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar Movimiento'
        return context


class MovimientoDetailView(BaseAuditedViewMixin, DetailView):
    """
    Vista para ver el detalle de un movimiento.

    Permisos: bodega.view_movimiento
    """
    model = Movimiento
    template_name = 'bodega/movimiento/detalle.html'
    context_object_name = 'movimiento'
    permission_required = 'bodega.view_movimiento'

    def get_queryset(self) -> QuerySet:
        """Optimiza consultas con select_related."""
        return super().get_queryset().select_related(
            'articulo', 'tipo', 'usuario'
        ).filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detalle de Movimiento'
        return context
