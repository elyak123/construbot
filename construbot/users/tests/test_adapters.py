# from unittest import skip
# from django.test import tag
from test_plus.test import TestCase
from django.urls import reverse
from construbot.users.models import Company
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from . import factories

User = get_user_model()


class AccountAdapterTest(TestCase):

    def test_singup_correct_requirements(self):
        with self.settings(ACCOUNT_EMAIL_VERIFICATION='none'):
            self.client.post(reverse('account_signup'), data={
                'email': 'bla@example.com',
                'username': 'Joe',
                'password1': 'super_secret',
                'password2': 'super_secret',
                'first_name': 'Joe',
                'last_name': 'Doe',
                'company': 'My own company',
            }, follow=True)
            user = User.objects.get(username='Joe')
            self.assertIn('My own company', [x.company_name for x in user.company.all()])

    def test_singup_correct_and_redirects(self):
        with self.settings(ACCOUNT_EMAIL_VERIFICATION='none'):
            response = self.client.post(reverse('account_signup'), data={
                'email': 'bla@example.com',
                'username': 'Joe',
                'password1': 'super_secret',
                'password2': 'super_secret',
                'first_name': 'Joe',
                'last_name': 'Doe',
                'company': 'My own company',
            }, follow=True)
            self.assertRedirects(response, reverse('proyectos:proyect_dashboard'))


class LoginAccountTest(TestCase):
    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        group = Group.objects.create(name='Users')
        company = Company.objects.create(company_name='my_company', customer=self.user.customer)
        self.user.company.add(company)
        self.user.groups.add(group)
        group = Group.objects.create(name='Administrators')
        group_projects = Group.objects.create(name='Proyectos')
        self.user.groups.add(group_projects)
        self.user.groups.add(group)

    def test_login_successful(self):
        with self.settings(ACCOUNT_EMAIL_VERIFICATION='none'):
            self.client.login(username=self.user.username, password='password')
            response = self.client.get(reverse('account_login'), follow=True)
            self.assertRedirects(response, reverse('proyectos:proyect_dashboard'))
