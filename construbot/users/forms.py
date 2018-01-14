from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = [
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
