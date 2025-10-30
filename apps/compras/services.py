"""
Service Layer para el módulo de compras.

Contiene la lógica de negocio siguiendo el principio de
Single Responsibility (SOLID). Las operaciones críticas
usan transacciones atómicas para garantizar consistencia.
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from core.utils import validar_rut, format_rut, generar_codigo_unico
from .models import (
    Proveedor, EstadoOrdenCompra, OrdenCompra,
    DetalleOrdenCompra, DetalleOrdenCompraArticulo,
    EstadoRecepcion, RecepcionArticulo, DetalleRecepcionArticulo,
    RecepcionActivo, DetalleRecepcionActivo
)
from .repositories import (
    ProveedorRepository, EstadoOrdenCompraRepository, OrdenCompraRepository,
    DetalleOrdenCompraRepository, DetalleOrdenCompraArticuloRepository,
    EstadoRecepcionRepository, RecepcionArticuloRepository,
    DetalleRecepcionArticuloRepository, RecepcionActivoRepository,
    DetalleRecepcionActivoRepository
)
from apps.bodega.models import Bodega, Articulo
from apps.bodega.repositories import ArticuloRepository, BodegaRepository
from apps.activos.models import Activo
from apps.activos.repositories import ActivoRepository


# ==================== PROVEEDOR SERVICE ====================

class ProveedorService:
    """Service para lógica de negocio de Proveedores."""

    def __init__(self):
        self.proveedor_repo = ProveedorRepository()

    @transaction.atomic
    def crear_proveedor(
        self,
        rut: str,
        razon_social: str,
        direccion: str,
        **kwargs: Any
    ) -> Proveedor:
        """
        Crea un nuevo proveedor con validaciones.

        Args:
            rut: RUT del proveedor
            razon_social: Razón social
            direccion: Dirección
            **kwargs: Campos opcionales

        Returns:
            Proveedor: Proveedor creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar RUT
        if not validar_rut(rut):
            raise ValidationError({'rut': 'RUT inválido'})

        # Verificar RUT único
        if self.proveedor_repo.exists_by_rut(rut):
            raise ValidationError({'rut': 'Ya existe un proveedor con este RUT'})

        # Formatear RUT
        rut_formateado = format_rut(rut)

        # Crear proveedor
        proveedor = Proveedor.objects.create(
            rut=rut_formateado,
            razon_social=razon_social.strip(),
            direccion=direccion.strip(),
            nombre_fantasia=kwargs.get('nombre_fantasia', ''),
            giro=kwargs.get('giro', ''),
            comuna=kwargs.get('comuna', ''),
            ciudad=kwargs.get('ciudad', ''),
            telefono=kwargs.get('telefono', ''),
            email=kwargs.get('email', ''),
            sitio_web=kwargs.get('sitio_web', ''),
            condicion_pago=kwargs.get('condicion_pago', 'Contado'),
            dias_credito=kwargs.get('dias_credito', 0),
            activo=True
        )

        return proveedor

    @transaction.atomic
    def actualizar_proveedor(
        self,
        proveedor: Proveedor,
        **campos: Any
    ) -> Proveedor:
        """
        Actualiza un proveedor existente.

        Args:
            proveedor: Proveedor a actualizar
            **campos: Campos a actualizar

        Returns:
            Proveedor: Proveedor actualizado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Si se actualiza el RUT, validar
        if 'rut' in campos:
            nuevo_rut = campos['rut']
            if not validar_rut(nuevo_rut):
                raise ValidationError({'rut': 'RUT inválido'})

            # Verificar que no exista otro con ese RUT
            if self.proveedor_repo.exists_by_rut(nuevo_rut, exclude_id=proveedor.id):
                raise ValidationError({'rut': 'Ya existe otro proveedor con este RUT'})

            campos['rut'] = format_rut(nuevo_rut)

        # Actualizar campos
        for campo, valor in campos.items():
            setattr(proveedor, campo, valor)

        proveedor.save()
        return proveedor

    @transaction.atomic
    def eliminar_proveedor(self, proveedor: Proveedor) -> None:
        """
        Elimina (soft delete) un proveedor.

        Args:
            proveedor: Proveedor a eliminar

        Raises:
            ValidationError: Si el proveedor tiene órdenes asociadas
        """
        # Verificar que no tenga órdenes de compra
        orden_repo = OrdenCompraRepository()
        ordenes = orden_repo.filter_by_proveedor(proveedor)

        if ordenes.exists():
            raise ValidationError(
                'No se puede eliminar el proveedor porque tiene órdenes de compra asociadas'
            )

        # Soft delete
        proveedor.eliminado = True
        proveedor.activo = False
        proveedor.save()


# ==================== ORDEN COMPRA SERVICE ====================

class OrdenCompraService:
    """Service para lógica de negocio de Órdenes de Compra."""

    def __init__(self):
        self.orden_repo = OrdenCompraRepository()
        self.estado_repo = EstadoOrdenCompraRepository()
        self.proveedor_repo = ProveedorRepository()
        self.bodega_repo = BodegaRepository()

    def calcular_totales(
        self,
        subtotal: Decimal,
        tasa_impuesto: Decimal = Decimal('0.19'),  # 19% IVA Chile
        descuento: Decimal = Decimal('0')
    ) -> Dict[str, Decimal]:
        """
        Calcula los totales de una orden de compra.

        Args:
            subtotal: Subtotal sin impuestos
            tasa_impuesto: Tasa de impuesto (default: 19%)
            descuento: Descuento aplicado

        Returns:
            Dict con 'subtotal', 'impuesto', 'descuento', 'total'
        """
        impuesto = (subtotal - descuento) * tasa_impuesto
        total = subtotal - descuento + impuesto

        return {
            'subtotal': subtotal,
            'impuesto': impuesto,
            'descuento': descuento,
            'total': total
        }

    @transaction.atomic
    def crear_orden_compra(
        self,
        proveedor: Proveedor,
        bodega_destino: Bodega,
        solicitante: User,
        fecha_orden: date,
        numero: Optional[str] = None,
        **kwargs: Any
    ) -> OrdenCompra:
        """
        Crea una nueva orden de compra.

        Args:
            proveedor: Proveedor
            bodega_destino: Bodega de destino
            solicitante: Usuario solicitante
            fecha_orden: Fecha de la orden
            numero: Número de orden (opcional, se genera automático)
            **kwargs: Campos opcionales

        Returns:
            OrdenCompra: Orden creada

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar proveedor activo
        if not proveedor.activo:
            raise ValidationError({'proveedor': 'El proveedor no está activo'})

        # Generar número si no se proporciona
        if not numero:
            numero = generar_codigo_unico('OC', OrdenCompra, 'numero', longitud=8)
        else:
            # Verificar que el número no exista
            if self.orden_repo.exists_by_numero(numero):
                raise ValidationError({'numero': 'Ya existe una orden con este número'})

        # Obtener estado inicial
        estado_inicial = self.estado_repo.get_inicial()
        if not estado_inicial:
            raise ValidationError('No se ha configurado un estado inicial para órdenes de compra')

        # Crear orden
        orden = OrdenCompra.objects.create(
            numero=numero,
            fecha_orden=fecha_orden,
            proveedor=proveedor,
            bodega_destino=bodega_destino,
            estado=estado_inicial,
            solicitante=solicitante,
            aprobador=kwargs.get('aprobador'),
            fecha_entrega_esperada=kwargs.get('fecha_entrega_esperada'),
            subtotal=Decimal('0'),
            impuesto=Decimal('0'),
            descuento=kwargs.get('descuento', Decimal('0')),
            total=Decimal('0'),
            observaciones=kwargs.get('observaciones', ''),
            notas_internas=kwargs.get('notas_internas', '')
        )

        return orden

    @transaction.atomic
    def cambiar_estado(
        self,
        orden: OrdenCompra,
        nuevo_estado: EstadoOrdenCompra,
        usuario: User
    ) -> OrdenCompra:
        """
        Cambia el estado de una orden de compra.

        Args:
            orden: Orden a actualizar
            nuevo_estado: Nuevo estado
            usuario: Usuario que realiza el cambio

        Returns:
            OrdenCompra: Orden actualizada

        Raises:
            ValidationError: Si el cambio no es válido
        """
        # Validar que el estado actual permita edición
        if orden.estado.es_final:
            raise ValidationError('No se puede cambiar el estado de una orden finalizada')

        # Actualizar estado
        orden.estado = nuevo_estado
        orden.save()

        return orden

    @transaction.atomic
    def recalcular_totales(self, orden: OrdenCompra) -> OrdenCompra:
        """
        Recalcula los totales de una orden basándose en sus detalles.

        Args:
            orden: Orden de compra

        Returns:
            OrdenCompra: Orden actualizada
        """
        # Sumar subtotales de detalles de activos
        detalle_repo = DetalleOrdenCompraRepository()
        detalles_activos = detalle_repo.filter_by_orden(orden)
        subtotal_activos = sum(d.subtotal for d in detalles_activos)

        # Sumar subtotales de detalles de artículos
        detalle_articulo_repo = DetalleOrdenCompraArticuloRepository()
        detalles_articulos = detalle_articulo_repo.filter_by_orden(orden)
        subtotal_articulos = sum(d.subtotal for d in detalles_articulos)

        # Subtotal total
        subtotal_total = subtotal_activos + subtotal_articulos

        # Calcular totales
        totales = self.calcular_totales(subtotal_total, descuento=orden.descuento)

        # Actualizar orden
        orden.subtotal = totales['subtotal']
        orden.impuesto = totales['impuesto']
        orden.total = totales['total']
        orden.save()

        return orden


