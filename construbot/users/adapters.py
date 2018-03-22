from .models import Customer, Company
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        new_customer = Customer.objects.create()
        empresa = Company.objects.create(company_name=form.cleaned_data['company'], customer=new_customer)
        user.customer = new_customer
        super(AccountAdapter, self).save_user(request, user, form, commit=True)
        user.company.add(empresa)
        return user

    def get_login_redirect_url(self, request):
        super(AccountAdapter, self).get_login_redirect_url(self, request)

    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
