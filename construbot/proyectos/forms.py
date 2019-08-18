from django.db import transaction
from django import forms
from dal import autocomplete
from treebeard.mp_tree import MP_AddRootHandler, MP_AddChildHandler
from .models import (
    Contrato, Cliente, Sitio, Concept, Destinatario, Estimate,
    EstimateConcept, ImageEstimateConcept, Retenciones, Units, Vertices)
from construbot.users.models import Company
from construbot.proyectos import widgets

MY_DATE_FORMATS = '%Y-%m-%d'


# class ContratoDummyFileForm(forms.Form):
#     dummy_archivo = forms.FileField()


class ContratoForm(forms.ModelForm):
    currently_at = forms.CharField(widget=forms.HiddenInput())
    # relacion_id_archivo = forms.CharField(widget=forms.HiddenInput(), required=False)

    def obj_transaction_process(self):
        with transaction.atomic():
            instance = MP_AddRootHandler(Contrato, **self.cleaned_data).process()
        return instance

    def save(self, commit=True):
        usrs = self.cleaned_data.pop('users')
        self.cleaned_data.pop('currently_at')
        self.instance = self.obj_transaction_process()
        super(ContratoForm, self).save(commit=False)
        self.cleaned_data.update({'users': usrs})
        self.save_m2m()
        return self.instance

    def clean(self):
        result = super(ContratoForm, self).clean()
        if self.cleaned_data.get('currently_at') is None:
            raise forms.ValidationError('Error en la formación del formulario, es posible que este corrupto,'
                                        'porfavor recarga y vuelve a intentarlo')
        if self.cleaned_data.get('currently_at') == self.request.user.currently_at.company_name:
            if self.request.user.is_new:
                self.request.user.is_new = False
                self.request.user.save()
            return result
        else:
            raise forms.ValidationError(
                'Actualmente te encuentras en otra compañia, '
                'es necesario recargar y repetir el proceso.'
            )

    class Meta:
        model = Contrato
        fields = [
            'folio', 'code', 'fecha', 'contrato_name',
            'contrato_shortName', 'cliente', 'sitio',
            'status', 'file', 'monto', 'users', 'anticipo'
        ]
        labels = {
            'code': 'Folio del contrato',
            'contrato_name': 'Nombre del contrato',
            'contrato_shortName': 'Nombre corto',
            'file': 'PDF del Contrato',
            'users': '¿A qué usuarios desea asignarlo?',
            'status': '¿El proyecto sigue en curso?'
        }
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
            'file': forms.FileInput(
                attrs={
                    'accept': 'application/pdf',
                },
            ),
            'anticipo': forms.TextInput(
                attrs={'style': 'width:200px;'}
            ),
        }
        help_texts = {
            'code': 'Código del contrato, este código debe coincidir con el código del contrato firmado.',
            'folio': 'ID consecutivo de contrato en la compañía.',
            'contrato_name': 'Nombre completo del proyecto, se utilizará para generar la estimación.',
            'contrato_shortName': 'Identificador corto del contrato para control en listados.',
            'cliente': '¿Con qué empresa/persona física firmé el contrato?',
            'sitio': '¿En qué predio será realizado el proyecto?',
            'status': 'Indique si el proyecto sigue en curso.',
            'monto': 'Cantidad por la cual se firmó el contrato. Sin IVA',
            'users': 'Seleccione a los usuarios a los que les quiere asignar el contrato.',
            'anticipo': 'Indique el porcentaje (de 0% a 100%) de anticipo del proyecto.'
        }


class SubContratoForm(ContratoForm):

    def obj_transaction_process(self):
        with transaction.atomic():
            instance = MP_AddChildHandler(self.contrato, **self.cleaned_data).process()
        return instance


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
        labels = {
            'cliente_name': 'Nombre del cliente'
        }
        widgets = {
            'company': forms.HiddenInput()
        }
        help_texts = {
            'cliente_name': 'Nombre o razón social del cliente con el cuál tendrá proyectos.',
        }


