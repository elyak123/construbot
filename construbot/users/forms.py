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
        proyectos_groups, proy_created = Group.objects.get_or_create(name='Proyectos')
        admin_group, admin_created = Group.objects.get_or_create(name='Administrators')
        user.company.add(empresa)
        user.groups.add(user_group)
        user.groups.add(proyectos_groups)
        user.groups.add(admin_group)

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
            'name',
        ]


class UsuarioInterno(UserCreationForm):

    def __init__(self, user, *args, **kwargs):
        super(UsuarioInterno, self).__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(customer=user.customer)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=True)
        self._save_m2m()
        return user

    class Meta:
        model = User
        exclude = [
            'password',
            'last_login',
            'is_superuser',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined',
            'last_supervised',
            'currently_at',
            'name',
        ]

        widgets = {
            'customer': forms.HiddenInput(),
        }
