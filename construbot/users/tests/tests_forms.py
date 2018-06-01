from django.test import TestCase
from construbot.users.forms import UserForm
from construbot.users.models import Company


class UserFormTest(TestCase):
    def test_signup_userform_setting_is_correct(self):
        from django.conf import settings
        self.assertEqual(settings.ACCOUNT_SIGNUP_FORM_CLASS, 'construbot.users.forms.UserForm')

    def test_signup_userform_post(self):
        form = UserForm(data={
            'email': 'bla@email.com',
            'username': 'some_name',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'password1': 'Secret 19384',
            'password2': 'Secret 19384',
            'company': 'Acme'
            })
        self.assertTrue(form.is_valid(), form.errors)


# class UsuarioInternoTest(TestCase):
#     def test_(self):
#         pass
