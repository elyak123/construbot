from django import forms
from dal import autocomplete
from .models import Contrato, Cliente, Sitio, Concept, Destinatario, Estimate, EstimateConcept, ImageEstimateConcept
from django.core.exceptions import ObjectDoesNotExist

MY_DATE_FORMATS = ['%Y-%m-%d']


class ContratoForm(forms.ModelForm):
    currently_at = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        result = super(ContratoForm, self).clean()
        if self.cleaned_data.get('currently_at') is None:
            raise forms.ValidationError('Error en la formación del formulario, es posible que este corrupto,'
                                        'porfavor recarga y vuelve a intentarlo')
        if self.cleaned_data.get('currently_at') == self.request.user.currently_at.company_name:
            return result
        else:
            raise forms.ValidationError(
                'Actualmente te encuentras en otra compañia, '
                'es necesario recargar y repetir el proceso.'
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
                attrs={'data-minimum-input-length': 3},
                forward=['cliente']
            ),
            'users': autocomplete.ModelSelect2Multiple(
                url='proyectos:user-autocomplete',
                attrs={
                    'data-minimum-input-length': 3,
                }
            ),
        }


class BaseCleanForm(forms.ModelForm):

    def clean(self):
        result = super(BaseCleanForm, self).clean()
        if self.cleaned_data.get('company') is None:
            raise forms.ValidationError('Error en la formación del formulario, es posible que este corrupto,'
                                        'porfavor recarga y vuelve a intentarlo')
        if self.cleaned_data['company'].company_name == self.request.user.currently_at.company_name:
            return result
        else:
            raise forms.ValidationError(
                'Actualmente te encuentras en otra compañia, '
                'es necesario recargar y repetir el proceso.'
            )


class ClienteForm(BaseCleanForm):

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
            'cliente': autocomplete.ModelSelect2(
                url='proyectos:cliente-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
        }


class DestinatarioForm(forms.ModelForm):

    class Meta:
        model = Destinatario
        fields = '__all__'
        widgets = {
            'cliente': autocomplete.ModelSelect2(
                url='proyectos:cliente-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
        }


class EstimateForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(EstimateForm, self).clean()
        destinatarios_contratos_error_message = 'Destinatarios y contratos no pueden ser de empresas diferentes'
        for auth_by in cleaned_data['auth_by']:
            if auth_by.cliente.company != cleaned_data['project'].cliente.company:
                raise forms.ValidationError(destinatarios_contratos_error_message)
        for auth_by_gen in cleaned_data['auth_by_gen']:
            if auth_by_gen.cliente.company != cleaned_data['project'].cliente.company:
                raise forms.ValidationError(destinatarios_contratos_error_message)
        pago_sin_fecha_validation_error_message = 'Si la estimación fué pagada, es necesaria fecha de pago.'
        if self.cleaned_data['paid'] and not self.cleaned_data['payment_date']:
            self.add_error('payment_date', pago_sin_fecha_validation_error_message)
        return cleaned_data

    class Meta:
        model = Estimate
        fields = '__all__'
        exclude = ['estimate_concept']
        labels = {
            'consecutive': 'Consecutivo',
            'descripcion': 'Descripción',
            'supervised_by': 'Supervisado por:',
            'start_date': 'Fecha de inicio',
            'finish_date': 'Fecha de finalización',
            'auth_by': 'Autorizado por [Estimación]:',
            'auth_by_gen': 'Autorizado por [Generador]:',
            'auth_date': 'Fecha de autorización',
            'paid': '¿Pagada?',
            'invoiced': '¿Facturada?',
            'payment_date': 'Fecha de pago',
        }
        widgets = {
            'consecutive': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ),
            'project': forms.HiddenInput(),
            'draft_by': forms.HiddenInput(),
            'supervised_by': autocomplete.ModelSelect2(
                url='proyectos:user-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
            'start_date': forms.DateInput(
                attrs={
                    'class': 'datetimepicker-input',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#id_start_date',
                    'name': 'start_date'
                },
                format=MY_DATE_FORMATS
            ),
            'finish_date': forms.DateInput(
                attrs={
                    'class': 'datetimepicker-input',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#id_finish_date',
                    'name': 'finish_date'
                },
                format=MY_DATE_FORMATS
            ),
            'auth_by': autocomplete.ModelSelect2Multiple(
                url='proyectos:destinatario-autocomplete',
                forward=['project'],
                attrs={
                    'data-minimum-input-length': 2,
                }
            ),
            'auth_by_gen': autocomplete.ModelSelect2Multiple(
                url='proyectos:destinatario-autocomplete',
                forward=['project'],
                attrs={
                    'data-minimum-input-length': 2,
                }
            ),
            'auth_date': forms.DateInput(
                attrs={
                    'class': 'datetimepicker-input',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#id_auth_date',
                    'name': 'auth_date'
                },
                format=MY_DATE_FORMATS
            ),
            'payment_date': forms.DateInput(
                attrs={
                    'class': 'datetimepicker-input',
                    'data-toggle': 'datetimepicker',
                    'data-target': '#id_payment_date',
                    'name': 'payment_date'
                },
                format=MY_DATE_FORMATS
            ),
        }


class ConceptDummyWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        """
            esto se queda asi.... todavia no se porque, espero que se sepa con
            las pruebas de las vistas.
        """
        try:
            value_instance = Concept.objects.get(pk=value)
            self.value = value_instance
        except:
            self.value = str(Concept.objects.get(concept_text=value).id)
            widget = forms.Select(choices=(self.value,))
            return widget.render(name, self.value, attrs)
        return super(ConceptDummyWidget, self).render(name, self.value, attrs)

    def value_from_datadict(self, data, files, name):
        """
            Funcion que usa la vista, todavia para pasar los datos al render
            en algunos casos es un numero, otros es texto, se maneja deacuerdo
            a como venga.
        """
        data_name = data.get(name)
        try:
            value = str(Concept.objects.get(concept_text=data_name).id)
            return value
        except ObjectDoesNotExist:
            if isinstance(data_name, int):
                return data_name
            else:
                raise


class FileNestedWidget(forms.ClearableFileInput):
    template_name = 'proyectos/file_input.html'


imageformset = forms.inlineformset_factory(
    EstimateConcept,
    ImageEstimateConcept,
    extra=1,
    fields=('image',),
    widgets={'image': FileNestedWidget()},
)


class BaseEstimateConceptInlineFormset(forms.BaseInlineFormSet):

    def add_fields(self, form, index):
        super(BaseEstimateConceptInlineFormset, self).add_fields(form, index)

        form.nested = imageformset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                imageformset.get_default_prefix()
            ),
        )

    def is_valid(self):
        result = super(BaseEstimateConceptInlineFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    nested_validity = form.nested.is_valid()
                    result &= nested_validity
        return result

    def save(self, commit=True):
        result = super(BaseEstimateConceptInlineFormset, self).save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                form.nested.save(commit=commit)
        return result


def estimateConceptInlineForm(count=0):
    inlineform = forms.inlineformset_factory(Estimate, EstimateConcept, fields=(
        'concept',
        'cuantity_estimated',
        'observations'
    ), max_num=count, extra=count, can_delete=False, widgets={
        'concept': ConceptDummyWidget(attrs={'readonly': True}),
        'cuantity_estimated': forms.TextInput(),
        'observations': forms.Textarea(attrs={'rows': 3})
    }, labels={
        'concept': 'Concepto',
        'cuantity_estimated': 'Cantidad estimada',
        'observations': 'Observaciones'
    }, formset=BaseEstimateConceptInlineFormset)
    return inlineform


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
