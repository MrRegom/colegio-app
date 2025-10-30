"""
Class-Based Views para el módulo de bajas de inventario.

Este archivo implementa todas las vistas usando CBVs siguiendo SOLID y DRY:
- Reutilización de mixins de core.mixins
- Separación de responsabilidades (Repository Pattern + Service Layer)
- Código limpio y mantenible
- Type hints completos
- Auditoría automática
- Workflow de autorización
"""
from typing import Any
from decimal import Decimal
from django.db.models import QuerySet, Q
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from core.mixins import (
    BaseAuditedViewMixin, AtomicTransactionMixin, SoftDeleteMixin,
    PaginatedListMixin, FilteredListMixin
)
from core.utils import registrar_log_auditoria
from .models import BajaInventario, DetalleBaja, MotivoBaja, EstadoBaja, HistorialBaja
from .forms import (
    BajaInventarioForm, DetalleBajaFormSet, AutorizarBajaForm,
    RechazarBajaForm, FiltroBajasForm
)
from .repositories import (
    MotivoBajaRepository, EstadoBajaRepository, BajaInventarioRepository,
    DetalleBajaRepository, HistorialBajaRepository
)
from .services import BajaInventarioService, DetalleBajaService


# ==================== VISTA MENÚ PRINCIPAL ====================

class MenuBajasView(BaseAuditedViewMixin, TemplateView):
    """
    Vista del menú principal del módulo de bajas de inventario.

    Muestra estadísticas y accesos rápidos basados en permisos del usuario.
    Permisos: bajas_inventario.view_bajainventario
    """
    template_name = 'bajas_inventario/menu_bajas.html'
    permission_required = 'bajas_inventario.view_bajainventario'

    def get_context_data(self, **kwargs) -> dict:
        """Agrega estadísticas y permisos al contexto."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Inicializar repositorios
        baja_repo = BajaInventarioRepository()
        estado_repo = EstadoBajaRepository()

        # Estadísticas del módulo
        estado_pendiente = estado_repo.get_by_codigo('PENDIENTE')
        estado_autorizada = estado_repo.get_by_codigo('AUTORIZADA')

        context['stats'] = {
            'total_bajas': baja_repo.get_all().count(),
            'mis_bajas': baja_repo.filter_by_solicitante(user).count(),
            'pendientes_autorizacion': baja_repo.filter_by_estado(estado_pendiente).count() if estado_pendiente else 0,
            'autorizadas': baja_repo.filter_by_estado(estado_autorizada).count() if estado_autorizada else 0,
        }

        # Permisos del usuario
        context['permisos'] = {
            'puede_crear': user.has_perm('bajas_inventario.add_bajainventario'),
            'puede_autorizar': user.has_perm('bajas_inventario.autorizar_bajainventario'),
            'puede_gestionar': user.has_perm('bajas_inventario.change_bajainventario'),
        }

        context['titulo'] = 'Módulo de Bajas de Inventario'
        return context


# ==================== VISTAS DE BAJAS DE INVENTARIO ====================

class BajaInventarioListView(BaseAuditedViewMixin, PaginatedListMixin, FilteredListMixin, ListView):
    """
    Vista para listar todas las bajas de inventario con filtros.

    Permisos: bajas_inventario.view_bajainventario
    Filtros: Estado, motivo, fechas, búsqueda
    """
    model = BajaInventario
    template_name = 'bajas_inventario/lista_bajas.html'
    context_object_name = 'bajas'
    permission_required = 'bajas_inventario.view_bajainventario'
    paginate_by = 25
    filter_form_class = FiltroBajasForm

    def get_queryset(self) -> QuerySet:
        """Retorna bajas no eliminadas con relaciones optimizadas y filtros."""
        queryset = super().get_queryset().filter(
            eliminado=False
        ).select_related(
            'motivo', 'estado', 'solicitante', 'bodega', 'autorizador'
        )

        # Aplicar filtros del formulario
        form = self.filter_form_class(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data

            if data.get('estado'):
                queryset = queryset.filter(estado=data['estado'])

            if data.get('motivo'):
                queryset = queryset.filter(motivo=data['motivo'])

            if data.get('fecha_desde'):
                queryset = queryset.filter(fecha_baja__gte=data['fecha_desde'])

            if data.get('fecha_hasta'):
                queryset = queryset.filter(fecha_baja__lte=data['fecha_hasta'])

            if data.get('buscar'):
                q = data['buscar']
                queryset = queryset.filter(
                    Q(numero__icontains=q) |
                    Q(descripcion__icontains=q)
                )

        return queryset.order_by('-fecha_baja')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Bajas de Inventario'
        context['form'] = self.filter_form_class(self.request.GET)
        return context


class BajaInventarioDetailView(BaseAuditedViewMixin, DetailView):
    """
    Vista para ver el detalle de una baja de inventario.

    Permisos: bajas_inventario.view_bajainventario
    """
    model = BajaInventario
    template_name = 'bajas_inventario/detalle_baja.html'
    context_object_name = 'baja'
    permission_required = 'bajas_inventario.view_bajainventario'

    def get_queryset(self) -> QuerySet:
        """Optimiza consultas con select_related y filtra eliminados."""
        return super().get_queryset().filter(eliminado=False).select_related(
            'motivo', 'estado', 'solicitante', 'autorizador', 'bodega'
        )

    def get_context_data(self, **kwargs) -> dict:
        """Agrega detalles y historial al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Baja {self.object.numero}'

        # Detalles de la baja
        context['detalles'] = self.object.detalles.filter(
            eliminado=False
        ).select_related(
            'activo', 'activo__unidad_medida', 'activo__categoria'
        )

        # Historial de cambios
        context['historial'] = self.object.historial.filter(
            eliminado=False
        ).select_related(
            'estado_anterior', 'estado_nuevo', 'usuario'
        )

        return context


class MisBajasListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para ver las bajas solicitadas por el usuario actual.

    Permisos: bajas_inventario.view_bajainventario
    """
    model = BajaInventario
    template_name = 'bajas_inventario/mis_bajas.html'
    context_object_name = 'bajas'
    permission_required = 'bajas_inventario.view_bajainventario'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo las bajas del usuario actual no eliminadas."""
        return super().get_queryset().filter(
            solicitante=self.request.user,
            eliminado=False
        ).select_related(
            'motivo', 'estado', 'bodega'
        ).order_by('-fecha_baja')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mis Bajas Solicitadas'
        return context


class BajasPorAutorizarListView(BaseAuditedViewMixin, PaginatedListMixin, ListView):
    """
    Vista para ver las bajas pendientes de autorización.

    Permisos: bajas_inventario.autorizar_bajainventario
    """
    model = BajaInventario
    template_name = 'bajas_inventario/bajas_por_autorizar.html'
    context_object_name = 'bajas'
    permission_required = 'bajas_inventario.autorizar_bajainventario'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Retorna solo bajas pendientes no eliminadas."""
        return super().get_queryset().filter(
            estado__codigo='PENDIENTE',
            eliminado=False
        ).select_related(
            'motivo', 'estado', 'solicitante', 'bodega'
        ).order_by('fecha_baja')

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Bajas Pendientes de Autorización'
        return context


class BajaInventarioCreateView(BaseAuditedViewMixin, AtomicTransactionMixin, CreateView):
    """
    Vista para crear una nueva baja de inventario.

    Permisos: bajas_inventario.add_bajainventario
    Auditoría: Registra acción CREAR automáticamente
    Transacción atómica: Garantiza que baja y detalles se creen correctamente
    """
    model = BajaInventario
    form_class = BajaInventarioForm
    template_name = 'bajas_inventario/form_baja.html'
    permission_required = 'bajas_inventario.add_bajainventario'

    # Configuración de auditoría
    audit_action = 'CREAR'
    audit_description_template = 'Creó baja de inventario {obj.numero}'

    # Mensaje de éxito
    success_message = 'Baja {obj.numero} creada exitosamente.'

    def get_success_url(self) -> str:
        """Redirige al detalle de la baja creada."""
        return reverse_lazy('bajas_inventario:detalle_baja', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs) -> dict:
        """Agrega formset y datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva Baja de Inventario'
        context['action'] = 'Crear'

        if self.request.POST:
            context['formset'] = DetalleBajaFormSet(self.request.POST)
        else:
            context['formset'] = DetalleBajaFormSet()

        return context

    def form_valid(self, form):
        """Procesa el formulario válido con formset usando service layer."""
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            try:
                # Inicializar services
                baja_service = BajaInventarioService()
                detalle_service = DetalleBajaService()

                # Preparar datos del formulario
                motivo = form.cleaned_data['motivo']
                bodega = form.cleaned_data['bodega']
                fecha_baja = form.cleaned_data['fecha_baja']
                descripcion = form.cleaned_data['descripcion']
                observaciones = form.cleaned_data.get('observaciones', '')
                documento = form.cleaned_data.get('documento')

                # Crear la baja usando service
                baja = baja_service.crear_baja(
                    motivo=motivo,
                    bodega=bodega,
                    solicitante=self.request.user,
                    fecha_baja=fecha_baja,
                    descripcion=descripcion,
                    observaciones=observaciones,
                    documento=documento
                )

                # Guardar los detalles usando service
                for detalle_form in formset:
                    if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE'):
                        detalle_service.agregar_detalle(
                            baja=baja,
                            activo=detalle_form.cleaned_data['activo'],
                            cantidad=detalle_form.cleaned_data['cantidad'],
                            valor_unitario=detalle_form.cleaned_data['valor_unitario'],
                            lote=detalle_form.cleaned_data.get('lote', ''),
                            numero_serie=detalle_form.cleaned_data.get('numero_serie', ''),
                            observaciones=detalle_form.cleaned_data.get('observaciones', '')
                        )

                self.object = baja

                # Continuar con el flujo normal (mensaje y redirección)
                response = super().form_valid(form)
                self.log_action(self.object, self.request)
                return response

            except ValidationError as e:
                # Manejar errores de validación del service
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(self.request, f'{field}: {error}')
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class BajaInventarioUpdateView(BaseAuditedViewMixin, AtomicTransactionMixin, UpdateView):
    """
    Vista para editar una baja de inventario existente.

    Permisos: bajas_inventario.change_bajainventario
    Auditoría: Registra acción EDITAR automáticamente
    Transacción atómica: Garantiza consistencia de datos
    """
    model = BajaInventario
    form_class = BajaInventarioForm
    template_name = 'bajas_inventario/form_baja.html'
    permission_required = 'bajas_inventario.change_bajainventario'

    # Configuración de auditoría
    audit_action = 'EDITAR'
    audit_description_template = 'Editó baja de inventario {obj.numero}'

    # Mensaje de éxito
    success_message = 'Baja {obj.numero} actualizada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Filtra bajas según permisos del usuario."""
        queryset = super().get_queryset().filter(eliminado=False)

        # Si no tiene permiso para editar cualquier baja, solo las propias
        if not self.request.user.has_perm('bajas_inventario.change_any_bajainventario'):
            queryset = queryset.filter(solicitante=self.request.user)

        return queryset

    def get_success_url(self) -> str:
        """Redirige al detalle de la baja editada."""
        return reverse_lazy('bajas_inventario:detalle_baja', kwargs={'pk': self.object.pk})

    def get(self, request, *args, **kwargs):
        """Verifica que la baja pueda ser editada."""
        self.object = self.get_object()

        # Verificar permisos de edición
        if self.object.solicitante != request.user and not request.user.has_perm('bajas_inventario.change_any_bajainventario'):
            messages.error(request, 'No tiene permisos para editar esta baja.')
            return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

        # No permitir edición si ya fue autorizada o está en estado final
        if not self.object.estado.permite_edicion or self.object.estado.es_final:
            messages.warning(request, 'No se puede editar una baja en este estado.')
            return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega formset y datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Baja {self.object.numero}'
        context['action'] = 'Editar'
        context['baja'] = self.object

        if self.request.POST:
            context['formset'] = DetalleBajaFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DetalleBajaFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        """Procesa el formulario válido con formset."""
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            form.save()
            formset.save()

            # Recalcular valor total
            valor_total = sum(
                detalle.valor_total
                for detalle in self.object.detalles.filter(eliminado=False)
            )
            self.object.valor_total = valor_total
            self.object.save()

            # Continuar con el flujo normal (mensaje y redirección)
            response = super().form_valid(form)
            self.log_action(self.object, self.request)
            return response
        else:
            return self.form_invalid(form)


