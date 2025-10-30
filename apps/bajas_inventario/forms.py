from django import forms
from django.forms import inlineformset_factory
from .models import BajaInventario, DetalleBaja, MotivoBaja, EstadoBaja, HistorialBaja
from apps.activos.models import Activo
from apps.bodega.models import Bodega


class BajaInventarioForm(forms.ModelForm):
    """Formulario para crear/editar Bajas de Inventario"""

    class Meta:
        model = BajaInventario
        fields = [
            'fecha_baja', 'motivo', 'bodega', 'descripcion',
            'observaciones', 'documento'
        ]
        widgets = {
            'fecha_baja': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'bodega': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa la razón de la baja...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
            'documento': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo motivos activos
        self.fields['motivo'].queryset = MotivoBaja.objects.filter(
            activo=True, eliminado=False
        )
        # Filtrar solo bodegas activas
        self.fields['bodega'].queryset = Bodega.objects.filter(
            activo=True, eliminado=False
        )


class DetalleBajaForm(forms.ModelForm):
    """Formulario para los detalles de la baja"""

    class Meta:
        model = DetalleBaja
        fields = [
            'activo', 'cantidad', 'valor_unitario',
            'lote', 'numero_serie', 'observaciones'
        ]
        widgets = {
            'activo': forms.Select(attrs={'class': 'form-select activo-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'valor_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'lote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lote (opcional)'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'N° de Serie (opcional)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo activos activos
        self.fields['activo'].queryset = Activo.objects.select_related(
            'categoria', 'unidad_medida'
        ).all()


# Formset para detalles de baja
DetalleBajaFormSet = inlineformset_factory(
    BajaInventario,
    DetalleBaja,
    form=DetalleBajaForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class AutorizarBajaForm(forms.Form):
    """Formulario para autorizar una baja de inventario"""
    notas_autorizacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas de autorización (opcional)...'
        }),
        label='Notas de Autorización'
    )


class RechazarBajaForm(forms.Form):
    """Formulario para rechazar una baja de inventario"""
    motivo_rechazo = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Indique el motivo del rechazo...'
        }),
        label='Motivo del Rechazo'
    )


class FiltroBajasForm(forms.Form):
    """Formulario para filtrar bajas de inventario"""
    estado = forms.ModelChoiceField(
        queryset=EstadoBaja.objects.filter(activo=True, eliminado=False),
        required=False,
        empty_label='Todos los estados',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    motivo = forms.ModelChoiceField(
        queryset=MotivoBaja.objects.filter(activo=True, eliminado=False),
        required=False,
        empty_label='Todos los motivos',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Hasta'
    )
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número, descripción...'
        }),
        label='Buscar'
    )
