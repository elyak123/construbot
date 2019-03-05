from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.conf import settings
from construbot.core.context import ContextManager


class AuthenticationTestMixin(UserPassesTestMixin, ContextManager):

    login_url = settings.LOGIN_URL
    permiso_requerido = 1
    asignacion_requerida = False
    change_company_ability = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.company.exists():
            if not self.request.user.currently_at:
                self.request.user.currently_at = self.request.user.company.first()
                self.request.user.save()
        else:
            raise AttributeError('Current User must have company')
        self.user_groups = [x.name.lower() for x in self.request.user.groups.all()]
        redirect_label = ['redirect']
        self.user_groups = self.user_groups + redirect_label
        self.nivel_permiso_usuario = self.auth_access()
        self.nivel_permiso_vista = self.get_nivel_permiso()
        if self.app_label_name.lower() in self.user_groups and self.nivel_permiso_usuario >= self.nivel_permiso_vista:
            return True
        else:
            raise PermissionDenied(
                'El usuario {} no tiene permiso para ver esta página.'.format(self.request.user.username)
            )

    def auth_access(self):
        return self.request.user.nivel_acceso.nivel

    def get_context_data(self, **kwargs):
        context = super(AuthenticationTestMixin, self).get_context_data(**kwargs)
        context['current_user'] = self.request.user
        context['user_pass'] = self.request.user.is_authenticated
        context['almenos_coordinador'] = self.nivel_permiso_usuario >= 2
        context['almenos_director'] = self.nivel_permiso_usuario >= 3
        context['almenos_corporativo'] = self.nivel_permiso_usuario >= 4
        context['puedo_cambiar'] = self.get_change_company_ability()
        return context

    def enforce_assignment(self, obj, qs):
        if obj in qs:
            return self.nivel_permiso_asignado if hasattr(self, 'nivel_permiso_asignado') else self.nivel_permiso_usuario
        return self.permiso_requerido

    def get_assignment_args(self):
        raise ImproperlyConfigured('Es necesario sobre escribir el metodo para que pueda funcionar')

    def get_nivel_permiso(self):
        if self.asignacion_requerida:
            return self.enforce_assignment(*self.get_assignment_args())
        else:
            return self.permiso_requerido

    def get_change_company_ability(self):
        return self.change_company_ability
