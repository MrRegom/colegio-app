"""
Service Layer para el módulo de bodega.

Contiene la lógica de negocio y coordina los repositories,
siguiendo el principio de Single Responsibility (SOLID).
"""
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Categoria, Articulo, TipoMovimiento, Movimiento, Bodega
from .repositories import (
    CategoriaRepository,
    ArticuloRepository,
    TipoMovimientoRepository,
    MovimientoRepository,
    BodegaRepository
)


# ==================== CATEGORÍA SERVICE ====================

class CategoriaService:
    """
    Service para lógica de negocio de Categoría.

    Coordina operaciones complejas y validaciones de negocio.
    """

    def __init__(self):
        self.repository = CategoriaRepository()

    def crear_categoria(
        self,
        codigo: str,
        nombre: str,
        descripcion: Optional[str] = None,
        observaciones: Optional[str] = None
    ) -> Categoria:
        """
        Crea una nueva categoría validando que no exista el código.

        Args:
            codigo: Código único de la categoría
            nombre: Nombre de la categoría
            descripcion: Descripción opcional
            observaciones: Observaciones opcionales

        Returns:
            Categoría creada

        Raises:
            ValidationError: Si el código ya existe
        """
        # Validar unicidad del código
        if self.repository.exists_by_codigo(codigo):
            raise ValidationError(
                f'Ya existe una categoría con el código "{codigo}".'
            )

        # Crear categoría
        categoria = Categoria.objects.create(
            codigo=codigo.strip().upper(),
            nombre=nombre.strip(),
            descripcion=descripcion,
            observaciones=observaciones
        )

        return categoria

    def actualizar_categoria(
        self,
        categoria: Categoria,
        codigo: Optional[str] = None,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        observaciones: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> Categoria:
        """
        Actualiza una categoría existente.

        Args:
            categoria: Categoría a actualizar
            codigo: Nuevo código (opcional)
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            observaciones: Nuevas observaciones (opcional)
            activo: Nuevo estado activo (opcional)

        Returns:
            Categoría actualizada

        Raises:
            ValidationError: Si el nuevo código ya existe
        """
        # Validar código si se está actualizando
        if codigo and codigo != categoria.codigo:
            if self.repository.exists_by_codigo(codigo, exclude_id=categoria.id):
                raise ValidationError(
                    f'Ya existe una categoría con el código "{codigo}".'
                )
            categoria.codigo = codigo.strip().upper()

        # Actualizar campos
        if nombre:
            categoria.nombre = nombre.strip()
        if descripcion is not None:
            categoria.descripcion = descripcion
        if observaciones is not None:
            categoria.observaciones = observaciones
        if activo is not None:
            categoria.activo = activo

        categoria.save()
        return categoria

    def eliminar_categoria(self, categoria: Categoria) -> Tuple[bool, str]:
        """
        Elimina lógicamente una categoría (soft delete).

        Valida que no tenga artículos asociados activos.

        Args:
            categoria: Categoría a eliminar

        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar si tiene artículos activos
        articulos_activos = ArticuloRepository.filter_by_categoria(categoria).filter(
            activo=True
        )

        if articulos_activos.exists():
            count = articulos_activos.count()
            return (
                False,
                f'No se puede eliminar la categoría porque tiene {count} '
                f'artículo(s) activo(s) asociado(s).'
            )

        # Soft delete
        categoria.eliminado = True
        categoria.activo = False
        categoria.save()

        return (True, f'Categoría "{categoria.nombre}" eliminada exitosamente.')


# ==================== ARTÍCULO SERVICE ====================

class ArticuloService:
    """
    Service para lógica de negocio de Artículo.

    Coordina operaciones complejas y validaciones de negocio.
    """

    def __init__(self):
        self.repository = ArticuloRepository()

    def crear_articulo(
        self,
        sku: str,
        codigo: str,
        nombre: str,
        categoria: Categoria,
        ubicacion_fisica: Bodega,
        unidad_medida: str,
        stock_minimo: Decimal = Decimal('0'),
        stock_maximo: Optional[Decimal] = None,
        punto_reorden: Optional[Decimal] = None,
        descripcion: Optional[str] = None,
        marca: Optional[str] = None,
        observaciones: Optional[str] = None
    ) -> Articulo:
        """
        Crea un nuevo artículo validando que no exista el SKU.

        Args:
            sku: SKU único del artículo
            codigo: Código del artículo
            nombre: Nombre del artículo
            categoria: Categoría del artículo
            ubicacion_fisica: Bodega donde se almacena
            unidad_medida: Unidad de medida
            stock_minimo: Stock mínimo permitido
            stock_maximo: Stock máximo permitido (opcional)
            punto_reorden: Punto de reorden (opcional)
            descripcion: Descripción (opcional)
            marca: Marca (opcional)
            observaciones: Observaciones (opcional)

        Returns:
            Artículo creado

        Raises:
            ValidationError: Si el SKU ya existe o hay errores de validación
        """
        # Validar unicidad del SKU
        if self.repository.exists_by_sku(sku):
            raise ValidationError(
                f'Ya existe un artículo con el SKU "{sku}".'
            )

        # Validar stock_maximo > stock_minimo
        if stock_maximo and stock_maximo < stock_minimo:
            raise ValidationError(
                'El stock máximo no puede ser menor que el stock mínimo.'
            )

        # Validar punto_reorden >= stock_minimo
        if punto_reorden and punto_reorden < stock_minimo:
            raise ValidationError(
                'El punto de reorden no puede ser menor que el stock mínimo.'
            )

        # Crear artículo
        articulo = Articulo.objects.create(
            sku=sku.strip().upper(),
            codigo=codigo.strip().upper(),
            nombre=nombre.strip(),
            categoria=categoria,
            ubicacion_fisica=ubicacion_fisica,
            unidad_medida=unidad_medida.strip(),
            stock_minimo=stock_minimo,
            stock_maximo=stock_maximo,
            punto_reorden=punto_reorden,
            descripcion=descripcion,
            marca=marca,
            observaciones=observaciones
        )

        return articulo

    def actualizar_articulo(
        self,
        articulo: Articulo,
        datos: Dict[str, Any]
    ) -> Articulo:
        """
        Actualiza un artículo existente.

        Args:
            articulo: Artículo a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Artículo actualizado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar SKU si se está actualizando
        if 'sku' in datos and datos['sku'] != articulo.sku:
            if self.repository.exists_by_sku(datos['sku'], exclude_id=articulo.id):
                raise ValidationError(
                    f'Ya existe un artículo con el SKU "{datos["sku"]}".'
                )

        # Validar stocks
        stock_min = datos.get('stock_minimo', articulo.stock_minimo)
        stock_max = datos.get('stock_maximo', articulo.stock_maximo)
        punto_reorden = datos.get('punto_reorden', articulo.punto_reorden)

        if stock_max and stock_max < stock_min:
            raise ValidationError(
                'El stock máximo no puede ser menor que el stock mínimo.'
            )

        if punto_reorden and punto_reorden < stock_min:
            raise ValidationError(
                'El punto de reorden no puede ser menor que el stock mínimo.'
            )

        # Actualizar campos
        for campo, valor in datos.items():
            if hasattr(articulo, campo):
                if campo in ['sku', 'codigo', 'nombre', 'unidad_medida'] and isinstance(valor, str):
                    valor = valor.strip().upper() if campo in ['sku', 'codigo'] else valor.strip()
                setattr(articulo, campo, valor)

        articulo.save()
        return articulo

    def obtener_articulos_bajo_stock(self) -> list[Articulo]:
        """
        Retorna lista de artículos con stock bajo el mínimo.

        Returns:
            Lista de artículos con stock crítico
        """
        return list(self.repository.get_low_stock())

    def obtener_articulos_punto_reorden(self) -> list[Articulo]:
        """
        Retorna lista de artículos que alcanzaron el punto de reorden.

        Returns:
            Lista de artículos que requieren reorden
        """
        return list(self.repository.get_reorder_point())


# ==================== MOVIMIENTO SERVICE ====================

class MovimientoService:
    """
    Service para lógica de negocio de Movimiento.

    Coordina operaciones complejas de movimientos de inventario
    con actualización atómica de stock.
    """

    def __init__(self):
        self.movimiento_repo = MovimientoRepository()
        self.articulo_repo = ArticuloRepository()
        self.tipo_repo = TipoMovimientoRepository()

    @transaction.atomic
    def registrar_entrada(
        self,
        articulo: Articulo,
        tipo: TipoMovimiento,
        cantidad: Decimal,
        usuario: User,
        motivo: str
    ) -> Movimiento:
        """
        Registra una entrada de inventario (aumenta stock).

        Esta operación es atómica: todo o nada.

        Args:
            articulo: Artículo a mover
            tipo: Tipo de movimiento
            cantidad: Cantidad a ingresar
            usuario: Usuario que realiza la operación
            motivo: Motivo del movimiento

        Returns:
            Movimiento creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar cantidad
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')

        # Calcular nuevo stock
        stock_anterior = articulo.stock_actual
        stock_nuevo = stock_anterior + cantidad

        # Validar stock máximo si está definido
        if articulo.stock_maximo and stock_nuevo > articulo.stock_maximo:
            raise ValidationError(
                f'La cantidad excede el stock máximo permitido '
                f'({articulo.stock_maximo}). Stock actual: {stock_anterior}, '
                f'intentando agregar: {cantidad}.'
            )

        # Crear movimiento
        movimiento = self.movimiento_repo.create(
            articulo=articulo,
            tipo=tipo,
            cantidad=cantidad,
            operacion='ENTRADA',
            usuario=usuario,
            motivo=motivo,
            stock_antes=stock_anterior,
            stock_despues=stock_nuevo
        )

        # Actualizar stock del artículo
        self.articulo_repo.update_stock(articulo, stock_nuevo)

        return movimiento

    @transaction.atomic
    def registrar_salida(
        self,
        articulo: Articulo,
        tipo: TipoMovimiento,
        cantidad: Decimal,
        usuario: User,
        motivo: str
    ) -> Movimiento:
        """
        Registra una salida de inventario (disminuye stock).

        Esta operación es atómica: todo o nada.

        Args:
            articulo: Artículo a mover
            tipo: Tipo de movimiento
            cantidad: Cantidad a sacar
            usuario: Usuario que realiza la operación
            motivo: Motivo del movimiento

        Returns:
            Movimiento creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar cantidad
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')

        # Calcular nuevo stock
        stock_anterior = articulo.stock_actual
        stock_nuevo = stock_anterior - cantidad

        # Validar que no quede en negativo
        if stock_nuevo < 0:
            raise ValidationError(
                f'Stock insuficiente. Stock actual: {stock_anterior}, '
                f'intentando sacar: {cantidad}.'
            )

        # Crear movimiento
        movimiento = self.movimiento_repo.create(
            articulo=articulo,
            tipo=tipo,
            cantidad=cantidad,
            operacion='SALIDA',
            usuario=usuario,
            motivo=motivo,
            stock_antes=stock_anterior,
            stock_despues=stock_nuevo
        )

        # Actualizar stock del artículo
        self.articulo_repo.update_stock(articulo, stock_nuevo)

        return movimiento

    @transaction.atomic
    def registrar_movimiento(
        self,
        articulo: Articulo,
        tipo: TipoMovimiento,
        cantidad: Decimal,
        operacion: str,
        usuario: User,
        motivo: str
    ) -> Movimiento:
        """
        Registra un movimiento (entrada o salida) según la operación.

        Esta operación es atómica: todo o nada.

        Args:
            articulo: Artículo a mover
            tipo: Tipo de movimiento
            cantidad: Cantidad a mover
            operacion: 'ENTRADA' o 'SALIDA'
            usuario: Usuario que realiza la operación
            motivo: Motivo del movimiento

        Returns:
            Movimiento creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        if operacion == 'ENTRADA':
            return self.registrar_entrada(articulo, tipo, cantidad, usuario, motivo)
        elif operacion == 'SALIDA':
            return self.registrar_salida(articulo, tipo, cantidad, usuario, motivo)
        else:
            raise ValidationError(
                f'Operación inválida: "{operacion}". '
                f'Debe ser "ENTRADA" o "SALIDA".'
            )

    def obtener_historial_articulo(
        self,
        articulo: Articulo,
        limit: int = 20
    ) -> list[Movimiento]:
        """
        Obtiene el historial de movimientos de un artículo.

        Args:
            articulo: Artículo del cual obtener el historial
            limit: Número máximo de movimientos a retornar

        Returns:
            Lista de movimientos ordenados por fecha descendente
        """
        return list(self.movimiento_repo.filter_by_articulo(articulo, limit))
