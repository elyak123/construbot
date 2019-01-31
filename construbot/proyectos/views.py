from django import shortcuts
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db.models import Max, F, Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from wkhtmltopdf.views import PDFTemplateView
from construbot.users.auth import AuthenticationTestMixin
from construbot.users.models import Company
from construbot.proyectos import forms
from construbot.core.utils import BasicAutocomplete
from .apps import ProyectosConfig
from .models import Contrato, Cliente, Sitio, Units, Concept, Destinatario, Estimate
from .utils import contratosvigentes

User = get_user_model()


class ProyectosMenuMixin(AuthenticationTestMixin):
    tengo_que_ser_admin = True
    app_label_name = ProyectosConfig.verbose_name
    menu_specific = [
        {
            'title': 'Contratos',
            'url': 'construbot.proyectos:listado_de_contratos',
            'always_appear': True,
            'icon': 'bookmark',
            'parent': False,
            'type': 'submenu',
            'submenu': [],
        },
        {
            'title': 'Clientes',
            'url': 'construbot.proyectos:listado_de_clientes',
            'always_appear': True,
            'icon': 'person',
            'parent': False,
            'type': 'submenu',
            'submenu': [],
        },
        {
            'title': 'Ubicaciones',
            'url': 'construbot.proyectos:listado_de_sitios',
            'always_appear': True,
            'icon': 'map-marker',
            'parent': False,
            'type': 'submenu',
            'submenu': [],
        },
        {
            'title': 'Contactos',
            'url': 'construbot.proyectos:listado_de_destinatarios',
            'always_appear': True,
            'icon': 'people',
            'parent': False,
            'type': 'submenu',
            'submenu': [],
        },            
    ]
    model_options = {
        'Contrato': {
            'model': Contrato,
        },
        'Cliente': {
            'ordering': 'cliente_name',
            'model': Cliente,
        },
        'Sitio': {
            'ordering': 'sitio_name',
            'model': Sitio,
        },
        'Destinatario': {
            'ordering': 'destinatario_text',
            'model': Destinatario,
        },
        'Estimate': {
            'model': Estimate,
        }
    }

    def get_company_query(self, opcion):
        company_query = {
            'Contrato': {
                'cliente__company': self.request.user.currently_at,
                'users': self.request.user
            },
            'Cliente': {
                'company': self.request.user.currently_at
            },
            'Sitio': {
                'cliente__company': self.request.user.currently_at
            },
            'Destinatario': {
                'cliente__company': self.request.user.currently_at
            },
            'Estimate': {
                'project__cliente__company': self.request.user.currently_at
            },
        }
        return company_query[opcion]


class ProyectDashboardView(ProyectosMenuMixin, ListView):
    tengo_que_ser_admin = False
    template_name = 'proyectos/index.html'
    model = Contrato

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(ProyectDashboardView, self).get_context_data(**kwargs)
        context['object'] = self.request.user.currently_at
        context['c_object'] = contratosvigentes(
            self.request.user, self.permiso_administracion
        )
        return context


