from construbot.users.tests import factories as user_factories
<<<<<<< HEAD
from django.core.urlresolvers import reverse
=======
from django.urls import reverse
>>>>>>> 432b8adc6f2247b6794c8149615a4b25fef180f5
from django.test import tag
from . import utils


class TestProyectsURLsCorrectTemplates(utils.BaseTestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        super(TestProyectsURLsCorrectTemplates, self).setUp()
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        for group in self.admin_group, self.proyectos_group, self.user_group:
            self.user.groups.add(group)
        self.user.company.add(company_test)
        self.user.currently_at = company_test

    def test_user_list(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertTemplateUsed(response, 'users/user_list.html')

    def test_user_detail(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:detail'))
        self.assertTemplateUsed(response, 'users/user_detail.html')
