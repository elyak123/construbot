from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.db.models import Max
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato
from .forms import ContratoForm


# Create your views here.
class ContratoListView(AuthenticationTestMixin, ListView):
    app_label_name = ProyectosConfig.verbose_name
    model = Contrato
    template_name = 'proyectos/listado_de_contratos.html'
    context_object_name = 'contratos'
    paginate_by = 2
    ordering = '-fecha'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(cliente__company=self.request.user.currently_at)
        return super(ContratoListView, self).get_queryset()


class ContratoDetailView(AuthenticationTestMixin, DetailView):
    app_label_name = ProyectosConfig.verbose_name
    model = Contrato
    context_object_name = 'contrato'
    template_name = 'proyectos/detalle_de_contrato.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Contrato, id=self.kwargs['pk'])


class ContratoCreationView(AuthenticationTestMixin, CreateView):
    app_label_name = ProyectosConfig.verbose_name
    form_class = ContratoForm
    # provisional.... obviamente....
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