class SitioForm(forms.ModelForm):

    class Meta:
        model = Sitio
        fields = '__all__'
        labels = {
            'sitio_name': 'Nombre del sitio',
            'sitio_location': 'Ubicación',
            'cliente': '¿A qué cliente pertenece?'
        }
        widgets = {
            'cliente': autocomplete.ModelSelect2(
                url='proyectos:cliente-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
        }
        help_texts = {
            'sitio_name': 'Nombre de la locación en la que se harán proyectos.',
            'sitio_location': 'Ciudad dónde se encuentra el sitio',
            'cliente': '¿A qué empresa/persona física le pertenece o se relaciona?'
        }


class DestinatarioForm(forms.ModelForm):

    class Meta:
        model = Destinatario
        fields = '__all__'
        labels = {
            'destinatario_text': 'Nombre del destinatario',
            'cliente': '¿En qué empresa trabaja?'
        }
        widgets = {
            'cliente': autocomplete.ModelSelect2(
                url='proyectos:cliente-autocomplete',
                attrs={'data-minimum-input-length': 3}
            ),
        }
        help_texts = {
            'destinatario_text': 'Nombre del representante de la empresa que firmará documentos.',
            'puesto': '¿En qué puesto trabaja?',
            'cliente': '¿Para qué empresa/persona física trabaja?'
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
        help_texts = {
            'consecutive': 'Número de estimación correspondiente al proyecto.',
            'supervised_by': '¿Qué usuario fue residente de obra?',
            'start_date': 'Fecha de inicio del período que comprende la estimación.',
            'finish_date': 'Fecha de finalización del período que comprende la estimación.',
            'auth_by': '¿Qué personas encargadas de la empresa cliente autorizan la estimación?',
            'auth_by_gen': '¿Qué personas encargadas de la empresa cliente autorizan el generador?',
            'auth_date': 'Fecha en la que la estimación ha sido autorizada.',
            'paid': '¿La estimación ya fue pagada?',
            'invoiced': '¿La estimación ya fue facturada?',
            'payment_date': 'En caso de que la estimación ya haya sido pagada, indique la fecha de pago.',
            'mostrar_anticipo': '¿Desea que en la versión impresa se muestre el concepto de anticipo?',
            'mostrar_retenciones': '¿Desea que en la versión impresa se muestren las retenciones efectuadas?'
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


class ImageInlineFormset(forms.BaseInlineFormSet):
    def clean(self):
        result = super(ImageInlineFormset, self).clean()
        limit_size = 2097152
        for frm in self.cleaned_data:
            img = frm.get("image", None)
            if img is not None:
                if img.size > limit_size:
                    raise forms.ValidationError("El tamaño de la imagen excede el tamaño permitido de 2MB.")


imageformset = forms.inlineformset_factory(
    EstimateConcept,
    ImageEstimateConcept,
    extra=1,
    fields=('image',),
    widgets={'image': widgets.FileNestedWidget()},
    formset=ImageInlineFormset,
)

verticesformset = forms.inlineformset_factory(
    EstimateConcept,
    Vertices,
    extra=1,
    fields=('nombre', 'largo', 'ancho', 'alto', 'piezas')
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
        form.vertices = verticesformset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                verticesformset.get_default_prefix()
            ),
        )

    def is_valid(self):
        result = super(BaseEstimateConceptInlineFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    nested_validity = form.nested.is_valid()
                    result &= nested_validity
                if hasattr(form, 'vertices'):
                    vertice_validity = form.vertices.is_valid()
                    result &= vertice_validity
        return result

    def save(self, commit=True):
        result = super(BaseEstimateConceptInlineFormset, self).save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                form.nested.save(commit=commit)
            if hasattr(form, 'vertices'):
                form.vertices.save(commit=commit)
        return result


class BaseUnitFormset(forms.BaseInlineFormSet):

    def clean(self):
        deleted_units = self.deleted_forms
        validation_errors = []
        for form in deleted_units:
            if form.instance.concept_set.count() > 0:
                validation_errors.append(forms.ValidationError(
                    '{} no puede ser eliminado, tiene conceptos '
                    'que deben ser eliminados primero.'.format(form.instance.unit))
                )
        if len(validation_errors) > 0:
            raise forms.ValidationError(validation_errors)


def estimateConceptInlineForm(count=0):
    inlineform = forms.inlineformset_factory(Estimate, EstimateConcept, fields=(
        'concept',
        'cuantity_estimated',
        'observations',
    ), max_num=count, extra=count, can_delete=False, widgets={
        'concept': widgets.ConceptDummyWidget(attrs={'readonly': True, 'rows': ""}),
        'cuantity_estimated': forms.TextInput(),
        'observations': forms.Textarea(
            attrs={'rows': '3', 'cols': '40'}
        )
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
            'cols': '20',
            'rows': '4'
        }),
        'unit': autocomplete.ModelSelect2(
            url='proyectos:unit-autocomplete',
            attrs={'class': 'n-input', 'data-minimum-input-length': 1}
        ),
        'total_cuantity': forms.NumberInput(attrs={
            'class': 'n-input',
        }),
        'unit_price': forms.NumberInput(attrs={
            'class': 'n-input',
        }),
        'code': forms.TextInput(attrs={
            'maxlength': '6',
            'class': 'inlineCode',
        }),
    },
)

ContractRetentionInlineForm = forms.inlineformset_factory(
    Contrato, Retenciones,
    fields=(
        'nombre',
        'tipo',
        'valor',
    ),
    extra=1,
)

UnitsInlineForm = forms.inlineformset_factory(
    Company, Units,
    fields=(
        'unit',
    ),
    extra=1,
    formset=BaseUnitFormset
)
