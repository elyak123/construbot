from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.conf import settings
from construbot.core.context import ContextManager
from django.shortcuts import redirect
from django.urls import reverse


class AuthenticationTestMixin(UserPassesTestMixin, ContextManager):

    login_url = settings.LOGIN_URL
    tengo_que_ser_admin = False
    change_company_ability = True

    def test_func(self):
        actual_usr = self.request.user
        UUID = settings.UUID
        if not actual_usr.is_authenticated:
            return False
        if actual_usr.company.exists():
            if not actual_usr.currently_at:
                actual_usr.currently_at = actual_usr.company.first()
                actual_usr.save()
        else:
            raise AttributeError('Current User must have company')
        self.user_groups = [x.name.lower() for x in actual_usr.groups.all()]
        self.permiso_administracion = self.auth_admin()
        self.debo_ser_admin = self.get_tengo_que_ser_admin()
        if UUID in actual_usr.username or UUID in actual_usr.currently_at.company_name:
            import pdb; pdb.set_trace()
            return redirect(reverse('users:create_username_and_company_name'))
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
        context['puedo_cambiar'] = self.get_change_company_ability()
        return context

    def get_tengo_que_ser_admin(self):
        return self.tengo_que_ser_admin

    def get_change_company_ability(self):
        return self.change_company_ability
