from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView, DeleteView
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db.models.functions import Lower
from django.http import JsonResponse, HttpResponseRedirect
from dal import autocomplete
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato, Cliente, Sitio, Units, Concept, Destinatario
from .forms import ContratoForm, ClienteForm, SitioForm, DestinatarioForm, ContractConceptInlineForm


class ProyectosMenuMixin(AuthenticationTestMixin):
    app_label_name = ProyectosConfig.verbose_name
    menu_specific = [
        {
            'title': 'Catalogos',
            'url': '',
            'icon': 'book',
            'parent': True,
            'type': 'submenu',
            'submenu': [
                {
                    'title': 'Contratos',
                    'url': 'construbot.proyectos:listado_de_contratos',
                    'urlkwargs': '',
                    'icon': 'bookmark',
                },
                {
                    'title': 'Clientes',
                    'url': 'construbot.proyectos:listado_de_clientes',
                    'urlkwargs': '',
                    'icon': 'person',
                },
                {
                    'title': 'Ubicaciones',
                    'url': 'construbot.proyectos:listado_de_sitios',
                    'urlkwargs': '',
                    'icon': 'map-marker',
                },
                {
                    'title': 'Contactos',
                    'url': 'construbot.proyectos:listado_de_destinatarios',
                    'urlkwargs': '',
                    'icon': 'people',
                },
            ],
        }
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
    }

    def get_company_query(self, opcion):
        company_query = {
            'Contrato': {
                'cliente__company': self.request.user.currently_at
            },
            'Cliente': {
                'company': self.request.user.currently_at
            },
            'Sitio': {
                'company': self.request.user.currently_at
            },
            'Destinatario': {
                'cliente__company': self.request.user.currently_at
            },
        }
        return company_query[opcion]


class DynamicList(ProyectosMenuMixin, ListView):
    def get_queryset(self):
        if not self.queryset:
            self.queryset = self.model.objects.filter(
                **self.get_company_query(self.model.__name__)).order_by(
                Lower(self.model_options[self.model.__name__]['ordering'])
            )
        return super(DynamicList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(DynamicList, self).get_context_data(**kwargs)
        context['model'] = self.model.__name__
        return context


class EstimacionSample(ProyectosMenuMixin, TemplateView):
    template_name = 'proyectos/sample.html'


class ContratoListView(DynamicList):
    model = Contrato
    ordering = '-fecha'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            **self.get_company_query(self.model.__name__))
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
        contrato = get_object_or_404(Contrato, pk=self.kwargs['pk'], cliente__company=self.request.user.currently_at)
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
    def get_context_object_name(self, obj):
        return obj.__class__.__name__.lower()

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'], **self.get_company_query(self.model.__name__))


class ContratoDetailView(DynamicDetail):
    model = Contrato


class ClienteDetailView(DynamicDetail):
    model = Cliente


class SitioDetailView(DynamicDetail):
    model = Sitio


class DestinatarioDetailView(DynamicDetail):
    model = Destinatario


class ContratoCreationView(ProyectosMenuMixin, CreateView):
    form_class = ContratoForm
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(ContratoCreationView, self).get_initial()
        max_id = self.form_class.Meta.model.objects.filter(
            cliente__company=self.request.user.currently_at
        ).aggregate(Max('folio'))['folio__max'] or 0
        max_id += 1
        initial_obj['currently_at'] = self.request.user.currently_at.company_name
        initial_obj['folio'] = max_id
        return initial_obj

    def get_context_data(self, **kwargs):
        context = super(ContratoCreationView, self).get_context_data(**kwargs)
        context['company'] = self.request.user.currently_at
        return context

    def form_valid(self, form):
        if form.cleaned_data['currently_at'] == self.request.user.currently_at.company_name:
            return super(ContratoCreationView, self).form_valid(form)
        else:
            return super(ContratoCreationView, self).form_invalid(form)


class DynamicCreation(ProyectosMenuMixin, CreateView):
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(DynamicCreation, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            return super(DynamicCreation, self).form_valid(form)
        else:
            return super(DynamicCreation, self).form_invalid(form)


class ClienteCreationView(DynamicCreation):
    form_class = ClienteForm


class SitioCreationView(DynamicCreation):
    form_class = SitioForm


class DestinatarioCreationView(DynamicCreation):
    form_class = DestinatarioForm


class DynamicEdition(ProyectosMenuMixin, UpdateView):
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            self.form_class.Meta.model,
            pk=self.kwargs['pk'],
            **self.get_company_query(self.form_class.Meta.model.__name__)
        )
        return obj

    def get_initial(self):
        initial_obj = super(DynamicEdition, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            return super(DynamicEdition, self).form_valid(form)
        else:
            return super(DynamicEdition, self).form_invalid(form)


class ContratoEditView(ProyectosMenuMixin, UpdateView):
    form_class = ContratoForm
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            Contrato,
            pk=self.kwargs['pk'],
            cliente__company=self.request.user.currently_at
        )
        return obj

    def get_initial(self):
        initial_obj = super(ContratoEditView, self).get_initial()
        initial_obj['currently_at'] = self.request.user.currently_at.company_name
        return initial_obj

    def form_valid(self, form):
        currently = form.cleaned_data.get('currently_at')
        if currently and currently == self.request.user.currently_at.company_name:
            self.object = form.save()
            return super(ContratoEditView, self).form_valid(form)
        else:
            return super(ContratoEditView, self).form_invalid(form)


class ClienteEditView(DynamicEdition):
    form_class = ClienteForm


class SitioEditView(DynamicEdition):
    form_class = SitioForm


class DestinatarioEditView(DynamicEdition):
    form_class = DestinatarioForm


class CatalogoConceptosInlineFormView(ProyectosMenuMixin, UpdateView):
    form_class = ContractConceptInlineForm
    template_name = 'proyectos/catalogo-conceptos-inline.html'

    def get_object(self):
        self.model = self.form_class.fk.related_model._meta.model
        obj = get_object_or_404(
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


class DynamicDelete(ProyectosMenuMixin, DeleteView):
    template_name = 'proyectos/delete.html'

    def get_object(self):
        self.model = self.model_options[self.kwargs['model']]['model']
        obj = get_object_or_404(
            self.model,
            **self.get_company_query(self.kwargs['model']),
            pk=self.kwargs['pk']
        )
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            folio = self.object.folio
        except AttributeError:
            folio = 0
        if folio:
            qs = self.model.objects.filter(**self.get_company_query(self.kwargs['model']))
            for i in qs:
                if i.folio > folio:
                    i.folio -= 1
                    i.save()
        self.object.delete()
        return HttpResponseRedirect("")


class BaseAutocompleteView(AuthenticationTestMixin, autocomplete.Select2QuerySetView):
    app_label_name = ProyectosConfig.verbose_name


class ClienteAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Cliente.objects.filter(
                cliente_name__unaccent__icontains=self.q,
                company=self.request.user.currently_at
            )
        else:
            qs = Cliente.objects.none()
        return qs


class SitioAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Sitio.objects.filter(
                sitio_name__unaccent__icontains=self.q,
                company=self.request.user.currently_at
            )
        else:
            qs = Sitio.objects.none()
        return qs


class UnitAutocomplete(BaseAutocompleteView):
    model = Units

    def get_key_words(self):
        self.key_words = {
            'unit__unaccent__icontains': self.q
        }
        return self.key_words

    def has_add_permission(self, request):
        return True

    def get_queryset(self):
        if self.q:
            qs = self.model.objects.filter(**self.get_key_words())
            return qs
        elif self.request.POST:
            return self.model.objects
