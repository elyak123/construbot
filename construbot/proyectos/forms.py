from django import forms
from .models import Contrato


class ContratoForm(forms.ModelForm):
    currently_at = forms.CharField(
        widget= forms.HiddenInput(
        )
    )

    class Meta:
        model = Contrato
        fields = '__all__'