# ==================== RECEPCIÓN ARTÍCULO SERVICE ====================

class RecepcionArticuloService:
    """Service para lógica de negocio de Recepciones de Artículos."""

    def __init__(self):
        self.recepcion_repo = RecepcionArticuloRepository()
        self.detalle_repo = DetalleRecepcionArticuloRepository()
        self.estado_repo = EstadoRecepcionRepository()
        self.articulo_repo = ArticuloRepository()

    @transaction.atomic
    def crear_recepcion(
        self,
        bodega: Bodega,
        recibido_por: User,
        orden_compra: Optional[OrdenCompra] = None,
        numero: Optional[str] = None,
        **kwargs: Any
    ) -> RecepcionArticulo:
        """
        Crea una nueva recepción de artículos.

        Args:
            bodega: Bodega de recepción
            recibido_por: Usuario que recibe
            orden_compra: Orden de compra asociada (opcional)
            numero: Número de recepción (opcional, se genera automático)
            **kwargs: Campos opcionales

        Returns:
            RecepcionArticulo: Recepción creada

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Generar número si no se proporciona
        if not numero:
            numero = generar_codigo_unico('RART', RecepcionArticulo, 'numero', longitud=8)
        else:
            if self.recepcion_repo.exists_by_numero(numero):
                raise ValidationError({'numero': 'Ya existe una recepción con este número'})

        # Obtener estado inicial
        estado_inicial = self.estado_repo.get_inicial()
        if not estado_inicial:
            raise ValidationError('No se ha configurado un estado inicial para recepciones')

        # Crear recepción
        recepcion = RecepcionArticulo.objects.create(
            numero=numero,
            orden_compra=orden_compra,
            bodega=bodega,
            estado=estado_inicial,
            recibido_por=recibido_por,
            documento_referencia=kwargs.get('documento_referencia', ''),
            observaciones=kwargs.get('observaciones', '')
        )

        return recepcion

    @transaction.atomic
    def agregar_detalle(
        self,
        recepcion: RecepcionArticulo,
        articulo: Articulo,
        cantidad: Decimal,
        actualizar_stock: bool = True,
        **kwargs: Any
    ) -> DetalleRecepcionArticulo:
        """
        Agrega un detalle a la recepción y actualiza el stock.

        Esta operación es atómica: se crea el detalle y se actualiza
        el stock del artículo en una sola transacción.

        Args:
            recepcion: Recepción
            articulo: Artículo recibido
            cantidad: Cantidad recibida
            actualizar_stock: Si debe actualizar el stock (default: True)
            **kwargs: Campos opcionales (lote, fecha_vencimiento, observaciones)

        Returns:
            DetalleRecepcionArticulo: Detalle creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar cantidad
        if cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a cero'})

        # Validar que la recepción no esté finalizada
        if recepcion.estado.es_final:
            raise ValidationError('No se pueden agregar detalles a una recepción finalizada')

        # Crear detalle
        detalle = DetalleRecepcionArticulo.objects.create(
            recepcion=recepcion,
            articulo=articulo,
            cantidad=cantidad,
            lote=kwargs.get('lote', ''),
            fecha_vencimiento=kwargs.get('fecha_vencimiento'),
            observaciones=kwargs.get('observaciones', '')
        )

        # Actualizar stock del artículo si corresponde
        if actualizar_stock:
            stock_nuevo = articulo.stock_actual + cantidad

            # Validar stock máximo
            if articulo.stock_maximo and stock_nuevo > articulo.stock_maximo:
                raise ValidationError(
                    f'La cantidad recibida excede el stock máximo del artículo '
                    f'({articulo.stock_maximo})'
                )

            articulo.stock_actual = stock_nuevo
            articulo.save()

        # Si hay orden de compra, actualizar cantidad recibida
        if recepcion.orden_compra:
            self._actualizar_cantidad_recibida_orden(recepcion.orden_compra, articulo, cantidad)

        return detalle

    def _actualizar_cantidad_recibida_orden(
        self,
        orden: OrdenCompra,
        articulo: Articulo,
        cantidad_adicional: Decimal
    ) -> None:
        """
        Actualiza la cantidad recibida en el detalle de la orden de compra.

        Args:
            orden: Orden de compra
            articulo: Artículo
            cantidad_adicional: Cantidad adicional recibida
        """
        from apps.compras.repositories import DetalleOrdenCompraArticuloRepository

        detalle_orden_repo = DetalleOrdenCompraArticuloRepository()
        detalles = detalle_orden_repo.filter_by_orden(orden)

        # Buscar el detalle del artículo
        for detalle in detalles:
            if detalle.articulo.id == articulo.id:
                detalle.cantidad_recibida += cantidad_adicional
                detalle.save()
                break


