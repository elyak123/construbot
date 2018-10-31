# from django import forms
from django import forms
from django.forms import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from .models import Company
from dal import autocomplete

User = get_user_model()


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
        user = super(UsuarioInterno, self).save(commit=True)
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

        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'groups': 'Grupos de trabajo',
            'company': 'Compañías de trabajo',
            'password1': 'Contraseña',
            'password2': 'Confirme Contraseña'
        }


        widgets = {
            'customer': forms.HiddenInput(),
            'company': autocomplete.ModelSelect2Multiple(
                url='proyectos:company-autocomplete',
                attrs={
                    'data-minimum-input-length': 3,
                }
            ),
        }


class UsuarioEdit(UserChangeForm):

    def __init__(self, user, *args, **kwargs):
        super(UsuarioEdit, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = User
        exclude = [
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

        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'groups': 'Grupos de trabajo',
            'company': 'Compañías de trabajo',
        }

        widgets = {
            'password': forms.HiddenInput(),
            'customer': forms.HiddenInput(),
            'company': autocomplete.ModelSelect2Multiple(
                url='proyectos:company-autocomplete',
                attrs={
                    'data-minimum-input-length': 3,
                }
            ),
        }

    def clean_groups(self):
        l_groups = self.data.getlist('groups')
        customer = self.user.customer
        numero_admins = User.objects.filter(customer=customer, groups__name='Administrators').count()
        group = Group.objects.get(name='Administrators').id
        if numero_admins == 1 and (str(group) not in l_groups and self.user.is_administrator()):
            raise ValidationError('¡No puedes quedarte sin administradores!')
        return l_groups


class UsuarioEditNoAdmin(UserChangeForm):
    class Meta:
        model = User
        exclude = [
            'groups',
            'company',
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
            'password': forms.HiddenInput(),
            'customer': forms.HiddenInput(),
            'company': autocomplete.ModelSelect2Multiple(
                url='proyectos:company-autocomplete',
                attrs={
                    'data-minimum-input-length': 3,
                }
            ),
        }


class CompanyForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'full_name': 'Nombre de la compañía',
            'company_name': 'Nombre corto'
        }
        widgets = {
            'customer': forms.HiddenInput(),
        }

    def save(self):
        company = super(CompanyForm, self).save()
        self.user.company.add(company.id)
        return company


class CompanyEditForm(forms.ModelForm):
    is_new = forms.BooleanField(
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'full_name': 'Nombre de la compañía',
            'company_name': 'Nombre corto'
        }
        widgets = {
            'customer': forms.HiddenInput(),
        }
