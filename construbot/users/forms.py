# from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User


class UserForm(UserCreationForm):
    company = forms.CharField(
        label=_('Empresa Principal'),
        help_text=_('Para comenzar necesitamos una empresa en la cual trabajar.')
    )

    def signup(self, request, user):
        pass

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
