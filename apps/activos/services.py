"""
Service Layer para el módulo de activos.

Contiene la lógica de negocio y coordina los repositories,
siguiendo el principio de Single Responsibility (SOLID).
"""
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    CategoriaActivo, UnidadMedida, EstadoActivo, Ubicacion,
    TipoMovimientoActivo, Activo, MovimientoActivo, UbicacionActual
)
from .repositories import (
    CategoriaActivoRepository, UnidadMedidaRepository,
    EstadoActivoRepository, UbicacionRepository,
    TipoMovimientoActivoRepository, ActivoRepository,
    MovimientoActivoRepository, UbicacionActualRepository
)


# ==================== ACTIVO SERVICE ====================

class ActivoService:
    """
    Service para lógica de negocio de Activo.

    Coordina operaciones complejas y validaciones de negocio.
    """

    def __init__(self):
        self.repository = ActivoRepository()
        self.estado_repo = EstadoActivoRepository()

    def crear_activo(
        self,
        codigo: str,
        nombre: str,
        categoria: CategoriaActivo,
        unidad_medida: UnidadMedida,
        descripcion: Optional[str] = None,
        marca: Optional[str] = None,
        modelo: Optional[str] = None,
        numero_serie: Optional[str] = None,
        stock_minimo: Decimal = Decimal('0'),
        stock_maximo: Optional[Decimal] = None,
        precio_unitario: Optional[Decimal] = None,
        requiere_serie: bool = False,
        requiere_lote: bool = False,
        requiere_vencimiento: bool = False
    ) -> Activo:
        """
        Crea un nuevo activo validando que no exista el código.

        Args:
            codigo: Código único del activo
            nombre: Nombre del activo
            categoria: Categoría del activo
            unidad_medida: Unidad de medida
            descripcion: Descripción opcional
            marca: Marca opcional
            modelo: Modelo opcional
            numero_serie: Número de serie opcional
            stock_minimo: Stock mínimo
            stock_maximo: Stock máximo opcional
            precio_unitario: Precio opcional
            requiere_serie: Indica si requiere número de serie
            requiere_lote: Indica si requiere lote
            requiere_vencimiento: Indica si requiere fecha de vencimiento

        Returns:
            Activo creado

        Raises:
            ValidationError: Si el código ya existe
        """
        # Validar unicidad del código
        if self.repository.exists_by_codigo(codigo):
            raise ValidationError(
                f'Ya existe un activo con el código "{codigo}".'
            )

        # Obtener estado inicial
        estado_inicial = self.estado_repo.get_inicial()
        if not estado_inicial:
            raise ValidationError(
                'No existe un estado inicial configurado. '
                'Por favor configure un estado como inicial en el catálogo.'
            )

        # Crear activo
        activo = Activo.objects.create(
            codigo=codigo.strip().upper(),
            nombre=nombre.strip(),
            descripcion=descripcion,
            categoria=categoria,
            unidad_medida=unidad_medida,
            estado=estado_inicial,
            marca=marca,
            modelo=modelo,
            numero_serie=numero_serie,
            stock_minimo=stock_minimo,
            stock_maximo=stock_maximo,
            precio_unitario=precio_unitario,
            requiere_serie=requiere_serie,
            requiere_lote=requiere_lote,
            requiere_vencimiento=requiere_vencimiento
        )

        return activo

    def actualizar_activo(
        self,
        activo: Activo,
        datos: Dict[str, Any]
    ) -> Activo:
        """
        Actualiza un activo existente.

        Args:
            activo: Activo a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Activo actualizado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar código si se está actualizando
        if 'codigo' in datos and datos['codigo'] != activo.codigo:
            if self.repository.exists_by_codigo(datos['codigo'], exclude_id=activo.id):
                raise ValidationError(
                    f'Ya existe un activo con el código "{datos["codigo"]}".'
                )

        # Actualizar campos
        for campo, valor in datos.items():
            if hasattr(activo, campo):
                if campo in ['codigo', 'nombre'] and isinstance(valor, str):
                    valor = valor.strip().upper() if campo == 'codigo' else valor.strip()
                setattr(activo, campo, valor)

        activo.save()
        return activo


# ==================== MOVIMIENTO ACTIVO SERVICE ====================

class MovimientoActivoService:
    """
    Service para lógica de negocio de MovimientoActivo.

    Coordina operaciones complejas de movimientos con actualización
    automática de ubicación actual.
    """

    def __init__(self):
        self.movimiento_repo = MovimientoActivoRepository()
        self.ubicacion_actual_repo = UbicacionActualRepository()

    @transaction.atomic
    def registrar_movimiento(
        self,
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
        """
        Registra un movimiento de activo y actualiza su ubicación actual.

        Esta operación es atómica: todo o nada.

        Args:
            activo: Activo a mover
            tipo_movimiento: Tipo de movimiento
            usuario_registro: Usuario que registra
            ubicacion_destino: Ubicación destino (opcional)
            responsable: Responsable del activo (opcional)
            numero_serie: Número de serie (opcional)
            lote: Lote (opcional)
            fecha_vencimiento: Fecha de vencimiento (opcional)
            observaciones: Observaciones (opcional)

        Returns:
            Movimiento creado

        Raises:
            ValidationError: Si faltan datos requeridos o hay errores de validación
        """
        # Validar campos requeridos según configuración del activo
        errors = {}

        if activo.requiere_serie and not numero_serie:
            errors['numero_serie'] = 'Este activo requiere número de serie'

        if activo.requiere_lote and not lote:
            errors['lote'] = 'Este activo requiere lote'

        if activo.requiere_vencimiento and not fecha_vencimiento:
            errors['fecha_vencimiento'] = 'Este activo requiere fecha de vencimiento'

        # Validar campos requeridos según tipo de movimiento
        if tipo_movimiento.requiere_ubicacion and not ubicacion_destino:
            errors['ubicacion_destino'] = 'Este tipo de movimiento requiere ubicación destino'

        if tipo_movimiento.requiere_responsable and not responsable:
            errors['responsable'] = 'Este tipo de movimiento requiere responsable'

        if errors:
            raise ValidationError(errors)

        # Validar que el estado del activo permita movimiento
        if not activo.estado.permite_movimiento:
            raise ValidationError(
                f'El activo está en estado "{activo.estado.nombre}" '
                f'que no permite movimientos.'
            )

        # Crear movimiento
        movimiento = self.movimiento_repo.create(
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

        # Actualizar ubicación actual
        self.ubicacion_actual_repo.update_or_create(
            activo=activo,
            ubicacion=ubicacion_destino,
            responsable=responsable,
            ultimo_movimiento=movimiento
        )

        return movimiento

    def obtener_historial_activo(
        self,
        activo: Activo,
        limit: int = 20
    ) -> list[MovimientoActivo]:
        """
        Obtiene el historial de movimientos de un activo.

        Args:
            activo: Activo del cual obtener el historial
            limit: Número máximo de movimientos a retornar

        Returns:
            Lista de movimientos ordenados por fecha descendente
        """
        return list(self.movimiento_repo.filter_by_activo(activo, limit))

    def obtener_ubicacion_actual(
        self,
        activo: Activo
    ) -> Optional[UbicacionActual]:
        """
        Obtiene la ubicación actual de un activo.

        Args:
            activo: Activo del cual obtener la ubicación

        Returns:
            UbicacionActual si existe, None en caso contrario
        """
        return self.ubicacion_actual_repo.get_by_activo(activo)

    def obtener_activos_por_ubicacion(
        self,
        ubicacion: Ubicacion
    ) -> list[UbicacionActual]:
        """
        Obtiene todos los activos en una ubicación específica.

        Args:
            ubicacion: Ubicación a consultar

        Returns:
            Lista de ubicaciones actuales en esa ubicación
        """
        return list(self.ubicacion_actual_repo.filter_by_ubicacion(ubicacion))

    def obtener_activos_por_responsable(
        self,
        responsable: User
    ) -> list[UbicacionActual]:
        """
        Obtiene todos los activos a cargo de un responsable.

        Args:
            responsable: Usuario responsable

        Returns:
            Lista de ubicaciones actuales a cargo del responsable
        """
        return list(self.ubicacion_actual_repo.filter_by_responsable(responsable))


# ==================== SERVICIOS DE CATÁLOGOS ====================

class CategoriaActivoService:
    """Service para lógica de negocio de CategoriaActivo."""

    def __init__(self):
        self.repository = CategoriaActivoRepository()

    def eliminar_categoria(self, categoria: CategoriaActivo) -> Tuple[bool, str]:
        """
        Elimina lógicamente una categoría.

        Valida que no tenga activos asociados activos.

        Args:
            categoria: Categoría a eliminar

        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar si tiene activos activos
        activos_activos = ActivoRepository.filter_by_categoria(categoria).filter(
            activo=True
        )

        if activos_activos.exists():
            count = activos_activos.count()
            return (
                False,
                f'No se puede eliminar la categoría porque tiene {count} '
                f'activo(s) activo(s) asociado(s).'
            )

        # Soft delete
        categoria.eliminado = True
        categoria.activo = False
        categoria.save()

        return (True, f'Categoría "{categoria.nombre}" eliminada exitosamente.')
