from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.db.models import Max
from dal import autocomplete
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato, Cliente, Sitio
from .forms import ContratoForm, ClienteForm, SitioForm


class ProyectosMenuMixin(AuthenticationTestMixin):
    app_label_name = ProyectosConfig.verbose_name
    menu_specific = [
        {
            'title': 'Catalogos',
            'url': '',
            'icon': '',
            'parent': True,
            'li_type': 'li_submenu',
            'a_type': 'anchor_menu_subitem',
            'submenu': [
                {
                    'title': 'Contratos',
                    'url': 'construbot.proyectos:listado_de_contratos',
                    'urlkwargs': '',
                    'icon': '',
                },
                {
                    'title': 'Clientes',
                    'url': 'construbot.proyectos:listado_de_clientes',
                    'urlkwargs': '',
                    'icon': '',
                },
                {
                    'title': 'Ubicaciones',
                    'url': 'construbot.proyectos:listado_de_sitios',
                    'urlkwargs': '',
                    'icon': '',
                },
                {
                    'title': 'Contactos',
                    'url': '',
                    'urlkwargs': '',
                    'icon': '',
                },
            ],
        }
    ]


# Create your views here.
class ContratoListView(ProyectosMenuMixin, ListView):
    model = Contrato
    paginate_by = 10
    ordering = '-fecha'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            cliente__company=self.request.user.currently_at
        )
        return super(ContratoListView, self).get_queryset()


class ClienteListView(ProyectosMenuMixin, ListView):
    model = Cliente
    paginate_by = 10
    ordering = 'cliente_name'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            company=self.request.user.currently_at
        )
        return super(ClienteListView, self).get_queryset()


class SitioListView(ProyectosMenuMixin, ListView):
    model = Sitio
    paginate_by = 10
    ordering = 'sitio_name'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            company=self.request.user.currently_at
        )
        return super(SitioListView, self).get_queryset()


class ContratoDetailView(ProyectosMenuMixin, DetailView):
    model = Contrato
    context_object_name = 'contrato'
    template_name = 'proyectos/detalle_de_contrato.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Contrato, pk=self.kwargs['pk'])


class ClienteDetailView(ProyectosMenuMixin, DetailView):
    model = Cliente
    context_object_name = 'cliente'
    template_name = 'proyectos/detalle_de_cliente.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Cliente, pk=self.kwargs['pk'])


class SitioDetailView(ProyectosMenuMixin, DetailView):
    model = Sitio
    context_object_name = 'sitio'
    template_name = 'proyectos/detalle_de_sitio.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Sitio, pk=self.kwargs['pk'])


class ContratoCreationView(ProyectosMenuMixin, CreateView):
    form_class = ContratoForm
    template_name = 'proyectos/contrato_form.html'

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
            self.object = form.save()
            return super(ContratoCreationView, self).form_valid(form)
        else:
            return super(ContratoCreationView, self).form_invalid(form)


class ClienteCreationView(ProyectosMenuMixin, CreateView):
    form_class = ClienteForm
    template_name = 'proyectos/contrato_form.html'

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


class SitioCreationView(ProyectosMenuMixin, CreateView):
    form_class = SitioForm
    template_name = 'proyectos/contrato_form.html'

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


class BaseAutocompleteView(AuthenticationTestMixin, autocomplete.Select2QuerySetView):
    app_label_name = ProyectosConfig.verbose_name


class ClienteAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Cliente.objects.filter(
                cliente_name__icontains=self.q,
                company=self.request.user.currently_at
            )
            return qs
        else:
            qs = Cliente.objects.none()


class SitioAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Sitio.objects.filter(
                sitio_name__icontains=self.q,
                company=self.request.user.currently_at
            )
            return qs
        else:
            qs = Sitio.objects.none()
