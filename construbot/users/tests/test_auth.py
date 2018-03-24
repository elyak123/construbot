from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import Group
from test_plus.test import TestCase
from construbot.users.auth import AuthenticationTestMixin
from . import factories


class AuthTest(TestCase):
    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()

    def test_user_no_company_raises_error(self):
        auth = AuthenticationTestMixin()
        request = self.factory.get('bla/bla')
        request.user = self.user
        auth.request = request
        with self.assertRaises(AttributeError):
            auth.test_func()
