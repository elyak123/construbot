from django.views.generic import ListView
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato


# Create your views here.
class ContratoListView(AuthenticationTestMixin, ListView):
    app_label_name = ProyectosConfig.verbose_name
    model = Contrato
    template_name = 'proyectos/listado_de_contratos.html'
    context_object_name = 'contratos'
    paginate_by = 2

    # def get_queryset(self):
    #     return self.model.objects.filter(company=self.request.user.currently_at)
