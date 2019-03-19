from unittest import mock
from django.core.exceptions import PermissionDenied
from django.test import override_settings, tag
from construbot.users.tests import factories
from construbot.proyectos.tests.test_proyectos_views import BaseViewTest
from construbot.account_config import views


class _LoginViewTest(BaseViewTest):

    @override_settings(ACCOUNT_ALLOW_REGISTRATION='hola')
    def test_loginview_context_obeys_settings(self):
        view = self.get_instance(
            views._LoginView,
            request=self.request,
        )
        context = view.get_context_data()
        self.assertEqual(context['allow_register'], 'hola')


class _PasswordChangeViewTest(BaseViewTest):

    def setUp(self):
        super(_PasswordChangeViewTest, self).setUp()
        self.view = self.get_instance(
            views._PasswordChangeView,
            request=self.request,
        )

    def test_get_nivel_permiso_for_auxiliar(self):
        self.view.nivel_permiso_usuario = self.user.nivel_acceso.nivel
        permiso = self.view.get_nivel_permiso()
        self.assertEqual(permiso, 1)

    def test_get_nivel_permiso_for_auxiliar_for_other_user(self):
        view = self.get_instance(
            views._PasswordChangeView,
            request=self.request,
            username='other_username'
        )
        view.permiso_usuario = self.user.nivel_acceso.nivel
        permiso = view.get_nivel_permiso()
        self.assertEqual(permiso, 3)

    @mock.patch('allauth.account.views.AjaxCapableProcessFormViewMixin.get')
    @mock.patch.object(views._PasswordChangeView, 'test_func')
    @mock.patch.object(views._PasswordChangeView, 'check_obj_permissions')
    @mock.patch.object(views._PasswordChangeView, 'get_object')
    def test_get_executes_functions(self, get_object, obj_permissions, test_func, mock_get):
        test_func.return_value = True
        self.view.nivel_permiso_vista = 1
        mock_object = mock.MagicMock()
        get_object.return_value = mock_object
        self.view.get(self.request)
        get_object.assert_called_once_with()
        obj_permissions.assert_called_once_with(mock_object)

    @mock.patch('allauth.account.views.AjaxCapableProcessFormViewMixin.post')
    @mock.patch.object(views._PasswordChangeView, 'test_func')
    @mock.patch.object(views._PasswordChangeView, 'check_obj_permissions')
    @mock.patch.object(views._PasswordChangeView, 'get_object')
    def test_post_executes_functions(self, get_object, obj_permissions, test_func, mock_post):
        test_func.return_value = True
        self.view.nivel_permiso_vista = 1
        mock_object = mock.MagicMock()
        get_object.return_value = mock_object
        self.view.post(self.request)
        get_object.assert_called_once_with()
        obj_permissions.assert_called_once_with(mock_object)

    def test_get_object(self):
        obj = self.view.get_object()
        self.assertEqual(obj, self.user)

    def test_get_object_with_username(self):
        other_user = factories.UserFactory(nivel_acceso=self.auxiliar_permission)
        view = self.get_instance(
            views._PasswordChangeView,
            request=self.request,
            username=other_user.username
        )
        obj = view.get_object()
        self.assertEqual(obj, other_user)
        self.assertNotEqual(obj, self.user)

    def test_check_obj_permissions_same_user(self):
        func = self.view.check_obj_permissions
        self.assertNotRaises(lambda: func(self.user), PermissionDenied, 'Permiso incorrecto en la vista')

    def test_check_obj_permissions_other_user(self):
        other_user = factories.UserFactory(nivel_acceso=self.auxiliar_permission, customer=self.user.customer)
        func = self.view.check_obj_permissions
        self.assertNotRaises(lambda: func(other_user), PermissionDenied, 'Permiso incorrecto en la vista')

    def test_check_obj_permissions_other_user_nivel_soporte(self):
        self.user.nivel_acceso = self.soporte_permission
        self.user.save()
        other_user = factories.UserFactory(nivel_acceso=self.auxiliar_permission)
        func = self.view.check_obj_permissions
        self.assertNotRaises(lambda: func(other_user), PermissionDenied, 'Permiso incorrecto en la vista')

    def test_check_obj_permissions_other_user_other_customer(self):
        other_user = factories.UserFactory(nivel_acceso=self.auxiliar_permission)
        with self.assertRaises(PermissionDenied):
            self.view.check_obj_permissions(other_user)

    def test_get_form_class(self):
        self.view.nivel_permiso_vista = 2
        form_class = self.view.get_form_class()
        self.assertEqual(form_class, views.ChangePasswordForm)

    def test_get_form_class_nivel_tres(self):
        self.view.nivel_permiso_vista = 3
        form_class = self.view.get_form_class()
        self.assertEqual(form_class, views.SetPasswordForm)

    def test_get_form_kw(self):
        mock_user = mock.Mock()
        self.view.object = mock_user
        kw = self.view.get_form_kwargs()
        self.assertEqual(mock_user, kw['user'])

    @mock.patch.object(views._PasswordChangeView, 'test_func')
    @mock.patch('construbot.users.auth.AuthenticationTestMixin.get_context_data')
    def test_get_context_data(self, mock_context, test_func):
        test_func.return_value = True
        mock_obj = mock.Mock()
        self.view.object = mock_obj
        mock_context.return_value = {}
        context = self.view.get_context_data()
        self.assertEqual(context['user'], mock_obj)

    @mock.patch('construbot.account_config.views.reverse')
    def test_get_success_url(self, mock_reverse):
        self.view.nivel_permiso_vista = 3
        mock_user = mock.Mock()
        mock_user.username = 'hola'
        self.view.object = mock_user
        self.view.get_success_url()
        mock_reverse.assert_called_once_with('users:detail', kwargs={'username': mock_user.username})

    @mock.patch('construbot.account_config.views.reverse')
    def test_get_success_url_director_o_menos(self, mock_reverse):
        self.view.nivel_permiso_vista = 2
        self.view.get_success_url()
        mock_reverse.assert_called_once_with('proyectos:proyect_dashboard')
