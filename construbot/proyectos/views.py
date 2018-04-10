from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.db.models import Max
from dal import autocomplete
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato, Cliente, Sitio
from .forms import ContratoForm


class ProyectosMenuMixin(AuthenticationTestMixin):
    app_label_name = ProyectosConfig.verbose_name
    menu_specific = [
        {
            'title': 'Catalogos',
            'url': '',
            'icon': '',
            'parent': True,
            'type': 'submenu',
            'submenu': [
                {
                    'title': 'Contratos',
                    'url': 'construbot.proyectos:listado_de_contratos',
                    'urlkwargs': '',
                    'icon': '',
                },
                {
                    'title': 'Clientes',
                    'url': '',
                    'urlkwargs': '',
                    'icon': '',
                },
                {
                    'title': 'Ubicaciones',
                    'url': '',
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
    template_name = 'proyectos/listado_de_contratos.html'
    context_object_name = 'contratos'
    paginate_by = 2
    ordering = '-fecha'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
                            cliente__company=self.request.user.currently_at
                        )
        return super(ContratoListView, self).get_queryset()


class ContratoDetailView(ProyectosMenuMixin, DetailView):
    model = Contrato
    context_object_name = 'contrato'
    template_name = 'proyectos/detalle_de_contrato.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Contrato, pk=self.kwargs['pk'])


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

    def get_success_url(self):
        return reverse('construbot.proyectos:listado_de_contratos')


class BaseAutocompleteView(AuthenticationTestMixin, autocomplete.Select2QuerySetView):
    app_label_name = ProyectosConfig.verbose_name

class ClienteAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Cliente.objects.filter(cliente_name__icontains=self.q, company=self.request.user.currently_at)
            return qs
        else:
            qs = Cliente.objects.none()


class SitioAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Sitio.objects.filter(sitio_name__icontains=self.q, company=self.request.user.currently_at)
            return qs
        else:
            qs = Sitio.objects.none()