# ==================== RECEPCIÓN ACTIVO SERVICE ====================

class RecepcionActivoService:
    """Service para lógica de negocio de Recepciones de Activos."""

    def __init__(self):
        self.recepcion_repo = RecepcionActivoRepository()
        self.detalle_repo = DetalleRecepcionActivoRepository()
        self.estado_repo = EstadoRecepcionRepository()
        self.activo_repo = ActivoRepository()

    @transaction.atomic
    def crear_recepcion(
        self,
        recibido_por: User,
        orden_compra: Optional[OrdenCompra] = None,
        numero: Optional[str] = None,
        **kwargs: Any
    ) -> RecepcionActivo:
        """
        Crea una nueva recepción de activos.

        Args:
            recibido_por: Usuario que recibe
            orden_compra: Orden de compra asociada (opcional)
            numero: Número de recepción (opcional, se genera automático)
            **kwargs: Campos opcionales

        Returns:
            RecepcionActivo: Recepción creada

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Generar número si no se proporciona
        if not numero:
            numero = generar_codigo_unico('RACT', RecepcionActivo, 'numero', longitud=8)
        else:
            if self.recepcion_repo.exists_by_numero(numero):
                raise ValidationError({'numero': 'Ya existe una recepción con este número'})

        # Obtener estado inicial
        estado_inicial = self.estado_repo.get_inicial()
        if not estado_inicial:
            raise ValidationError('No se ha configurado un estado inicial para recepciones')

        # Crear recepción
        recepcion = RecepcionActivo.objects.create(
            numero=numero,
            orden_compra=orden_compra,
            estado=estado_inicial,
            recibido_por=recibido_por,
            documento_referencia=kwargs.get('documento_referencia', ''),
            observaciones=kwargs.get('observaciones', '')
        )

        return recepcion

    @transaction.atomic
    def agregar_detalle(
        self,
        recepcion: RecepcionActivo,
        activo: Activo,
        cantidad: Decimal,
        **kwargs: Any
    ) -> DetalleRecepcionActivo:
        """
        Agrega un detalle a la recepción de activos.

        Args:
            recepcion: Recepción
            activo: Activo recibido
            cantidad: Cantidad recibida
            **kwargs: Campos opcionales (numero_serie, observaciones)

        Returns:
            DetalleRecepcionActivo: Detalle creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        # Validar cantidad
        if cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a cero'})

        # Validar que la recepción no esté finalizada
        if recepcion.estado.es_final:
            raise ValidationError('No se pueden agregar detalles a una recepción finalizada')

        # Validar número de serie si el activo lo requiere
        numero_serie = kwargs.get('numero_serie')
        if activo.requiere_serie and not numero_serie:
            raise ValidationError(
                {'numero_serie': 'Este activo requiere número de serie'}
            )

        # Crear detalle
        detalle = DetalleRecepcionActivo.objects.create(
            recepcion=recepcion,
            activo=activo,
            cantidad=cantidad,
            numero_serie=numero_serie or '',
            observaciones=kwargs.get('observaciones', '')
        )

        # Si hay orden de compra, actualizar cantidad recibida
        if recepcion.orden_compra:
            self._actualizar_cantidad_recibida_orden(recepcion.orden_compra, activo, cantidad)

        return detalle

    def _actualizar_cantidad_recibida_orden(
        self,
        orden: OrdenCompra,
        activo: Activo,
        cantidad_adicional: Decimal
    ) -> None:
        """
        Actualiza la cantidad recibida en el detalle de la orden de compra.

        Args:
            orden: Orden de compra
            activo: Activo
            cantidad_adicional: Cantidad adicional recibida
        """
        from apps.compras.repositories import DetalleOrdenCompraRepository

        detalle_orden_repo = DetalleOrdenCompraRepository()
        detalles = detalle_orden_repo.filter_by_orden(orden)

        # Buscar el detalle del activo
        for detalle in detalles:
            if detalle.activo.id == activo.id:
                detalle.cantidad_recibida += cantidad_adicional
                detalle.save()
                break
