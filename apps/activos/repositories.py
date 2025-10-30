"""
Repository Pattern para el módulo de activos.

Separa la lógica de acceso a datos de la lógica de negocio,
siguiendo el principio de Inversión de Dependencias (SOLID).
"""
from typing import Optional, List
from decimal import Decimal
from django.db.models import QuerySet, Q
from django.contrib.auth.models import User
from .models import (
    CategoriaActivo, UnidadMedida, EstadoActivo, Ubicacion,
    TipoMovimientoActivo, Activo, MovimientoActivo, UbicacionActual
)


# ==================== REPOSITORIOS DE CATÁLOGOS ====================

class CategoriaActivoRepository:
    """Repository para gestionar acceso a datos de CategoriaActivo."""

    @staticmethod
    def get_all() -> QuerySet[CategoriaActivo]:
        """Retorna todas las categorías no eliminadas."""
        return CategoriaActivo.objects.filter(eliminado=False).order_by('codigo')

    @staticmethod
    def get_active() -> QuerySet[CategoriaActivo]:
        """Retorna solo categorías activas y no eliminadas."""
        return CategoriaActivo.objects.filter(activo=True, eliminado=False).order_by('codigo')

    @staticmethod
    def get_by_id(categoria_id: int) -> Optional[CategoriaActivo]:
        """Obtiene una categoría por su ID."""
        try:
            return CategoriaActivo.objects.get(id=categoria_id, eliminado=False)
        except CategoriaActivo.DoesNotExist:
            return None

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[CategoriaActivo]:
        """Obtiene una categoría por su código."""
        try:
            return CategoriaActivo.objects.get(codigo=codigo, eliminado=False)
        except CategoriaActivo.DoesNotExist:
            return None

    @staticmethod
    def search(query: str) -> QuerySet[CategoriaActivo]:
        """Búsqueda de categorías por código o nombre."""
        return CategoriaActivo.objects.filter(
            Q(codigo__icontains=query) | Q(nombre__icontains=query),
            eliminado=False
        ).order_by('codigo')


class UnidadMedidaRepository:
    """Repository para gestionar acceso a datos de UnidadMedida."""

    @staticmethod
    def get_all() -> QuerySet[UnidadMedida]:
        """Retorna todas las unidades no eliminadas."""
        return UnidadMedida.objects.filter(eliminado=False).order_by('codigo')

    @staticmethod
    def get_active() -> QuerySet[UnidadMedida]:
        """Retorna solo unidades activas y no eliminadas."""
        return UnidadMedida.objects.filter(activo=True, eliminado=False).order_by('codigo')

    @staticmethod
    def get_by_id(unidad_id: int) -> Optional[UnidadMedida]:
        """Obtiene una unidad por su ID."""
        try:
            return UnidadMedida.objects.get(id=unidad_id, eliminado=False)
        except UnidadMedida.DoesNotExist:
            return None


class EstadoActivoRepository:
    """Repository para gestionar acceso a datos de EstadoActivo."""

    @staticmethod
    def get_all() -> QuerySet[EstadoActivo]:
        """Retorna todos los estados no eliminados."""
        return EstadoActivo.objects.filter(eliminado=False).order_by('codigo')

    @staticmethod
    def get_active() -> QuerySet[EstadoActivo]:
        """Retorna solo estados activos y no eliminados."""
        return EstadoActivo.objects.filter(activo=True, eliminado=False).order_by('codigo')

    @staticmethod
    def get_by_id(estado_id: int) -> Optional[EstadoActivo]:
        """Obtiene un estado por su ID."""
        try:
            return EstadoActivo.objects.get(id=estado_id, eliminado=False)
        except EstadoActivo.DoesNotExist:
            return None

    @staticmethod
    def get_inicial() -> Optional[EstadoActivo]:
        """Obtiene el estado inicial del sistema."""
        return EstadoActivo.objects.filter(
            es_inicial=True, activo=True, eliminado=False
        ).first()


class UbicacionRepository:
    """Repository para gestionar acceso a datos de Ubicacion."""

    @staticmethod
    def get_all() -> QuerySet[Ubicacion]:
        """Retorna todas las ubicaciones no eliminadas."""
        return Ubicacion.objects.filter(eliminado=False).order_by('codigo')

    @staticmethod
    def get_active() -> QuerySet[Ubicacion]:
        """Retorna solo ubicaciones activas y no eliminadas."""
        return Ubicacion.objects.filter(activo=True, eliminado=False).order_by('codigo')

    @staticmethod
    def get_by_id(ubicacion_id: int) -> Optional[Ubicacion]:
        """Obtiene una ubicación por su ID."""
        try:
            return Ubicacion.objects.get(id=ubicacion_id, eliminado=False)
        except Ubicacion.DoesNotExist:
            return None

    @staticmethod
    def search(query: str) -> QuerySet[Ubicacion]:
        """Búsqueda de ubicaciones por código, nombre, edificio o área."""
        return Ubicacion.objects.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(edificio__icontains=query) |
            Q(area__icontains=query),
            eliminado=False
        ).order_by('codigo')


