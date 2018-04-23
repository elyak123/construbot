from django import forms
from dal import autocomplete
from .models import Contrato, Cliente, Sitio, Concept, Destinatario

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


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'company': forms.HiddenInput()
        }


class SitioForm(forms.ModelForm):
    class Meta:
        model = Sitio
        fields = '__all__'
        widgets = {
            'company': forms.HiddenInput()
        }


class DestinatarioForm(forms.ModelForm):
    class Meta:
        model = Destinatario
        fields = '__all__'
        widgets = {
            'company': forms.HiddenInput(),
            'cliente': autocomplete.ModelSelect2(
                url='proyectos:cliente-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
        }

ContractConceptInlineForm = forms.inlineformset_factory(
    Contrato, Concept,
    fields=(
        'code',
        'concept_text',
        'unit',
        'total_cuantity',
        'unit_price',
    ),
    extra=1,
    widgets={
        'concept_text': forms.Textarea(attrs={
            'cols': '35',
            'rows': '3'
        }),
        'unit': autocomplete.ModelSelect2(
            url='proyectos:unit-autocomplete',
            attrs={'data-minimum-input-length': 3}
        ),
        'code': forms.TextInput(attrs={
            'class': 'inlineCode'
        }),
    },
)