class DynamicList(ProyectosMenuMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.model.objects.filter(
                **self.get_company_query(self.model.__name__)).order_by(
                Lower(self.model_options[self.model.__name__]['ordering'])
            )
        return super(DynamicList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(DynamicList, self).get_context_data(**kwargs)
        context['model'] = self.model.__name__
        return context


class ContratoListView(DynamicList):
    model = Contrato
    ordering = '-fecha'

    def get_queryset(self):
        if self.request.user.is_administrator():
            self.queryset = self.model.objects.filter(
                cliente__company=self.request.user.currently_at)
        else:
            self.queryset = self.model.objects.filter(
                **self.get_company_query(self.model.__name__)
            )
        return super(ContratoListView, self).get_queryset()


class ClienteListView(DynamicList):
    model = Cliente


class SitioListView(DynamicList):
    model = Sitio


class DestinatarioListView(DynamicList):
    model = Destinatario


class CatalogoConceptos(ProyectosMenuMixin, ListView):
    model = Concept
    ordering = 'code'

    def get(self, request, *args, **kwargs):
        contrato = shortcuts.get_object_or_404(
            Contrato, pk=self.kwargs['pk'], cliente__company=self.request.user.currently_at
        )
        queryset = self.model.objects.filter(project=contrato)
        json = {}
        json['conceptos'] = []
        for concepto in queryset:
            aux = {}
            aux["code"] = concepto.code
            aux["concept_text"] = concepto.concept_text
            aux["unit"] = concepto.unit.unit
            aux["cuantity"] = concepto.total_cuantity
            aux["unit_price"] = concepto.unit_price
            json['conceptos'].append(aux)
        return JsonResponse(json)


class DynamicDetail(ProyectosMenuMixin, DetailView):
    change_company_ability = False

    def get_context_object_name(self, obj):
        return obj.__class__.__name__.lower()

    def get_object(self, queryset=None):
        return shortcuts.get_object_or_404(
            self.model, pk=self.kwargs['pk'], **self.get_company_query(self.model.__name__)
        )


class ContratoDetailView(DynamicDetail):
    tengo_que_ser_admin = False
    model = Contrato

    def get_object(self, queryset=None):
        query_kw = self.get_company_query(self.model.__name__)
        query_kw.update({'pk': self.kwargs['pk']})
        if self.request.user.is_administrator():
            del query_kw['users']
        return shortcuts.get_object_or_404(self.model, **query_kw)


class ClienteDetailView(DynamicDetail):
    model = Cliente


class SitioDetailView(DynamicDetail):
    model = Sitio


class DestinatarioDetailView(DynamicDetail):
    model = Destinatario


class EstimateDetailView(DynamicDetail):
    tengo_que_ser_admin = False
    model = Estimate

    def get_context_data(self, **kwargs):
        context = super(EstimateDetailView, self).get_context_data(**kwargs)
        context["conceptos"] = self.object.anotaciones_conceptos()
        context["cantidad_de_conceptos"] = len(context["conceptos"])
        return context


class BasePDFGenerator(PDFTemplateView, EstimateDetailView):
    filename = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.get_context_data(object=self.object)
        return super(BasePDFGenerator, self).get(self.request, *args, **kwargs)

    def get_cmd_options(self):
        return {
            'orientation': 'Landscape',
            'javascript-delay': 1000
        }

    def get_context_data(self, **kwargs):
        context = super(BasePDFGenerator, self).get_context_data(**kwargs)
        context['pdf'] = True
        return context


class EstimatePdfPrint(BasePDFGenerator):
    template_name = 'proyectos/concept_estimate.html'


class GeneratorPdfPrint(BasePDFGenerator):
    template_name = 'proyectos/concept_generator.html'


class ContratoCreationView(ProyectosMenuMixin, CreateView):
    change_company_ability = False
    form_class = forms.ContratoForm
    template_name = 'proyectos/creation_form.html'

    def get_form(self, *args, **kwargs):
        form = super(ContratoCreationView, self).get_form(form_class=None)
        form.request = self.request
        return form

    def get_initial(self):
        initial_obj = super(ContratoCreationView, self).get_initial()
        max_id = self.form_class.Meta.model.objects.filter(
            cliente__company=self.request.user.currently_at
        ).aggregate(Max('folio'))['folio__max'] or 0
        max_id += 1
        initial_obj['currently_at'] = self.request.user.currently_at.company_name
        initial_obj['folio'] = max_id
        initial_obj['users'] = [usr.pk for usr in User.objects.filter(
            company=self.request.user.currently_at,
            groups__name='Administrators')]
        return initial_obj

    def get_context_data(self, **kwargs):
        context = super(ContratoCreationView, self).get_context_data(**kwargs)
        context['company'] = self.request.user.currently_at
        return context


class DynamicCreation(ProyectosMenuMixin, CreateView):
    change_company_ability = False
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(DynamicCreation, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def get_form(self, *args, **kwargs):
        form = super(DynamicCreation, self).get_form(form_class=None)
        form.request = self.request
        return form


class ClienteCreationView(DynamicCreation):
    form_class = forms.ClienteForm


class SitioCreationView(DynamicCreation):
    form_class = forms.SitioForm


class DestinatarioCreationView(DynamicCreation):
    form_class = forms.DestinatarioForm


class EstimateCreationView(ProyectosMenuMixin, CreateView):
    change_company_ability = False
    tengo_que_ser_admin = False
    form_class = forms.EstimateForm
    model = Contrato
    template_name = 'proyectos/estimate_form.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        fill_data = self.fill_concept_formset()
        inlineform = forms.estimateConceptInlineForm(count=self.concept_count)
        return self.render_to_response(
            self.get_context_data(**self.get_prepare_generator_context(form, inlineform, fill_data))
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        fill_data = self.fill_concept_formset()
        if form.is_valid():
            return self.form_valid(form, fill_data)
        else:
            inlineform = forms.estimateConceptInlineForm(count=self.concept_count)
            return self.form_invalid(form, inlineform, fill_data)

    def get_prepare_generator_context(self, form, inlineform, fill_data):
        if hasattr(inlineform, 'form') and callable(inlineform):
            if not hasattr(inlineform, 'is_bound') or not inlineform.is_bound:
                generator_inline_concept = inlineform(initial=fill_data)
        else:
            generator_inline_concept = inlineform
        codes = [x['concept'].code for x in fill_data]
        image_formset_prefix = [x.nested.prefix for x in generator_inline_concept.forms]
        return_dict = {
            'form': form,
            'generator_inline_concept': generator_inline_concept,
            'generator_zip': zip(generator_inline_concept, codes),
            'image_formset_prefix': image_formset_prefix
        }
        return return_dict

    def fill_concept_formset(self):
        self.project_instance = shortcuts.get_object_or_404(
            Contrato,
            pk=self.kwargs.get('pk'),
            cliente__company=self.request.user.currently_at
        )
        concepts = Concept.objects.filter(project=self.project_instance).order_by('id')
        data = [
            {
                'concept': x, 'cuantity_estimated': 0,
                'concept_text_input': x.concept_text
            } for x in concepts
        ]
        self.concept_count = concepts.count()
        return data

    def get_initial(self):
        initial_dict = super(EstimateCreationView, self).get_initial()

        max_consecutive = Estimate._meta.model._default_manager.filter(
            project=self.kwargs['pk']
        ).aggregate(Max('consecutive'))['consecutive__max'] or 0
        max_consecutive += 1

        initial_dict['consecutive'] = max_consecutive
        initial_dict['project'] = self.kwargs['pk']
        initial_dict['draft_by'] = self.request.user
        return initial_dict

    def form_valid(self, form, fill_data):
        inlineform = forms.estimateConceptInlineForm(count=self.concept_count)
        generator_inline_concept = inlineform(
            self.request.POST,
            self.request.FILES,
            instance=form.instance
        )
        if generator_inline_concept.is_valid():
            response = super(EstimateCreationView, self).form_valid(form)
            generator_inline_concept.save()
            return response
        else:
            return self.form_invalid(form, generator_inline_concept, fill_data)

    def form_invalid(self, form, inlineform, fill_data):
        return self.render_to_response(
            self.get_context_data(**self.get_prepare_generator_context(form, inlineform, fill_data))
        )

    def get_success_url(self):
        url = reverse_lazy('proyectos:contrato_detail', kwargs={
            'pk': self.kwargs['pk']
        })
        return url

    def get_context_data(self, **kwargs):
        context = super(EstimateCreationView, self).get_context_data(**kwargs)
        context['project_instance'] = self.project_instance
        return context


class DynamicEdition(ProyectosMenuMixin, UpdateView):
    change_company_ability = False
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = shortcuts.get_object_or_404(
            self.form_class.Meta.model,
            pk=self.kwargs['pk'],
            **self.get_company_query(self.form_class.Meta.model.__name__)
        )
        return obj

    def get_initial(self):
        initial_obj = super(DynamicEdition, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def get_form(self, *args, **kwargs):
        form = super(DynamicEdition, self).get_form(form_class=None)
        form.request = self.request
        return form


class ContratoEditView(ProyectosMenuMixin, UpdateView):
    change_company_ability = False
    form_class = forms.ContratoForm
    template_name = 'proyectos/creation_form.html'

    def get_form(self, *args, **kwargs):
        form = super(ContratoEditView, self).get_form(form_class=None)
        form.request = self.request
        return form

    def get_object(self):
        if self.request.user.is_administrator():
            obj = shortcuts.get_object_or_404(
                Contrato,
                pk=self.kwargs['pk'],
                cliente__company=self.request.user.currently_at
            )
        else:
            obj = shortcuts.get_object_or_404(
                Contrato,
                pk=self.kwargs['pk'],
                **self.get_company_query('Contrato')
            )
        return obj

    def get_initial(self):
        initial_obj = super(ContratoEditView, self).get_initial()
        initial_obj['currently_at'] = self.request.user.currently_at.company_name
        return initial_obj


class ClienteEditView(DynamicEdition):
    form_class = forms.ClienteForm


class SitioEditView(DynamicEdition):
    form_class = forms.SitioForm


class DestinatarioEditView(DynamicEdition):
    form_class = forms.DestinatarioForm


class EstimateEditView(ProyectosMenuMixin, UpdateView):
    tengo_que_ser_admin = False
    change_company_ability = False
    form_class = forms.EstimateForm
    template_name = 'proyectos/estimate_form.html'
    model = Estimate

    def get_object(self, queryset=None):
        self.object = shortcuts.get_object_or_404(
            self.model,
            pk=self.kwargs['pk'],
            project__cliente__company=self.request.user.currently_at
        )
        return self.object

    def get_initial(self):
        init_dict = {}
        init_dict['draft_by'] = self.request.user
        init_dict['project'] = self.kwargs['pk']
        return super(EstimateEditView, self).get_initial()

    def form_valid(self, form):
        form.save()
        conceptformclass = forms.estimateConceptInlineForm()
        self.conceptForm = conceptformclass(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        if self.conceptForm.is_valid():
            self.conceptForm.save()
            return super(EstimateEditView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_formset_for_context(self):
        if not hasattr(self, 'conceptForm'):
            formset = forms.estimateConceptInlineForm()(instance=self.object)
        else:
            formset = self.conceptForm
        return formset

    def get_concept_codes(self):
        self.project_instance = shortcuts.get_object_or_404(
            Contrato,
            pk=self.object.project.pk,
            cliente__company=self.request.user.currently_at
        )
        concepts = [x.code for x in Concept.objects.filter(project=self.project_instance).order_by('id')]
        return concepts

    def get_context_data(self, **kwargs):
        context = super(EstimateEditView, self).get_context_data(**kwargs)
        project_instance = Estimate.objects.get(pk=self.kwargs.get('pk')).project
        formset = self.get_formset_for_context()
        concept_codes = self.get_concept_codes()
        image_formset_prefix = [x.nested.prefix for x in formset.forms]
        context['generator_inline_concept'] = formset
        context['generator_zip'] = zip(formset, concept_codes)
        context['image_formset_prefix'] = image_formset_prefix
        context['project_instance'] = project_instance
        return context


class CatalogosView(ProyectosMenuMixin, UpdateView):

    def get_object(self):
        self.model = self.form_class.fk.related_model._meta.model
        obj = shortcuts.get_object_or_404(
            self.model,
            cliente__company=self.request.user.currently_at,
            pk=self.kwargs['pk']
        )
        return obj

    def get_success_url(self):
        return reverse(
            'construbot.proyectos:contrato_detail',
            kwargs={'pk': self.kwargs['pk']}
        )

    def get_context_data(self, **kwargs):
        context = super(CatalogosView, self).get_context_data(**kwargs)
        context['type'] = self.tipo if hasattr(self, 'tipo') else None
        context['formset'] = context.pop('form')
        return context


class CatalogoRetencionesInlineFormView(CatalogosView):
    change_company_ability = False
    form_class = forms.ContractRetentionInlineForm
    template_name = 'proyectos/catalogo-conceptos-inline.html'
    tipo = 'retenciones'


class CatalogoConceptosInlineFormView(CatalogosView):
    change_company_ability = False
    form_class = forms.ContractConceptInlineForm
    template_name = 'proyectos/catalogo-conceptos-inline.html'
    tipo = 'conceptos'


class DynamicDelete(ProyectosMenuMixin, DeleteView):
    template_name = 'core/delete.html'

    def get_object(self):
        self.model = self.model_options[self.kwargs['model']]['model']
        obj = shortcuts.get_object_or_404(
            self.model,
            **self.get_company_query(self.kwargs['model']),
            pk=self.kwargs['pk']
        )
        return obj

    def get_company_query(self, opcion):
        kwargs = super(DynamicDelete, self).get_company_query(opcion)
        if hasattr(self, 'object'):
            if opcion == 'Estimate':
                folio = {'consecutive__gt': self.object.consecutive}
                field = 'consecutive'
            else:
                folio = {'folio__gt': self.object.folio}
                field = 'folio'
            kwargs.update(folio)
            return (kwargs, field)
        return kwargs

    def folio_handling(self):
        if hasattr(self.object, 'folio') or hasattr(self.object, 'consecutive'):
            kwargs, field = self.get_company_query(self.kwargs['model'])
            if(hasattr(self.object, 'folio')):
                self.model.objects.filter(**kwargs).update(folio=F(field) - 1)
            else:
                self.model.objects.filter(**kwargs).update(consecutive=F(field) - 1)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.folio_handling()
        self.object.delete()
        return JsonResponse({"exito": True})


class AutocompletePoryectos(BasicAutocomplete):
    app_label_name = ProyectosConfig.verbose_name

    def get_key_words(self):
        base_string = '__unaccent__icontains'
        if self.create_field:
            search_string = self.create_field + base_string
            return {search_string: self.q}
        else:
            return {}


class ClienteAutocomplete(AutocompletePoryectos):
    model = Cliente
    ordering = 'cliente_name'

    def get_key_words(self):
        key_words = super(ClienteAutocomplete, self).get_key_words()
        key_words.update({'company': self.request.user.currently_at})
        return key_words

    def get_post_key_words(self):
        kw = {'company': self.request.user.currently_at}
        return kw


class SitioAutocomplete(AutocompletePoryectos):
    model = Sitio
    ordering = 'sitio_name'

    def get_key_words(self):
        key_words = super(SitioAutocomplete, self).get_key_words()
        key_words.update({'cliente__company': self.request.user.currently_at})
        return key_words

    def get_post_key_words(self):
        # Depende enteramente de la existencia de destinatario en el
        # formulario... suceptible a errores....
        cliente = shortcuts.get_object_or_404(Cliente, pk=int(self.forwarded.get('cliente')))
        kw = {'cliente': cliente}
        return kw


class DestinatarioAutocomplete(AutocompletePoryectos):
    model = Destinatario
    ordering = 'destinatario_text'

    def get_key_words(self):
        key_words = super(DestinatarioAutocomplete, self).get_key_words()
        key_words.update({'cliente': Contrato.objects.get(pk=int(self.forwarded.get('project'))).cliente})
        return key_words

    def get_post_key_words(self):
        kw = {'cliente': Contrato.objects.get(pk=int(self.forwarded.get('project'))).cliente}
        return kw


class UnitAutocomplete(AutocompletePoryectos):
    model = Units
    ordering = 'unit'

    def get_key_words(self):
        if hasattr(self, 'create_field') and self.create_field is not None:
            key_words = super(UnitAutocomplete, self).get_key_words()
            key_words.update({'company': self.request.user.currently_at})
        else:
            key_words = {
                'unit__unaccent__icontains': self.q,
                'company': self.request.user.currently_at
            }
        return key_words

    def get_post_key_words(self):
        kw = {'company': self.request.user.currently_at}
        return kw


class UserAutocomplete(AutocompletePoryectos):
    model = User
    ordering = 'username'

    def get_queryset(self):
        if self.request.user and self.q:
            qs = self.model.objects.filter(
                (Q(username__unaccent__icontains=self.q) | Q(email__unaccent__icontains=self.q)),
                company=self.request.user.currently_at
            )
            return qs
        elif self.request.user and self.request.POST:
            return self.model.objects


class CompanyAutocomplete(AutocompletePoryectos):
    model = Company
    ordering = 'company_name'

    def get_key_words(self):
        key_words = {
            'company_name__unaccent__icontains': self.q,
        }
        return key_words

    def get_queryset(self):
        if self.request.user and self.q:
            qs = self.request.user.company.filter(**self.get_key_words()).order_by(self.ordering)
            return qs
        elif self.request.user and self.request.POST:
            return self.model.objects
