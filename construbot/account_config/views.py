from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.account.views import (
    LoginView, SignupView, PasswordChangeView,
    PasswordSetView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView,
    PasswordResetFromKeyDoneView, LogoutView, EmailVerificationSentView,
    AccountInactiveView, EmailView, ConfirmEmailView)
from allauth.account.forms import ChangePasswordForm, SetPasswordForm
from construbot.users.auth import AuthenticationTestMixin

User = get_user_model()


class _SignupView(SignupView):
    pass


class _LoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super(_LoginView, self).get_context_data(**kwargs)
        context['allow_register'] = settings.ACCOUNT_ALLOW_REGISTRATION
        return context


class _LogoutView(LogoutView):
    pass


class _PasswordChangeView(AuthenticationTestMixin, PasswordChangeView):
    app_label_name = 'redirect'
    permiso_requerido = 3

    def get_nivel_permiso(self):
        if (self.kwargs.get('username') == self.request.user.username) or self.kwargs.get('username') is None:
            return self.nivel_permiso_usuario
        else:
            return self.permiso_requerido

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.check_obj_permissions(self.object)
        return super(_PasswordChangeView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.check_obj_permissions(self.object)
        return super(_PasswordChangeView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not self.kwargs.get('username', None):
            return self.request.user
        return User.objects.select_related('customer').get(username=self.kwargs['username'])

    def check_obj_permissions(self, obj):
        if self.request.user.customer != obj.customer and self.request.user.nivel_acceso.nivel < 5:
            raise PermissionDenied('El usuario no tiene acceso a permisos fuera de su cuenta.')

    def get_form_class(self):
        if self.nivel_permiso_vista == self.permiso_requerido:
            return SetPasswordForm
        return ChangePasswordForm

    def get_form_kwargs(self):
        kwargs = super(_PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(_PasswordChangeView, self).get_context_data(**kwargs)
        context['user'] = self.object
        return context

    def get_success_url(self):
        if self.nivel_permiso_vista == self.permiso_requerido:
            return reverse('users:detail', kwargs={'username': self.object.username})
        return reverse('proyectos:proyect_dashboard')


class _PasswordSetView(PasswordSetView):
    pass


class _PasswordResetView(PasswordResetView):
    pass


class _PasswordResetDoneView(PasswordResetDoneView):
    pass


class _PasswordResetFromKeyView(PasswordResetFromKeyView):
    pass


class _PasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    pass


class _AccountInactiveView(AccountInactiveView):
    pass


class _EmailView(EmailView):
    pass


class _EmailVerificationSentView(EmailVerificationSentView):
    pass


class _ConfirmEmailView(ConfirmEmailView):
    pass