class BajaInventarioDeleteView(BaseAuditedViewMixin, SoftDeleteMixin, DeleteView):
    """
    Vista para eliminar (soft delete) una baja de inventario.

    Permisos: bajas_inventario.delete_bajainventario
    Auditoría: Registra acción ELIMINAR automáticamente
    Implementa soft delete
    """
    model = BajaInventario
    template_name = 'bajas_inventario/eliminar_baja.html'
    permission_required = 'bajas_inventario.delete_bajainventario'
    success_url = reverse_lazy('bajas_inventario:lista_bajas')

    # Configuración de auditoría
    audit_action = 'ELIMINAR'
    audit_description_template = 'Eliminó baja de inventario {obj.numero}'

    # Mensaje de éxito
    success_message = 'Baja {obj.numero} eliminada exitosamente.'

    def get_queryset(self) -> QuerySet:
        """Filtra bajas según permisos del usuario."""
        queryset = super().get_queryset().filter(eliminado=False)

        # Si no tiene permiso para eliminar cualquier baja, solo las propias
        if not self.request.user.has_perm('bajas_inventario.delete_any_bajainventario'):
            queryset = queryset.filter(solicitante=self.request.user)

        return queryset

    def get(self, request, *args, **kwargs):
        """Verifica que la baja pueda ser eliminada."""
        self.object = self.get_object()

        # Verificar permisos de eliminación
        if self.object.solicitante != request.user and not request.user.has_perm('bajas_inventario.delete_any_bajainventario'):
            messages.error(request, 'No tiene permisos para eliminar esta baja.')
            return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

        # Solo se pueden eliminar bajas en estado inicial
        if not self.object.estado.es_inicial:
            messages.warning(request, 'Solo se pueden eliminar bajas en estado inicial.')
            return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar Baja {self.object.numero}'
        context['baja'] = self.object
        return context


