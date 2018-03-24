from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import Group
from test_plus.test import TestCase
from construbot.users.models import Company
from . import factories

from ..views import (
    UserRedirectView,
    UserUpdateView
)


class BaseUserTestCase(TestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()


class TestUserRedirectView(BaseUserTestCase):

    def test_get_redirect_url(self):
        # Instantiate the view directly. Never do this outside a test!
        view = UserRedirectView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        view.request = request
        # Expect: '/users/testuser/', as that is the default username for
        #   self.make_user()
        self.assertEqual(
            view.get_redirect_url(),
            '/users/testuser/'
        )


class TestUserUpdateView(BaseUserTestCase):

    def setUp(self):
        # call BaseUserTestCase.setUp()
        super(TestUserUpdateView, self).setUp()
        # Instantiate the view directly. Never do this outside a test!
        self.view = UserUpdateView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        self.view.request = request

    def test_get_success_url(self):
        # Expect: '/users/testuser/', as that is the default username for
        #   self.make_user()
        self.assertEqual(
            self.view.get_success_url(),
            '/users/testuser/'
        )

    def test_get_object(self):
        # Expect: self.user, as that is the request's user object
        self.assertEqual(
            self.view.get_object(),
            self.user
        )


class TestListUserView(BaseUserTestCase):
    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        group = Group.objects.create(name='Users')
        company = Company.objects.create(company_name='my_company', customer=self.user.customer)
        self.user.company.add(company)
        self.user.groups.add(group)

    def additional_users_different_customer(self):
        self.user1_different_customer = self.make_user(username='foreign_user')
        group, created = Group.objects.get_or_create(name='Users')
        company = Company.objects.create(company_name='another_company', customer=self.user.customer)
        self.user.company.add(company)
        self.user.groups.add(group)

    def test_list_users_renders_correctly(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertEqual(response.status_code, 200)

    def test_view_list_users_only_in_current_company(self):
        self.additional_users_different_customer()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertNotContains(response, 'foreign_user')
