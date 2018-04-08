from django.views.generic import ListView, CreateView
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

    def get_queryset(self):
        return self.model.objects.filter(
                cliente__company=self.request.user.currently_at
            ).order_by('-fecha')


class ContratoCreationView(AuthenticationTestMixin, CreateView):
    app_label_name = ProyectosConfig.verbose_name
    form_class = ContratoForm
    # provisional.... obviamente....
    template_name = 'users/user_form.html'

    def get_initial(self):
        initial_obj = super(ContratoCreationView, self).get_initial()
        max_id = self.form_class.Meta.model.objects.filter(
            cliente__company=self.request.user.currently_at
        ).aggregate(Max('folio'))['folio__max'] or 0
        max_id += 1
        initial_obj['folio'] = max_id
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['currently_at'] == self.current_user.currently_at.company_name:
            self.object = form.save()
            return super(ContratoCreationView, self).form_valid(form)
        else:
            return super(ContratoCreationView, self).form_invalid(form)
