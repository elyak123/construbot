from django import forms
from .models import Contrato

MY_DATE_FORMATS = ['%Y-%m-%d']

class ContratoForm(forms.ModelForm):
    currently_at = forms.CharField(
        widget= forms.HiddenInput(
        )
    )

    class Meta:
        model = Contrato
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(
                    attrs={'class': 'datepicker', 'name': 'fecha'},
                    format=MY_DATE_FORMATS
                ),
        }
