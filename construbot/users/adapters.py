from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import Customer, NivelAcceso


class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        new_customer = Customer.objects.create()
        user.customer = new_customer
        nivel_acceso, nivel_created = NivelAcceso.objects.get_or_create(nivel=4)
        user.nivel_acceso = nivel_acceso
        return super(AccountAdapter, self).save_user(request, user, form, commit=True)

    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)  # pragma: no cover


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)  # pragma: no cover
