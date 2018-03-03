from construbot.users.forms import UserForm
from django.test import TestCase


class UserFormTest(TestCase):
    def test_userform_setting_is_correct(self):
        from django.conf import settings
        self.assertEqual(settings.ACCOUNT_SIGNUP_FORM_CLASS, 'construbot.users.forms.UserForm')

    def test_userform_post(self):
        form = UserForm(data={
            'email': 'bla@email.com',
            'username': 'some_name',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'password1': 'Secret 19384',
            'password2': 'Secret 19384',
            })
        self.assertTrue(form.is_valid(), 'Falta el customer')
