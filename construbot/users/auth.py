from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from core.context import ContextManager


class AuthenticationTestMixin(UserPassesTestMixin, ContextManager):

    login_url = 'login'
    tengo_que_ser_admin = False

    def test_func(self):
        self.current_user = self.request.user

        if self.current_user.company.exists():
            if not self.current_user.currently_at:
                self.current_user.currently_at = self.current_user.company.first()
                self.current_user.save()
        else:
            raise AttributeError('Current User must have company')

        self.user_groups = [x.name.lower() for x in self.current_user.groups.all()]
        self.user_pass = self.current_user.is_authenticated
        self.permiso_administracion = self.auth_admin()
        self.debo_ser_admin = self.get_tengo_que_ser_admin()
        if self.user_pass:
            if self.debo_ser_admin and not self.permiso_administracion:
                raise PermissionDenied
            elif self.app_label_name.lower() in self.user_groups:
                return True
            else:
                raise PermissionDenied
        else:
            return False

    def auth_admin(self):
        return self.current_user.is_administrator()

    def get_context_data(self, **kwargs):
        context = super(AuthenticationTestMixin, self).get_context_data(**kwargs)
        context['current_user'] = self.current_user
        context['user_pass'] = self.user_pass
        context['is_administrador'] = self.permiso_administracion
        return context

    def get_tengo_que_ser_admin(self):
        return self.tengo_que_ser_admin