# ==================== VISTAS DE WORKFLOW (AUTORIZAR, RECHAZAR) ====================

class BajaInventarioAutorizarView(BaseAuditedViewMixin, AtomicTransactionMixin, DetailView):
    """
    Vista para autorizar una baja de inventario.

    Permisos: bajas_inventario.autorizar_bajainventario
    Auditoría: Registra acción APROBAR automáticamente
    Transacción atómica: Garantiza consistencia del workflow
    """
    model = BajaInventario
    template_name = 'bajas_inventario/autorizar_baja.html'
    context_object_name = 'baja'
    permission_required = 'bajas_inventario.autorizar_bajainventario'

    # Configuración de auditoría
    audit_action = 'APROBAR'
    audit_description_template = 'Autorizó baja de inventario {obj.numero}'

    def get_queryset(self) -> QuerySet:
        """Solo bajas no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega formulario y datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Autorizar Baja {self.object.numero}'

        if self.request.POST:
            context['form'] = AutorizarBajaForm(self.request.POST)
        else:
            context['form'] = AutorizarBajaForm()

        return context

    def get(self, request, *args, **kwargs):
        """Verifica que la baja pueda ser autorizada."""
        self.object = self.get_object()

        # Verificar que esté pendiente
        if self.object.estado.codigo != 'PENDIENTE':
            messages.warning(request, 'Esta baja no está pendiente de autorización.')
            return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la autorización de la baja usando service layer."""
        self.object = self.get_object()
        form = AutorizarBajaForm(request.POST)

        if form.is_valid():
            try:
                # Inicializar service
                baja_service = BajaInventarioService()

                # Autorizar baja usando service
                self.object = baja_service.autorizar_baja(
                    baja=self.object,
                    autorizador=request.user,
                    notas_autorizacion=form.cleaned_data.get('notas_autorizacion', '')
                )

                # Log de auditoría
                self.log_action(self.object, request)

                messages.success(request, f'Baja {self.object.numero} autorizada exitosamente.')
                return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

            except ValidationError as e:
                # Manejar errores de validación del service
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                else:
                    messages.error(request, str(e))
                return self.render_to_response(self.get_context_data(form=form))

        # Si el formulario no es válido, mostrar errores
        return self.render_to_response(self.get_context_data(form=form))


class BajaInventarioRechazarView(BaseAuditedViewMixin, AtomicTransactionMixin, DetailView):
    """
    Vista para rechazar una baja de inventario.

    Permisos: bajas_inventario.autorizar_bajainventario
    Auditoría: Registra acción RECHAZAR automáticamente
    Transacción atómica: Garantiza consistencia del workflow
    """
    model = BajaInventario
    template_name = 'bajas_inventario/rechazar_baja.html'
    context_object_name = 'baja'
    permission_required = 'bajas_inventario.autorizar_bajainventario'

    # Configuración de auditoría
    audit_action = 'RECHAZAR'
    audit_description_template = 'Rechazó baja de inventario {obj.numero}'

    def get_queryset(self) -> QuerySet:
        """Solo bajas no eliminadas."""
        return super().get_queryset().filter(eliminado=False)

    def get_context_data(self, **kwargs) -> dict:
        """Agrega formulario y datos al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Rechazar Baja {self.object.numero}'

        if self.request.POST:
            context['form'] = RechazarBajaForm(self.request.POST)
        else:
            context['form'] = RechazarBajaForm()

        return context

    def get(self, request, *args, **kwargs):
        """Verifica que la baja pueda ser rechazada."""
        self.object = self.get_object()

        # Verificar que esté pendiente
        if self.object.estado.codigo != 'PENDIENTE':
            messages.warning(request, 'Esta baja no está pendiente de autorización.')
            return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el rechazo de la baja usando service layer."""
        self.object = self.get_object()
        form = RechazarBajaForm(request.POST)

        if form.is_valid():
            try:
                # Inicializar service
                baja_service = BajaInventarioService()

                # Rechazar baja usando service
                self.object = baja_service.rechazar_baja(
                    baja=self.object,
                    rechazador=request.user,
                    motivo_rechazo=form.cleaned_data['motivo_rechazo']
                )

                # Log de auditoría
                self.log_action(self.object, request)

                messages.success(request, f'Baja {self.object.numero} rechazada.')
                return redirect('bajas_inventario:detalle_baja', pk=self.object.pk)

            except ValidationError as e:
                # Manejar errores de validación del service
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                else:
                    messages.error(request, str(e))
                return self.render_to_response(self.get_context_data(form=form))

        # Si el formulario no es válido, mostrar errores
        return self.render_to_response(self.get_context_data(form=form))
