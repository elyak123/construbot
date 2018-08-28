from django.test import TestCase, override_settings, tag
from django.http import QueryDict
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from construbot.users import forms
from construbot.users.models import Company
from . import factories
from django.test import tag
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

    @override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
    def test_UsuarioInterno_post(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        users_group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(users_group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.user.company.add(company)
        data = {
            'customer': str(self.user.customer.id),
            'username': 'test_user_dos',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'lkjas@hola.com',
            'groups': [str(users_group.id)],
            'company': [str(company.id)],
            'password1': 'esteesunpsslargo',
            'password2': 'esteesunpsslargo'
        }
        form = forms.UsuarioInterno(self.user, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password('esteesunpsslargo'))
        self.assertTrue(authenticate(username='test_user_dos', password='esteesunpsslargo'))

class UsuarioEditTest(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
    
    def test_UsusarioEdit_post(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        users_group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(users_group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.user.company.add(company)
        qdict = QueryDict('groups={}'.format(users_group.id), mutable=True)
        data = {
            'customer': str(self.user.customer.id),
            'username': 'nuevo_test',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'lkjas@hola.com',
            'groups': str(group.id),
            'company': str(company.id),
        }
        qdict.update(data)
        form = forms.UsuarioEdit(self.user, data=qdict, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(authenticate(username='nuevo_test', password='password'))        

    def test_UsusarioEdit_group_error(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        users_group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(users_group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.user.company.add(company)
        qdict = QueryDict('', mutable=True)
        data = {
            'customer': str(self.user.customer.id),
            'username': 'nuevo_test',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'lkjas@hola.com',
            'groups': str(users_group.id),
            'company': str(company.id),
        }
        qdict.update(data)
        test_error_dict = {'groups': ['¡No puedes quedarte sin administradores!']}
        form = forms.UsuarioEdit(self.user, data=qdict, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, test_error_dict)

    def test_CompanyCreationForm(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        self.user.company.add(company)
        data = {
            'customer': self.user.customer.id,
            'full_name': 'Company Test, S.A. de C.V.',
            'company_name': 'CT S.A. de C.V.',
        }
        form = forms.CompanyForm(self.user, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        company = form.save()
        self.assertEqual(company.company_name, 'CT S.A. de C.V.')

    def test_CompanyEditForm(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        self.user.company.add(company)
        data = {
            'customer': self.user.customer.id,
            'full_name': 'Company Edit, S.A. de C.V.',
            'company_name': 'CE S.A. de C.V.',
            'is_new': True,
        }
        form = forms.CompanyEditForm(data=data, instance=company)
        self.assertTrue(form.is_valid(), form.errors)
        company = form.save()
        self.assertEqual(company.company_name, 'CE S.A. de C.V.')
