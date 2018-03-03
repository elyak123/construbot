# from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):

    def signup(self, request, user):
        # crear aqui el customer
        pass

    class Meta:
        model = User
        exclude = [
            'password',
            #'customer',
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
