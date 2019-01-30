from django.shortcuts import render
from allauth.account.views import (LoginView, SignupView, EmailView, PasswordChangeView,
    PasswordSetView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView,
    PasswordResetFromKeyDoneView, LogoutView, EmailVerificationSentView,
    AccountInactiveView, EmailView, EmailVerificationSentView, ConfirmEmailView)
from django.conf import settings


class _SignupView(SignupView):
    pass


class _LoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super(_LoginView, self).get_context_data(**kwargs)
        context['allow_register'] = settings.ACCOUNT_ALLOW_REGISTRATION
        return context


class _LogoutView(LogoutView):
    pass


class _PasswordChangeView(PasswordChangeView):
    pass


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
