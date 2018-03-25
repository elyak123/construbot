from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.conf import settings
from core.context import ContextManager


class AuthenticationTestMixin(UserPassesTestMixin, ContextManager):

    login_url = settings.LOGIN_URL
    tengo_que_ser_admin = False

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
        self.permiso_administracion = self.auth_admin()
        self.debo_ser_admin = self.get_tengo_que_ser_admin()
        if self.debo_ser_admin and not self.permiso_administracion:
            raise PermissionDenied
        elif self.app_label_name.lower() in self.user_groups:
            return True
        else:
            raise PermissionDenied

    def auth_admin(self):
        return self.request.user.is_administrator()

    def get_context_data(self, **kwargs):
        context = super(AuthenticationTestMixin, self).get_context_data(**kwargs)
        context['current_user'] = self.request.user
        context['user_pass'] = self.request.user.is_authenticated
        context['is_administrador'] = self.permiso_administracion
        return context

    def get_tengo_que_ser_admin(self):
        return self.tengo_que_ser_admin
