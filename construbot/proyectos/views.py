from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato


# Create your views here.
class ContratoListView(AuthenticationTestMixin, ListView):
    app_label_name = ProyectosConfig.verbose_name
    model = Contrato
    template_name = 'proyectos/listado_de_contratos.html'
    context_object_name = 'contratos'
    paginate_by = 4

    def get_queryset(self):
        model = self.model.objects.filter(cliente__company=self.request.user.currently_at).order_by('-fecha')
        return model


class ContratoDetailView(AuthenticationTestMixin, DetailView):
    app_label_name = ProyectosConfig.verbose_name
    model = Contrato
    context_object_name = 'contrato'
    template_name = 'proyectos/detalle_de_contrato.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Contrato, id=self.kwargs['pk'])