class TipoMovimientoActivoRepository:
    """Repository para gestionar acceso a datos de TipoMovimientoActivo."""

    @staticmethod
    def get_all() -> QuerySet[TipoMovimientoActivo]:
        """Retorna todos los tipos de movimiento no eliminados."""
        return TipoMovimientoActivo.objects.filter(eliminado=False).order_by('codigo')

    @staticmethod
    def get_active() -> QuerySet[TipoMovimientoActivo]:
        """Retorna solo tipos activos y no eliminados."""
        return TipoMovimientoActivo.objects.filter(activo=True, eliminado=False).order_by('codigo')

    @staticmethod
    def get_by_id(tipo_id: int) -> Optional[TipoMovimientoActivo]:
        """Obtiene un tipo de movimiento por su ID."""
        try:
            return TipoMovimientoActivo.objects.get(id=tipo_id, eliminado=False)
        except TipoMovimientoActivo.DoesNotExist:
            return None


# ==================== ACTIVO REPOSITORY ====================

class ActivoRepository:
    """Repository para gestionar acceso a datos de Activo."""

    @staticmethod
    def get_all() -> QuerySet[Activo]:
        """Retorna todos los activos no eliminados con relaciones optimizadas."""
        return Activo.objects.filter(
            eliminado=False
        ).select_related(
            'categoria', 'unidad_medida', 'estado'
        ).order_by('codigo')

    @staticmethod
    def get_active() -> QuerySet[Activo]:
        """Retorna solo activos activos y no eliminados."""
        return Activo.objects.filter(
            activo=True, eliminado=False
        ).select_related(
            'categoria', 'unidad_medida', 'estado'
        ).order_by('codigo')

    @staticmethod
    def get_by_id(activo_id: int) -> Optional[Activo]:
        """Obtiene un activo por su ID."""
        try:
            return Activo.objects.select_related(
                'categoria', 'unidad_medida', 'estado'
            ).get(id=activo_id, eliminado=False)
        except Activo.DoesNotExist:
            return None

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Activo]:
        """Obtiene un activo por su código."""
        try:
            return Activo.objects.select_related(
                'categoria', 'unidad_medida', 'estado'
            ).get(codigo=codigo, eliminado=False)
        except Activo.DoesNotExist:
            return None

    @staticmethod
    def filter_by_categoria(categoria: CategoriaActivo) -> QuerySet[Activo]:
        """Retorna activos de una categoría específica."""
        return Activo.objects.filter(
            categoria=categoria,
            eliminado=False
        ).select_related(
            'categoria', 'unidad_medida', 'estado'
        ).order_by('codigo')

    @staticmethod
    def filter_by_estado(estado: EstadoActivo) -> QuerySet[Activo]:
        """Retorna activos en un estado específico."""
        return Activo.objects.filter(
            estado=estado,
            eliminado=False
        ).select_related(
            'categoria', 'unidad_medida', 'estado'
        ).order_by('codigo')

    @staticmethod
    def search(query: str) -> QuerySet[Activo]:
        """Búsqueda de activos por código, nombre, marca, modelo o serie."""
        return Activo.objects.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(marca__icontains=query) |
            Q(modelo__icontains=query) |
            Q(numero_serie__icontains=query),
            eliminado=False
        ).select_related(
            'categoria', 'unidad_medida', 'estado'
        ).order_by('codigo')

    @staticmethod
    def exists_by_codigo(codigo: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un activo con el código dado."""
        queryset = Activo.objects.filter(codigo=codigo)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()


# ==================== MOVIMIENTO ACTIVO REPOSITORY ====================

class MovimientoActivoRepository:
    """Repository para gestionar acceso a datos de MovimientoActivo."""

    @staticmethod
    def get_all() -> QuerySet[MovimientoActivo]:
        """Retorna todos los movimientos con relaciones optimizadas."""
        return MovimientoActivo.objects.select_related(
            'activo', 'tipo_movimiento', 'ubicacion_destino',
            'responsable', 'usuario_registro'
        ).order_by('-fecha_movimiento')

    @staticmethod
    def get_by_id(movimiento_id: int) -> Optional[MovimientoActivo]:
        """Obtiene un movimiento por su ID."""
        try:
            return MovimientoActivo.objects.select_related(
                'activo', 'tipo_movimiento', 'ubicacion_destino',
                'responsable', 'usuario_registro'
            ).get(id=movimiento_id)
        except MovimientoActivo.DoesNotExist:
            return None

    @staticmethod
    def filter_by_activo(activo: Activo, limit: int = 20) -> QuerySet[MovimientoActivo]:
        """Retorna movimientos de un activo específico."""
        return MovimientoActivo.objects.filter(
            activo=activo
        ).select_related(
            'tipo_movimiento', 'ubicacion_destino', 'responsable', 'usuario_registro'
        ).order_by('-fecha_movimiento')[:limit]

    @staticmethod
    def filter_by_ubicacion(ubicacion: Ubicacion) -> QuerySet[MovimientoActivo]:
        """Retorna movimientos hacia una ubicación específica."""
        return MovimientoActivo.objects.filter(
            ubicacion_destino=ubicacion
        ).select_related(
            'activo', 'tipo_movimiento', 'responsable', 'usuario_registro'
        ).order_by('-fecha_movimiento')

    @staticmethod
    def filter_by_responsable(responsable: User) -> QuerySet[MovimientoActivo]:
        """Retorna movimientos de un responsable específico."""
        return MovimientoActivo.objects.filter(
            responsable=responsable
        ).select_related(
            'activo', 'tipo_movimiento', 'ubicacion_destino', 'usuario_registro'
        ).order_by('-fecha_movimiento')

    @staticmethod
    def create(
        activo: Activo,
        tipo_movimiento: TipoMovimientoActivo,
        usuario_registro: User,
        ubicacion_destino: Optional[Ubicacion] = None,
        responsable: Optional[User] = None,
        numero_serie: Optional[str] = None,
        lote: Optional[str] = None,
        fecha_vencimiento: Optional[str] = None,
        observaciones: Optional[str] = None
    ) -> MovimientoActivo:
        """Crea un nuevo movimiento."""
        return MovimientoActivo.objects.create(
            activo=activo,
            tipo_movimiento=tipo_movimiento,
            usuario_registro=usuario_registro,
            ubicacion_destino=ubicacion_destino,
            responsable=responsable,
            numero_serie=numero_serie,
            lote=lote,
            fecha_vencimiento=fecha_vencimiento,
            observaciones=observaciones
        )


# ==================== UBICACION ACTUAL REPOSITORY ====================

class UbicacionActualRepository:
    """Repository para gestionar acceso a datos de UbicacionActual."""

    @staticmethod
    def get_all() -> QuerySet[UbicacionActual]:
        """Retorna todas las ubicaciones actuales con relaciones optimizadas."""
        return UbicacionActual.objects.select_related(
            'activo', 'ubicacion', 'responsable', 'ultimo_movimiento'
        )

    @staticmethod
    def get_by_activo(activo: Activo) -> Optional[UbicacionActual]:
        """Obtiene la ubicación actual de un activo."""
        try:
            return UbicacionActual.objects.select_related(
                'ubicacion', 'responsable', 'ultimo_movimiento'
            ).get(activo=activo)
        except UbicacionActual.DoesNotExist:
            return None

    @staticmethod
    def filter_by_ubicacion(ubicacion: Ubicacion) -> QuerySet[UbicacionActual]:
        """Retorna activos en una ubicación específica."""
        return UbicacionActual.objects.filter(
            ubicacion=ubicacion
        ).select_related(
            'activo', 'responsable', 'ultimo_movimiento'
        )

    @staticmethod
    def filter_by_responsable(responsable: User) -> QuerySet[UbicacionActual]:
        """Retorna activos a cargo de un responsable."""
        return UbicacionActual.objects.filter(
            responsable=responsable
        ).select_related(
            'activo', 'ubicacion', 'ultimo_movimiento'
        )

    @staticmethod
    def update_or_create(
        activo: Activo,
        ubicacion: Optional[Ubicacion],
        responsable: Optional[User],
        ultimo_movimiento: MovimientoActivo
    ) -> UbicacionActual:
        """Actualiza o crea la ubicación actual de un activo."""
        ubicacion_actual, created = UbicacionActual.objects.update_or_create(
            activo=activo,
            defaults={
                'ubicacion': ubicacion,
                'responsable': responsable,
                'ultimo_movimiento': ultimo_movimiento
            }
        )
        return ubicacion_actual
