from django import forms
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
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
        user.company.add(empresa)
        user.groups.add(user_group)
        user.groups.add(proyectos_groups)

    class Meta:
        model = User
        exclude = [
            'is_new',
            'openpay',
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
            'nivel_acceso',
        ]


class UsuarioInterno(UserCreationForm):

    def __init__(self, user, *args, **kwargs):
        super(UsuarioInterno, self).__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(customer=user.customer)

    def save(self, commit=True):
        user = super(UsuarioInterno, self).save(commit=True)
        self._save_m2m()
        return user

    def clean_groups(self):
        n_acceso = self.data['nivel_acceso']
        user_group, created = Group.objects.get_or_create(name='Users')
        proyectos_groups, proy_created = Group.objects.get_or_create(name='Proyectos')
        if int(n_acceso) >= 3:
            return [user_group.id, proyectos_groups.id]
        return [proyectos_groups.id]

    class Meta:
        model = User
        exclude = [
            'is_new',
            'openpay',
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
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'first_name': 'Nombres del usuario, es necesario para impresión de estimaciones.',
            'last_name': 'Apellidos del usuario, es necesario para la impresión de estimaciones.',
            'company': 'Compañías de trabajo, ¿A qué compañías podrá tener acceso?',
        }
        widgets = {
            'groups': forms.HiddenInput(),
            'customer': forms.HiddenInput(),
            'nivel_acceso': autocomplete.ModelSelect2(
                url='proyectos:nivelacceso-autocomplete'
            ),
            'company': autocomplete.ModelSelect2Multiple(
                url='proyectos:company-autocomplete',
                attrs={
                    'data-minimum-input-length': 3,
                }
            ),
        }


class UsuarioEdit(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            'Las contraseñas no se almacenan en texto plano, así '
            'que no hay manera de ver la contraseña del usuario, pero se puede '
            'cambiar la contraseña mediante este '
            '<a href="{}">formulario</a>.'
        ),
    )

    def __init__(self, user, admin, *args, **kwargs):
        # Llamamos el super del padre porque el padre cambia arbitrariamente la url
        # de cambio de contraseña
        super(UserChangeForm, self).__init__(*args, **kwargs)
        pass_change = reverse('account_change_password', kwargs={'username': user.username})
        self.fields['company'].queryset = admin.company.all()
        self.fields['password'].help_text = self.fields['password'].help_text.format(pass_change)
        self.user = user

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'company',
            'email',
            'nivel_acceso'
        ]

        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'company': 'Compañías de trabajo',
            'nivel_acceso': 'Nivel de Acceso'
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'first_name': 'Nombres del usuario, es necesario para impresión de estimaciones.',
            'last_name': 'Apellidos del usuario, es necesario para la impresión de estimaciones.',
            'company': 'Compañías de trabajo, ¿A qué compañías podrá tener acceso?',
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


class UsuarioEditNoAdmin(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        ]
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'first_name': 'Nombres del usuario, es necesario para impresión de estimaciones.',
            'last_name': 'Apellidos del usuario, es necesario para la impresión de estimaciones.',
            'company': 'Compañías de trabajo, ¿A qué compañías podrá tener acceso?',
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


class CompanyForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'full_name': 'Razón Social',
            'company_name': 'Nombre de la Compañía'
        }
        help_texts = {
            'full_name': 'Razón social de la empresa de trabajo, es necesaria para mostrarlo en los documentos impresos.',
            'company_name': 'Nombre corto de la empresa, con la cual sea más sencillo identificarla.',
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
        required=False
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
