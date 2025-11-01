"""
Formularios para el módulo de bodega.
Implementa validación centralizada siguiendo buenas prácticas Django.
"""
from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .models import Bodega, Categoria, Articulo, TipoMovimiento, Movimiento


class CategoriaForm(forms.ModelForm):
    """Formulario para crear y editar categorías de artículos."""

    class Meta:
        model = Categoria
        fields = ['codigo', 'nombre', 'descripcion', 'observaciones', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de categoría',
                'maxlength': '20'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la categoría',
                'rows': 3
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones adicionales',
                'rows': 2
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'observaciones': 'Observaciones',
            'activo': 'Activo'
        }

    def clean_codigo(self):
        """Validar que el código sea único (en mayúsculas)."""
        codigo = self.cleaned_data.get('codigo', '').strip().upper()

        # Si estamos editando, excluir la instancia actual
        queryset = Categoria.objects.filter(codigo=codigo)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(
                f'Ya existe una categoría con el código "{codigo}".'
            )

        return codigo

    def clean_nombre(self):
        """Limpiar y validar el nombre."""
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre es obligatorio.')
        return nombre
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo marcas y modelos activos
        from apps.inventario.models import Marca, Modelo
        self.fields['marca'].queryset = Marca.objects.filter(activo=True, eliminado=False)
        self.fields['modelo'].queryset = Modelo.objects.filter(activo=True, eliminado=False)
        self.fields['modelo'].required = False
        
        # Si hay instancia y tiene marca, filtrar modelos
        if self.instance and self.instance.pk and self.instance.marca:
            self.fields['modelo'].queryset = Modelo.objects.filter(
                marca=self.instance.marca,
                activo=True,
                eliminado=False
            )
        
        # Cargar sectores activos
        from apps.inventario.models import SectorInventario
        self.fields['sector'].queryset = SectorInventario.objects.filter(activo=True, eliminado=False)


class ArticuloForm(forms.ModelForm):
    """Formulario para crear y editar artículos de bodega."""

    class Meta:
        model = Articulo
        fields = [
            'sku', 'codigo', 'nombre_articulo', 'nombre', 'descripcion',
            'marca', 'modelo', 'codigo_barras', 'categoria', 'sector',
            'stock_actual', 'stock_minimo', 'stock_maximo', 'punto_reorden',
            'unidad_medida', 'ubicacion_fisica', 'observaciones', 'activo'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SKU único del artículo',
                'required': True
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código del artículo'
            }),
            'nombre_articulo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_nombre_articulo',
                'data-autocomplete': 'true'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del artículo',
                'required': True,
                'id': 'id_nombre'
            }),
            'marca': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_marca',
                'data-filter': 'modelo'
            }),
            'modelo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_modelo',
                'disabled': True
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dejar vacío para auto-generar desde SKU'
            }),
            'sector': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada',
                'rows': 3
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
                'step': '0.01',
                'min': '0'
            }),
            'punto_reorden': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
                'step': '0.01',
                'min': '0'
            }),
            'unidad_medida': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: UN, KG, LT',
                'required': True
            }),
            'ubicacion_fisica': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones adicionales',
                'rows': 2
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo categorías activas y no eliminadas
        self.fields['categoria'].queryset = Categoria.objects.filter(
            activo=True,
            eliminado=False
        ).order_by('codigo')

        # Filtrar solo bodegas activas y no eliminadas
        self.fields['ubicacion_fisica'].queryset = Bodega.objects.filter(
            activo=True,
            eliminado=False
        ).order_by('codigo')
        
        # Filtrar marcas y modelos activos
        from apps.inventario.models import Marca, Modelo, NombreArticulo, SectorInventario
        self.fields['marca'].queryset = Marca.objects.filter(activo=True, eliminado=False)
        self.fields['modelo'].queryset = Modelo.objects.filter(activo=True, eliminado=False)
        self.fields['modelo'].required = False
        
        # Si hay instancia y tiene marca, filtrar modelos
        if self.instance and self.instance.pk and self.instance.marca:
            self.fields['modelo'].queryset = Modelo.objects.filter(
                marca=self.instance.marca,
                activo=True,
                eliminado=False
            )
        
        # Cargar nombres de artículos y sectores activos
        self.fields['nombre_articulo'].queryset = NombreArticulo.objects.filter(activo=True, eliminado=False)
        self.fields['sector'].queryset = SectorInventario.objects.filter(activo=True, eliminado=False)

    def clean_sku(self):
        """Validar que el SKU sea único (en mayúsculas)."""
        sku = self.cleaned_data.get('sku', '').strip().upper()

        # Si estamos editando, excluir la instancia actual
        queryset = Articulo.objects.filter(sku=sku)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(
                f'Ya existe un artículo con el SKU "{sku}".'
            )

        return sku

    def clean(self):
        """Validaciones de múltiples campos."""
        cleaned_data = super().clean()
        stock_minimo = cleaned_data.get('stock_minimo')
        stock_maximo = cleaned_data.get('stock_maximo')
        punto_reorden = cleaned_data.get('punto_reorden')

        # Validar que stock máximo sea mayor que mínimo
        if stock_minimo and stock_maximo:
            if stock_maximo <= stock_minimo:
                raise ValidationError({
                    'stock_maximo': 'El stock máximo debe ser mayor que el stock mínimo.'
                })

        # Validar que punto de reorden esté entre mínimo y máximo
        if punto_reorden and stock_minimo:
            if punto_reorden < stock_minimo:
                raise ValidationError({
                    'punto_reorden': 'El punto de reorden debe ser mayor o igual al stock mínimo.'
                })

        return cleaned_data


class MovimientoForm(forms.ModelForm):
    """Formulario para registrar movimientos de inventario."""

    class Meta:
        model = Movimiento
        fields = ['articulo', 'tipo', 'cantidad', 'operacion', 'motivo']
        widgets = {
            'articulo': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_articulo'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'operacion': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa el motivo del movimiento',
                'rows': 3,
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo artículos activos y no eliminados
        self.fields['articulo'].queryset = Articulo.objects.filter(
            activo=True,
            eliminado=False
        ).select_related('categoria').order_by('sku')

        # Filtrar solo tipos de movimiento activos
        self.fields['tipo'].queryset = TipoMovimiento.objects.filter(
            activo=True,
            eliminado=False
        ).order_by('codigo')

    def clean_cantidad(self):
        """Validar que la cantidad sea positiva."""
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad and cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')
        return cantidad

    def clean(self):
        """Validar que haya suficiente stock para salidas."""
        cleaned_data = super().clean()
        articulo = cleaned_data.get('articulo')
        cantidad = cleaned_data.get('cantidad')
        operacion = cleaned_data.get('operacion')

        # Validar stock disponible para salidas
        if articulo and cantidad and operacion == 'SALIDA':
            if articulo.stock_actual < cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {articulo.stock_actual} {articulo.unidad_medida}'
                })

        return cleaned_data


class ArticuloFiltroForm(forms.Form):
    """Formulario para filtrar artículos."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por SKU, código, nombre o marca...'
        }),
        label='Búsqueda'
    )

    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activo=True, eliminado=False),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Categoría'
    )

    bodega = forms.ModelChoiceField(
        queryset=Bodega.objects.filter(activo=True, eliminado=False),
        required=False,
        empty_label='Todas las bodegas',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Bodega'
    )

    activo = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('1', 'Activos'),
            ('0', 'Inactivos')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Estado'
    )
