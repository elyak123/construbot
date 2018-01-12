from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from accounts.models import ExtendUser

class UserForm(UserChangeForm):
    class Meta:
        model  = ExtendUser
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'groups'
        ]

class UserCreationForm(UserCreationForm):
    class Meta:
        model = ExtendUser
        fields = [
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'email',
            'groups',
            'company',
            'customer',
            'currently_at',
        ]
        
        labels = {
            'username'  : 'Nombre del usuario',
            'first_name': 'Nombre(s)',
            'last_name' : 'Apellido(s)',
            'email'     : 'Correo electrónico (opcional)',
            'password1' : 'Contraseña',
            'password2' : 'Confirma contraseña',
            'groups'    : 'Aplicaciones en los que va a trabajar'
        }
        widgets = {
            'password1' : forms.PasswordInput(),
            'password2' : forms.PasswordInput()
        }
        help_texts = {
            'company': 'Selecciona las compañías a las que el usuario tendrá acceso, (mantén pulsado Control o CMD para seleccionar más de una).',
        }

class NoAdminUserForm(UserForm):
    class Meta:
        model  = ExtendUser
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'customer',
            'currently_at',
        ]
        labels = {
            'company' : 'Compañía(s) de trabajo, (mantén pulsado Control o CMD para seleccionar más de una).',
        }
        widgets = {
            'user'    : forms.HiddenInput(),
            'customer': forms.HiddenInput(),
        }
