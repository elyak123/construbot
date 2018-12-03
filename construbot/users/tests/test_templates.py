from construbot.users.tests import factories as user_factories
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import tag
from . import factories
from test_plus.test import TestCase


class TestProyectsURLsCorrectTemplates(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        administrador = user_factories.GroupFactory(name="Administrators")
        proyectos = user_factories.GroupFactory(name="Proyectos")
        users = user_factories.GroupFactory(name="Users")
        for group in administrador, proyectos, users:
            self.user.groups.add(group)
        self.user.company.add(company_test)
        self.user.currently_at = company_test

    def test_user_list(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_test)
        self.user2 = self.make_user(username="some")
        self.user2.company.add(company_test)
        self.user.currently_at = company_test
        self.user.save()
        self.user2.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertTemplateUsed(response, 'users/user_list.html')

    def test_user_detail(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:detail'))
        self.assertTemplateUsed(response, 'users/user_detail.html')
