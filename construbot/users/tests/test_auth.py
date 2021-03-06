from django.test import tag
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group, AnonymousUser
from construbot.users.models import Company
from construbot.users.auth import AuthenticationTestMixin
from . import utils


class AuthTest(utils.BaseTestCase):

    def test_user_no_company_raises_error(self):
        view = self.get_instance(
            AuthenticationTestMixin,
            request=self.get_request(self.user)
        )
        with self.assertRaises(AttributeError):
            view.test_func()

    def test_user_with_company_no_curently_gets_assigned(self):
        view = self.get_instance(
            AuthenticationTestMixin,
            request=self.get_request(self.user)
        )
        company = Company.objects.create(
            company_name='A company',
            customer=self.user.customer
        )
        group = Group.objects.create(name='foo')
        view.request.user.company.add(company)
        view.request.user.groups.add(group)
        view.app_label_name = 'foo'
        view.test_func()
        self.assertEqual(company, view.request.user.currently_at)

    def test_AnonymousUser_returns_false(self):
        view = self.get_instance(
            AuthenticationTestMixin,
            request=self.get_request(AnonymousUser())
        )
        self.assertFalse(view.test_func())

    def test_user_accessing_app_not_in_groups(self):
        view = self.get_instance(
            AuthenticationTestMixin,
            request=self.get_request(self.user)
        )
        company = Company.objects.create(
            company_name='A company',
            customer=view.request.user.customer
        )
        view.request.user.company.add(company)
        view.app_label_name = 'bar'
        with self.assertRaises(PermissionDenied):
            view.test_func()

    def test_tengo_que_ser_admin_no_permiso_direccion(self):
        view = self.get_instance(
            AuthenticationTestMixin,
            request=self.get_request(self.user)
        )
        company = Company.objects.create(
            company_name='A company',
            customer=self.user.customer
        )
        group = Group.objects.create(name='bar')
        view.request.user.groups.add(group)
        view.request.user.company.add(company)
        view.permiso_requerido = 3
        view.app_label_name = 'bar'
        with self.assertRaises(PermissionDenied):
            view.test_func()

    def test_usuario_con_permiso_no_apps_permission_denied(self):
        view = self.get_instance(
            AuthenticationTestMixin,
            request=self.get_request(self.user)
        )
        view.tengo_que_ser_admin = True
        company = Company.objects.create(
            company_name='this company',
            customer=view.request.user.customer
        )
        view.request.user.groups.add(self.admin_group)
        view.request.user.company.add(company)
        view.app_label_name = 'bla'
        with self.assertRaises(PermissionDenied):
            view.test_func()
