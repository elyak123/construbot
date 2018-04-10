from django import forms
from dal import autocomplete
from .models import Contrato

MY_DATE_FORMATS = ['%Y-%m-%d']


class ContratoForm(forms.ModelForm):
    currently_at = forms.CharField(
        widget=forms.HiddenInput(
        )
    )

    class Meta:
        model = Contrato
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(
                attrs={
                    'class': 'datetimepicker-input',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#id_fecha',
                    'name': 'fecha'
                },
                format=MY_DATE_FORMATS
            ),
            'folio': forms.TextInput(
                attrs={'readonly': 'readonly'}
                ),
            'cliente': autocomplete.ModelSelect2(
                url='proyectos:cliente-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
            'sitio': autocomplete.ModelSelect2(
                url='proyectos:sitio-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
        }
