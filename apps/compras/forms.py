"""
Formularios para el módulo de compras.

Implementa validaciones personalizadas y limpieza de datos siguiendo
las mejores prácticas de Django 5.2.
"""
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    Proveedor, OrdenCompra, DetalleOrdenCompraArticulo, DetalleOrdenCompra,
    EstadoOrdenCompra, RecepcionArticulo, DetalleRecepcionArticulo,
    RecepcionActivo, DetalleRecepcionActivo, EstadoRecepcion
)
from apps.bodega.models import Bodega, Articulo
from apps.activos.models import Activo


# ==================== FORMULARIOS DE PROVEEDOR ====================

class ProveedorForm(forms.ModelForm):
    """Formulario para crear/editar proveedores."""

    class Meta:
        model = Proveedor
        fields = [
            'rut', 'razon_social', 'nombre_fantasia', 'giro',
            'direccion', 'comuna', 'ciudad', 'telefono', 'email', 'sitio_web',
            'condicion_pago', 'dias_credito', 'activo'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'giro': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'condicion_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'dias_credito': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_rut(self):
        """Validar formato y unicidad del RUT."""
        rut = self.cleaned_data.get('rut', '').strip().upper()

        # Validar unicidad
        queryset = Proveedor.objects.filter(rut=rut)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(f'Ya existe un proveedor con el RUT "{rut}".')

        return rut


# ==================== FORMULARIOS DE ORDEN DE COMPRA ====================

class OrdenCompraForm(forms.ModelForm):
    """Formulario para crear/editar órdenes de compra."""

    class Meta:
        model = OrdenCompra
        fields = [
            'numero', 'fecha_orden', 'fecha_entrega_esperada',
            'proveedor', 'bodega_destino', 'estado', 'observaciones'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OC-00001'}),
            'fecha_orden': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_entrega_esperada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'bodega_destino': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(
            activo=True, eliminado=False
        ).order_by('razon_social')

        # Filtrar bodegas activas
        self.fields['bodega_destino'].queryset = Bodega.objects.filter(
            activo=True, eliminado=False
        ).order_by('nombre')

        # Filtrar estados activos
        self.fields['estado'].queryset = EstadoOrdenCompra.objects.filter(
            activo=True
        ).order_by('codigo')

        # Establecer estado inicial por defecto
        if not self.instance.pk:
            estado_inicial = EstadoOrdenCompra.objects.filter(
                es_inicial=True, activo=True
            ).first()
            if estado_inicial:
                self.fields['estado'].initial = estado_inicial

    def clean_numero(self):
        """Validar que el número de orden sea único."""
        numero = self.cleaned_data.get('numero', '').strip().upper()

        queryset = OrdenCompra.objects.filter(numero=numero)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(f'Ya existe una orden de compra con el número "{numero}".')

        return numero

    def clean(self):
        """Validar fechas."""
        cleaned_data = super().clean()
        fecha_orden = cleaned_data.get('fecha_orden')
        fecha_entrega_esperada = cleaned_data.get('fecha_entrega_esperada')

        if fecha_orden and fecha_entrega_esperada:
            if fecha_entrega_esperada < fecha_orden:
                raise ValidationError({
                    'fecha_entrega_esperada': 'La fecha de entrega esperada no puede ser anterior a la fecha de orden.'
                })

        return cleaned_data


class DetalleOrdenCompraArticuloForm(forms.ModelForm):
    """Formulario para agregar artículos a una orden de compra."""

    class Meta:
        model = DetalleOrdenCompraArticulo
        fields = ['articulo', 'cantidad', 'precio_unitario', 'descuento', 'observaciones']
        widgets = {
            'articulo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['articulo'].queryset = Articulo.objects.filter(
            activo=True, eliminado=False
        ).select_related('categoria').order_by('sku')

    def clean(self):
        """Validar que el descuento no sea mayor que el subtotal."""
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        precio_unitario = cleaned_data.get('precio_unitario')
        descuento = cleaned_data.get('descuento', Decimal('0'))

        if cantidad and precio_unitario:
            subtotal_sin_descuento = cantidad * precio_unitario
            if descuento > subtotal_sin_descuento:
                raise ValidationError({
                    'descuento': f'El descuento no puede ser mayor que el subtotal (${subtotal_sin_descuento:,.2f}).'
                })

        return cleaned_data


class DetalleOrdenCompraActivoForm(forms.ModelForm):
    """Formulario para agregar activos a una orden de compra."""

    class Meta:
        model = DetalleOrdenCompra
        fields = ['activo', 'cantidad', 'precio_unitario', 'descuento', 'observaciones']
        widgets = {
            'activo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activo'].queryset = Activo.objects.filter(
            activo=True, eliminado=False
        ).select_related('categoria').order_by('codigo')

    def clean(self):
        """Validar que el descuento no sea mayor que el subtotal."""
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        precio_unitario = cleaned_data.get('precio_unitario')
        descuento = cleaned_data.get('descuento', Decimal('0'))

        if cantidad and precio_unitario:
            subtotal_sin_descuento = cantidad * precio_unitario
            if descuento > subtotal_sin_descuento:
                raise ValidationError({
                    'descuento': f'El descuento no puede ser mayor que el subtotal (${subtotal_sin_descuento:,.2f}).'
                })

        return cleaned_data


class OrdenCompraFiltroForm(forms.Form):
    """Formulario para filtrar órdenes de compra."""

    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número...'
        })
    )

    estado = forms.ModelChoiceField(
        required=False,
        label='Estado',
        queryset=EstadoOrdenCompra.objects.filter(activo=True).order_by('nombre'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    proveedor = forms.ModelChoiceField(
        required=False,
        label='Proveedor',
        queryset=Proveedor.objects.filter(activo=True, eliminado=False).order_by('razon_social'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )


# ==================== FORMULARIOS DE RECEPCIÓN DE ARTÍCULOS ====================

class RecepcionArticuloForm(forms.ModelForm):
    """Formulario para crear/editar recepciones de artículos."""

    class Meta:
        model = RecepcionArticulo
        fields = ['numero', 'orden_compra', 'bodega', 'documento_referencia', 'observaciones']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'REC-ART-00001'}),
            'orden_compra': forms.Select(attrs={'class': 'form-select'}),
            'bodega': forms.Select(attrs={'class': 'form-select'}),
            'documento_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guía/Factura'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar órdenes no finalizadas
        self.fields['orden_compra'].queryset = OrdenCompra.objects.filter(
            estado__es_final=False
        ).select_related('proveedor').order_by('-numero')
        self.fields['orden_compra'].required = False

        # Filtrar bodegas activas
        self.fields['bodega'].queryset = Bodega.objects.filter(
            activo=True, eliminado=False
        ).order_by('nombre')

    def clean_numero(self):
        """Validar que el número de recepción sea único."""
        numero = self.cleaned_data.get('numero', '').strip().upper()

        queryset = RecepcionArticulo.objects.filter(numero=numero)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(f'Ya existe una recepción con el número "{numero}".')

        return numero


class DetalleRecepcionArticuloForm(forms.ModelForm):
    """Formulario para agregar artículos a una recepción."""

    class Meta:
        model = DetalleRecepcionArticulo
        fields = ['articulo', 'cantidad', 'lote', 'fecha_vencimiento', 'observaciones']
        widgets = {
            'articulo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['articulo'].queryset = Articulo.objects.filter(
            activo=True, eliminado=False
        ).select_related('categoria').order_by('sku')
        self.fields['lote'].required = False
        self.fields['fecha_vencimiento'].required = False


class RecepcionArticuloFiltroForm(forms.Form):
    """Formulario para filtrar recepciones de artículos."""

    estado = forms.ModelChoiceField(
        required=False,
        label='Estado',
        queryset=EstadoRecepcion.objects.filter(activo=True, eliminado=False).order_by('nombre'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    bodega = forms.ModelChoiceField(
        required=False,
        label='Bodega',
        queryset=Bodega.objects.filter(activo=True, eliminado=False).order_by('nombre'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )


# ==================== FORMULARIOS DE RECEPCIÓN DE ACTIVOS ====================

class RecepcionActivoForm(forms.ModelForm):
    """Formulario para crear/editar recepciones de activos."""

    class Meta:
        model = RecepcionActivo
        fields = ['numero', 'orden_compra', 'documento_referencia', 'observaciones']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'REC-ACT-00001'}),
            'orden_compra': forms.Select(attrs={'class': 'form-select'}),
            'documento_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guía/Factura'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar órdenes no finalizadas
        self.fields['orden_compra'].queryset = OrdenCompra.objects.filter(
            estado__es_final=False
        ).select_related('proveedor').order_by('-numero')
        self.fields['orden_compra'].required = False

    def clean_numero(self):
        """Validar que el número de recepción sea único."""
        numero = self.cleaned_data.get('numero', '').strip().upper()

        queryset = RecepcionActivo.objects.filter(numero=numero)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(f'Ya existe una recepción con el número "{numero}".')

        return numero


class DetalleRecepcionActivoForm(forms.ModelForm):
    """Formulario para agregar activos a una recepción."""

    class Meta:
        model = DetalleRecepcionActivo
        fields = ['activo', 'cantidad', 'numero_serie', 'observaciones']
        widgets = {
            'activo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activo'].queryset = Activo.objects.filter(
            activo=True, eliminado=False
        ).select_related('categoria').order_by('codigo')
        self.fields['numero_serie'].required = False


class RecepcionActivoFiltroForm(forms.Form):
    """Formulario para filtrar recepciones de activos."""

    estado = forms.ModelChoiceField(
        required=False,
        label='Estado',
        queryset=EstadoRecepcion.objects.filter(activo=True, eliminado=False).order_by('nombre'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
