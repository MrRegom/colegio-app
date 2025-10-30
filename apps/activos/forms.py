from django import forms
from django.contrib.auth.models import User
from .models import (
    Activo, CategoriaActivo, UnidadMedida, EstadoActivo,
    Ubicacion, TipoMovimientoActivo, MovimientoActivo, UbicacionActual
)


class CategoriaActivoForm(forms.ModelForm):
    """Formulario para crear y editar categorías de activos"""

    class Meta:
        model = CategoriaActivo
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
        widgets = {
            'codigo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: COMP'}
            ),
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Computadoras'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la categoría...'}
            ),
            'activo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class UnidadMedidaForm(forms.ModelForm):
    """Formulario para crear y editar unidades de medida"""

    class Meta:
        model = UnidadMedida
        fields = ['codigo', 'nombre', 'simbolo', 'activo']
        widgets = {
            'codigo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: UND'}
            ),
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Unidad'}
            ),
            'simbolo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: un'}
            ),
            'activo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class EstadoActivoForm(forms.ModelForm):
    """Formulario para crear y editar estados de activos"""

    class Meta:
        model = EstadoActivo
        fields = ['codigo', 'nombre', 'descripcion', 'color', 'es_inicial', 'permite_movimiento', 'activo']
        widgets = {
            'codigo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: ACTIVO'}
            ),
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Activo'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'color': forms.TextInput(
                attrs={'class': 'form-control', 'type': 'color'}
            ),
            'es_inicial': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'permite_movimiento': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'activo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class ActivoForm(forms.ModelForm):
    """Formulario para crear y editar activos (bienes que no manejan stock)"""

    class Meta:
        model = Activo
        fields = [
            'codigo', 'nombre', 'descripcion',
            'categoria', 'estado',
            'marca', 'modelo', 'numero_serie', 'codigo_barras',
            'precio_unitario', 'costo_promedio',
            'requiere_serie', 'requiere_lote', 'requiere_vencimiento',
            'activo'
        ]
        widgets = {
            'codigo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Código único del activo'}
            ),
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre del activo'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada...'}
            ),
            'categoria': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'estado': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'marca': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Marca del producto'}
            ),
            'modelo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Modelo'}
            ),
            'numero_serie': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Número de serie'}
            ),
            'codigo_barras': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Código de barras'}
            ),
            'precio_unitario': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}
            ),
            'costo_promedio': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}
            ),
            'requiere_serie': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'requiere_lote': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'requiere_vencimiento': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'activo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo registros activos para los selectores
        self.fields['categoria'].queryset = CategoriaActivo.objects.filter(activo=True, eliminado=False)
        self.fields['estado'].queryset = EstadoActivo.objects.filter(activo=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Asignar siempre la unidad de medida "UNIDAD"
        try:
            unidad_unidad = UnidadMedida.objects.get(codigo='UNIDAD')
            instance.unidad_medida = unidad_unidad
        except UnidadMedida.DoesNotExist:
            # Si no existe, crear la unidad "UNIDAD"
            unidad_unidad = UnidadMedida.objects.create(
                codigo='UNIDAD',
                nombre='Unidad',
                simbolo='un',
                activo=True,
                eliminado=False
            )
            instance.unidad_medida = unidad_unidad

        # Establecer valores por defecto para stock (no se usan pero son requeridos en el modelo)
        instance.stock_minimo = 0
        instance.stock_maximo = None
        instance.punto_reorden = None

        if commit:
            instance.save()
        return instance


class UbicacionForm(forms.ModelForm):
    """Formulario para crear y editar ubicaciones"""

    class Meta:
        model = Ubicacion
        fields = ['codigo', 'nombre', 'descripcion', 'edificio', 'piso', 'area', 'activo']
        widgets = {
            'codigo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: UB001'}
            ),
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Oficina Principal'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la ubicación...'}
            ),
            'edificio': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Edificio A'}
            ),
            'piso': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Piso 2'}
            ),
            'area': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Recursos Humanos'}
            ),
            'activo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class TipoMovimientoActivoForm(forms.ModelForm):
    """Formulario para crear y editar tipos de movimiento"""

    class Meta:
        model = TipoMovimientoActivo
        fields = ['codigo', 'nombre', 'descripcion', 'requiere_ubicacion', 'requiere_responsable', 'activo']
        widgets = {
            'codigo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: ASIG'}
            ),
            'nombre': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Asignación'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'requiere_ubicacion': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'requiere_responsable': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'activo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class MovimientoActivoForm(forms.ModelForm):
    """
    Formulario para registrar movimientos de activos individuales.
    Los campos lote y fecha_vencimiento son dinámicos según configuración del activo.
    """

    class Meta:
        model = MovimientoActivo
        fields = [
            'activo', 'tipo_movimiento', 'ubicacion_destino', 'responsable',
            'numero_serie', 'lote', 'fecha_vencimiento', 'observaciones'
        ]
        widgets = {
            'activo': forms.Select(
                attrs={'class': 'form-select', 'id': 'id_activo'}
            ),
            'tipo_movimiento': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'ubicacion_destino': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'responsable': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'numero_serie': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Número de serie único'}
            ),
            'lote': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Número de lote'}
            ),
            'fecha_vencimiento': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'observaciones': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar solo registros activos
        self.fields['activo'].queryset = Activo.objects.filter(activo=True).select_related(
            'categoria', 'estado'
        )
        self.fields['tipo_movimiento'].queryset = TipoMovimientoActivo.objects.filter(activo=True)
        self.fields['ubicacion_destino'].queryset = Ubicacion.objects.filter(activo=True, eliminado=False)
        self.fields['responsable'].queryset = User.objects.filter(is_active=True).order_by('username')

        # Hacer que todos los campos opcionales sean realmente opcionales al inicio
        self.fields['ubicacion_destino'].required = False
        self.fields['responsable'].required = False
        self.fields['numero_serie'].required = False
        self.fields['lote'].required = False
        self.fields['fecha_vencimiento'].required = False

        # Si hay una instancia, configurar campos según el activo
        if self.instance and self.instance.pk and self.instance.activo:
            self._configurar_campos_por_activo(self.instance.activo)

    def _configurar_campos_por_activo(self, activo):
        """Configura la visibilidad y requerimiento de campos según el activo"""
        # Número de serie
        if activo.requiere_serie:
            self.fields['numero_serie'].required = True
            self.fields['numero_serie'].widget.attrs['required'] = 'required'

        # Lote
        if activo.requiere_lote:
            self.fields['lote'].required = True
            self.fields['lote'].widget.attrs['required'] = 'required'

        # Fecha de vencimiento
        if activo.requiere_vencimiento:
            self.fields['fecha_vencimiento'].required = True
            self.fields['fecha_vencimiento'].widget.attrs['required'] = 'required'

    def clean(self):
        cleaned_data = super().clean()
        activo = cleaned_data.get('activo')
        tipo_movimiento = cleaned_data.get('tipo_movimiento')

        if not activo:
            return cleaned_data

        # Validar campos según configuración del activo
        if activo.requiere_serie and not cleaned_data.get('numero_serie'):
            self.add_error('numero_serie', 'Este activo requiere número de serie')

        if activo.requiere_lote and not cleaned_data.get('lote'):
            self.add_error('lote', 'Este activo requiere lote')

        if activo.requiere_vencimiento and not cleaned_data.get('fecha_vencimiento'):
            self.add_error('fecha_vencimiento', 'Este activo requiere fecha de vencimiento')

        # Validar campos según tipo de movimiento
        if tipo_movimiento:
            if tipo_movimiento.requiere_ubicacion and not cleaned_data.get('ubicacion_destino'):
                self.add_error('ubicacion_destino', 'Este tipo de movimiento requiere ubicación destino')

            if tipo_movimiento.requiere_responsable and not cleaned_data.get('responsable'):
                self.add_error('responsable', 'Este tipo de movimiento requiere responsable')

        return cleaned_data


class FiltroActivosForm(forms.Form):
    """Formulario para filtrar activos en la lista"""

    categoria = forms.ModelChoiceField(
        queryset=CategoriaActivo.objects.filter(activo=True, eliminado=False),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estado = forms.ModelChoiceField(
        queryset=EstadoActivo.objects.filter(activo=True),
        required=False,
        empty_label='Todos los estados',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    buscar = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Buscar por código, nombre, marca...'
            }
        )
    )


class AjusteInventarioForm(forms.Form):
    """Formulario para ajustar inventario"""

    cantidad_ajuste = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.01'}
        ),
        label='Cantidad de Ajuste',
        help_text='Valores positivos aumentan, negativos disminuyen'
    )

    motivo = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivo del ajuste...'}
        ),
        label='Motivo del Ajuste',
        required=True
    )
