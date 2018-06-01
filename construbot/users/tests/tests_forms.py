from django.test import TestCase, tag
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from construbot.users import forms
from construbot.users.models import Company
from . import factories
from . import utils


class UserFormTest(TestCase):
    def test_signup_userform_setting_is_correct(self):
        from django.conf import settings
        self.assertEqual(settings.ACCOUNT_SIGNUP_FORM_CLASS, 'construbot.users.forms.UserForm')

    def test_signup_userform_post(self):
        form = forms.UserForm(data={
            'email': 'bla@email.com',
            'username': 'some_name',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'password1': 'Secret 19384',
            'password2': 'Secret 19384',
            'company': 'Acme'
            })
        self.assertTrue(form.is_valid(), form.errors)


class UsuarioInternoTest(utils.BaseTestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
    @tag('current')
    def test_UsuarioInterno_post(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.user.company.add(company)
        data = {
            'customer': str(self.user.customer.id),
            'username': 'test_user_dos',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'lkjas@hola.com',
            'company': [str(company.id)],
            'password1': 'esteesunpsslargo',
            'password2': 'esteesunpsslargo'
        }
        form = forms.UsuarioInterno(self.user, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password('esteesunpsslargo'))
        self.assertTrue(authenticate(username='test_user_1', password='esteesunpsslargo'))
