from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group, AnonymousUser
from test_plus.test import TestCase
from construbot.users.models import Company
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

    def test_user_with_company_no_curently_gets_assigned(self):
        company = Company.objects.create(company_name='A company', customer=self.user.customer)
        self.user.company.add(company)
        auth = AuthenticationTestMixin()
        request = self.factory.get('bla/bla')
        request.user = self.user
        group = Group.objects.create(name='foo')
        request.user.groups.add(group)
        auth.request = request
        auth.app_label_name = 'foo'
        auth.test_func()
        self.assertEqual(company, self.user.currently_at)

    def test_AnonymousUser_returns_false(self):
        auth = AuthenticationTestMixin()
        request = self.factory.get('bla/bla')
        request.user = AnonymousUser()
        auth.request = request
        self.assertFalse(auth.test_func())

    def test_user_accessing_app_not_in_groups(self):
        company = Company.objects.create(company_name='A company', customer=self.user.customer)
        self.user.company.add(company)
        auth = AuthenticationTestMixin()
        request = self.factory.get('bla/bla')
        request.user = self.user
        auth.request = request
        auth.app_label_name = 'bar'
        with self.assertRaises(PermissionDenied):
            auth.test_func()

    def test_tengo_que_ser_admin_no_permiso_administracion(self):
        company = Company.objects.create(company_name='A company', customer=self.user.customer)
        self.user.company.add(company)
        auth = AuthenticationTestMixin()
        auth.tengo_que_ser_admin = True
        request = self.factory.get('bla/bla')
        request.user = self.user
        auth.request = request
        auth.app_label_name = 'bar'
        with self.assertRaises(PermissionDenied):
            auth.test_func()
