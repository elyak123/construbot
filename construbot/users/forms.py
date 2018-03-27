# from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from .models import User, Company


class UserForm(UserCreationForm):
    company = forms.CharField(
        label=_('Empresa Principal'),
        help_text=_('Para comenzar necesitamos una empresa en la cual trabajar.')
    )

    def signup(self, request, user):
        empresa = Company.objects.create(company_name=self.cleaned_data['company'], customer=user.customer)
        user_group, created = Group.objects.get_or_create(name='Users')
        user.company.add(empresa)
        user.groups.add(user_group)

    class Meta:
        model = User
        exclude = [
            'password',
            'customer',
            'company',
            'last_login',
            'is_superuser',
            'groups',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined',
            'last_supervised',
            'currently_at',
        ]


class UsuarioInterno(UserForm):
    def signup(self, request, user):
        pass

    # def save(self, *args, **kwargs):
        # user = super(UsuarioInterno, self).get_queryset()
        # user.customer = s
        # user.company = self.current_user
        # super(user, self).save(*args, **kwargs)

    # class Meta:
    #     model = User
    #     exclude = [
    #         'password',
    #         'customer',
    #         'company',
    #         'last_login',
    #         'is_superuser',
    #         'user_permissions',
    #         'is_staff',
    #         'is_active',
    #         'date_joined',
    #         'last_supervised',
    #         'currently_at',
    #     ]
