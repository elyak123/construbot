from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db.models.functions import Lower
from django.http import JsonResponse
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
            'ordering': '-fecha',
        },
        'Cliente': {
            'ordering': 'cliente_name',
        },
        'Sitio': {
            'ordering': 'sitio_name',
        },
        'Destinatario': {
            'ordering': 'destinatario_text',
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
        self.queryset = self.model.objects.filter(**self.get_company_query(self.model.__name__))
        return super(DynamicList, self).get_queryset()

    def get_ordering(self):
        self.ordering = self.model_options[self.model.__name__]['ordering']
        return self.ordering


class DynamicDetail(ProyectosMenuMixin, DetailView):
    def get_context_object_name(self):
        return Lower(self.model.__name__)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'], **self.get_company_query(self.model.__name__))


class ContratoListView(DynamicList):
    model = Contrato


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

"""
    class BasicCreationView(ProyectosMenuMixin, CreateView):
        def get_initial(self):
            initial_obj = super(ClienteCreationView, self).get_initial()
            initial_obj['company'] = self.request.user.currently_at
            return initial_obj

        def form_valid(self, form):
            if form.cleaned_data['company'] == self.request.user.currently_at:
                self.object = form.save()
                return super(ClienteCreationView, self).form_valid(form)
            else:
                return super(ClienteCreationView, self).form_invalid(form)
"""


# class ClienteCreationView(BasicCreationView):
class ClienteCreationView(ProyectosMenuMixin, CreateView):
    form_class = ClienteForm
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(ClienteCreationView, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            self.object = form.save()
            return super(ClienteCreationView, self).form_valid(form)
        else:
            return super(ClienteCreationView, self).form_invalid(form)


# class SitioCreationView(BasicCreationView):
class SitioCreationView(ProyectosMenuMixin, CreateView):
    form_class = SitioForm
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(SitioCreationView, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            self.object = form.save()
            return super(SitioCreationView, self).form_valid(form)
        else:
            return super(SitioCreationView, self).form_invalid(form)


class DestinatarioCreationView(ProyectosMenuMixin, CreateView):
    form_class = DestinatarioForm
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(DestinatarioCreationView, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            self.object = form.save()
            return super(DestinatarioCreationView, self).form_valid(form)
        else:
            return super(DestinatarioCreationView, self).form_invalid(form)


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


class ClienteEditView(ProyectosMenuMixin, UpdateView):
    form_class = ClienteForm
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            Cliente,
            pk=self.kwargs['pk'],
            company=self.request.user.currently_at,
        )
        return obj

    def get_initial(self):
        initial_obj = super(ClienteEditView, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            self.object = form.save()
            return super(ClienteEditView, self).form_valid(form)
        else:
            return super(ClienteEditView, self).form_invalid(form)


class SitioEditView(ProyectosMenuMixin, UpdateView):
    form_class = SitioForm
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            Sitio,
            pk=self.kwargs['pk'],
            company=self.request.user.currently_at,
        )
        return obj

    def get_initial(self):
        initial_obj = super(SitioEditView, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            self.object = form.save()
            return super(SitioEditView, self).form_valid(form)
        else:
            return super(SitioEditView, self).form_invalid(form)


class DestinatarioEditView(ProyectosMenuMixin, UpdateView):
    form_class = DestinatarioForm
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            Destinatario,
            pk=self.kwargs['pk'],
            company=self.request.user.currently_at,
        )
        return obj

    def get_initial(self):
        initial_obj = super(DestinatarioEditView, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            self.object = form.save()
            return super(DestinatarioEditView, self).form_valid(form)
        else:
            return super(DestinatarioEditView, self).form_invalid(form)


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
