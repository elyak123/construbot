from unittest import mock
from django.core.exceptions import PermissionDenied
from django.test import override_settings, tag
from django.urls import reverse
from construbot.users.models import Company
from . import factories
from . import utils

from ..views import (
    UserRedirectView,
    UserUpdateView, UserDetailView,
    UserCreateView, CompanyCreateView,
    CompanyEditView, UserDeleteView,
    CompanyChangeView, CompanyListView,
    UserMixin, RemoveIsNewUserStatus, PasswordRedirectView
)
from ..forms import (
    UsuarioInterno, UsuarioEdit, UsuarioEditNoAdmin,
    CompanyForm
)


class UserMixinTest(utils.BaseTestCase):

    def test_check_permissions_raises_permission_denied(self):
        mock_obj = mock.MagicMock()
        mock_obj.obj = mock.MagicMock()
        view = self.get_instance(
            UserMixin,
            request=self.get_request(self.user),
        )
        with self.assertRaises(PermissionDenied):
            view.check_obj_permissions(mock_obj)


class UserRedirectViewTest(utils.BaseTestCase):

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
            '/proyectos/'
        )


class UserUpdateViewTest(utils.BaseTestCase):

    def setUp(self):
        super(UserUpdateViewTest, self).setUp()
        self.view = UserUpdateView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request
        self.view.nivel_permiso_usuario = 3
        self.view.nivel_permiso_vista = self.view.permiso_requerido

    @mock.patch.object(UserUpdateView, 'check_obj_permissions')
    def test_user_update_check_200(self, mock_check):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_test)
        with self.login(username=self.user.username, password='password'):
            response = self.get_check_200('users:update')
            self.assertEqual(response.status_code, 200)
        mock_check.assert_called_once_with(self.user)

    def test_get_nivel_permiso(self):
        self.view.nivel_permiso_usuario = 1
        self.view.permiso_requerido = 3
        self.view.kwargs = {'username': None}
        self.assertEqual(self.view.get_nivel_permiso(), self.view.nivel_permiso_usuario)
        self.view.kwargs = {'username': 'otro_que_no_conozco'}
        self.assertEqual(self.view.get_nivel_permiso(), self.view.permiso_requerido)

    def test_get_success_url(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.view.kwargs = {'username': self.user.username}
        self.view.object = self.user
        self.assertEqual(
            self.view.get_success_url(),
            '/users/detalle/{}/'.format(self.user.username)
        )

    def test_get_object(self):
        self.view.kwargs = {'username': self.user.username}
        self.assertEqual(
            self.view.get_object(),
            self.user
        )

    def test_get_current_user_object_if_not_user_kwargs(self):
        self.view.kwargs = {}
        self.assertEqual(
            self.view.get_object(),
            self.user
        )

    def test_get_form_kwargs(self):
        test_kwargs = {
            'initial': {},
            'prefix': None,
            'instance': self.user
        }
        self.view.kwargs = {'username': self.user.username}
        self.view.object = self.user
        self.assertEqual(
            self.view.get_form_kwargs(),
            test_kwargs
        )

    def test_get_form_kwargs_different_user(self):
        self.user.groups.add(self.admin_group)
        test_user = self.user_factory(
            company=self.user.company.first(),
            customer=self.user.customer,
            email='hola@hola.com',
            username='hola',
            nivel_acceso=self.auxiliar_permission
        )
        test_kwargs = {
            'initial': {},
            'prefix': None,
            'user': test_user,
            'instance': test_user
        }
        self.view.kwargs = {'username': test_user.username}
        self.view.object = test_user
        self.assertEqual(
            self.view.get_form_kwargs(),
            test_kwargs
        )

    def test_get_form_kwargs_for_auxiliar_self_user(self):
        self.view.nivel_permiso_usuario = 1
        self.view.nivel_permiso_vista = 3
        test_kwargs = {'initial': {}, 'prefix': None}
        self.view.kwargs = {'username': self.user.username}
        self.assertEqual(
            self.view.get_form_kwargs(),
            test_kwargs
        )

    def test_get_form_kwargs_no_username(self):
        test_kwargs = {
            'initial': {},
            'prefix': None,
            'instance': self.user
        }
        self.view.object = self.user
        self.view.kwargs = {}
        self.assertEqual(
            self.view.get_form_kwargs(),
            test_kwargs
        )

    def test_returns_admin_form(self):
        self.view.kwargs = {'username': 'blabla'}
        self.assertEqual(
            self.view.get_form_class(),
            UsuarioEdit
        )

    def test_returns_not_admin_form(self):
        self.view.kwargs = {'username': self.user.username}
        self.assertEqual(
            self.view.get_form_class(),
            UsuarioEditNoAdmin
        )

    def test_returns_not_admin_form_no_username(self):
        self.view.kwargs = {}
        self.assertEqual(
            self.view.get_form_class(),
            UsuarioEditNoAdmin
        )

    def test_get_form_class(self):
        self.view.nivel_permiso_usuario = 1
        self.assertEqual(self.view.get_form_class(), UsuarioEditNoAdmin)


class ListUserViewTest(utils.BaseTestCase):
    def setUp(self):
        super(ListUserViewTest, self).setUp()
        company = Company.objects.create(company_name='my_company', customer=self.user.customer)
        self.user.company.add(company)
        self.user.groups.add(self.user_group)

    def additional_users_different_customer(self):
        self.user1_different_customer = self.user_factory(
            username='foreign_user',
            nivel_acceso=self.auxiliar_permission
        )
        company = Company.objects.create(company_name='another_company', customer=self.user.customer)
        self.user.company.add(company)
        self.user.groups.add(self.user_group)

    def test_list_users_renders_correctly(self):
        self.client.login(username=self.user.username, password='password')
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        response = self.client.get(reverse('users:list'))
        self.assertEqual(response.status_code, 200)

    def test_list_users_renders_correct_error(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertEqual(response.status_code, 403)

    def test_view_list_users_only_in_current_company(self):
        self.additional_users_different_customer()
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertNotContains(response, 'foreign_user')


class DetailUserViewTest(utils.BaseTestCase):

    def test_detail_view_another_user_requires_director_perms(self):
        company = Company.objects.create(
            company_name='another_company',
            customer=self.user.customer
        )
        self.user.company.add(company)
        self.user.groups.add(self.user_group)
        view = self.get_instance(
            UserDetailView,
            request=self.get_request(self.user),
        )
        view.kwargs = {'username': 'another_user'}
        with self.assertRaises(PermissionDenied):
            view.test_func()

    def test_detail_view_another_company_returns_user_obj(self):
        self.user.groups.add(self.user_group)
        self.user.groups.add(self.admin_group)
        company = Company.objects.create(
            company_name='another_company',
            customer=self.user.customer
        )
        self.user.company.add(company)
        self.user.currently_at = company
        view = self.get_instance(
            UserDetailView,
            request=self.get_request(self.user),
        )
        view.kwargs['username'] = None
        obj = view.get_object()
        self.assertEqual(obj, self.user)


class UserCreateViewTest(utils.BaseTestCase):

    def test_user_creation_form_query_involves_requests_user_companies(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        company_2 = Company.objects.create(
            company_name='some_other_company',
            customer=self.user.customer
        )
        self.user.company.add(company)
        self.user.company.add(company_2)
        view = self.get_instance(
            UserCreateView,
            request=self.get_request(self.user)
        )
        other_user = self.user_factory(username='bla', nivel_acceso=self.auxiliar_permission)
        other_user_company = Company.objects.create(
            company_name='other_user_company',
            customer=other_user.customer,
        )
        other_user.company.add(other_user_company)
        form = view.get_form()
        query = [repr(x) for x in self.user.company.all()]
        self.assertNotEqual(other_user.customer, self.user.customer)
        self.assertIsInstance(form, UsuarioInterno)
        self.assertQuerysetEqual(form.fields['company'].queryset, query, ordered=False)

    def test_user_creation_correct_success_url(self):
        view = self.get_instance(
            UserCreateView,
            request=self.get_request(self.user)
        )
        view.object = self.user_factory(username='some_user', nivel_acceso=self.auxiliar_permission)
        success_url = view.get_success_url()
        self.assertEqual('/users/detalle/{}/'.format(view.object.username), success_url)

    def test_user_creation_check_200(self):
        company = Company.objects.create(
            company_name='200_company',
            customer=self.user.customer
        )
        self.user.groups.add(self.user_group)
        self.user.company.add(company)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        with self.login(username=self.user.username, password='password'):
            response = self.get_check_200('users:new')
            self.assertEqual(response.status_code, 200)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
    def test_user_created_can_login(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        self.user.groups.add(self.user_group)
        self.user.nivel_acceso = self.director_permission
        self.user.company.add(company)
        self.user.save()
        with self.login(username=self.user.username, password='password'):
            data = {
                'customer': str(self.user.customer.id),
                'username': 'test_user_tres',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'lkjas@hola.com',
                'nivel_acceso': self.auxiliar_permission.id,
                'company': [str(company.id)],
                'password1': 'esteesunpsslargo',
                'password2': 'esteesunpsslargo'
            }
            response = self.client.post(reverse('users:new'), data)
            self.assertRedirects(
                response,
                reverse('users:detail', kwargs={'username': 'test_user_tres'}),
                msg_prefix='\n{}\n'.format(
                    str(response.context_data['form'].errors) if hasattr(response, 'context_data') else ''
                )
            )
        with self.login(username='test_user_tres', password='esteesunpsslargo'):
            response = self.client.get(reverse('users:detail', kwargs={'username': 'test_user_tres'}))
            self.assertEqual(response.status_code, 200)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
    def test_user_created_can_login_different_company(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        company_1 = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        self.user.groups.add(self.user_group)
        self.user.nivel_acceso = self.director_permission
        self.user.company.add(company_1, company)
        self.user.currently_at = company
        self.user.save()
        with self.login(username=self.user.username, password='password'):
            data = {
                'customer': str(self.user.customer.id),
                'username': 'test_user_tres',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'lkjas@hola.com',
                'nivel_acceso': self.auxiliar_permission.id,
                'company': [str(company_1.id)],
                'password1': 'esteesunpsslargo',
                'password2': 'esteesunpsslargo'
            }
            response = self.client.post(reverse('users:new'), data)
            self.assertRedirects(
                response,
                reverse('users:detail', kwargs={'username': 'test_user_tres'}),
                msg_prefix='\n{}\n'.format(
                    str(response.context_data['form'].errors) if hasattr(response, 'context_data') else ''
                )
            )


class CompanyCreateViewTest(utils.BaseTestCase):

    def setUp(self):
        super(CompanyCreateViewTest, self).setUp()
        self.view = CompanyCreateView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request

    def test_get_form(self):
        self.assertEqual(
            self.view.get_form().__class__,
            CompanyForm
        )

    def test_correct_success_url(self):
        self.view.object = factories.CompanyFactory(customer=self.user.customer)
        test_url = '/users/detalle/company/{}/'.format(self.view.object.pk)
        self.assertEqual(
            self.view.get_success_url(),
            test_url
        )

    def test_correct_initial_data(self):
        test_customer = self.user.customer
        self.assertEqual(
            self.view.get_initial()['customer'],
            test_customer
        )


class CompanyEditViewTest(utils.BaseTestCase):

    def setUp(self):
        super(CompanyEditViewTest, self).setUp()
        self.view = CompanyEditView()
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request

    def test_correct_success_url(self):
        self.view.object = factories.CompanyFactory(customer=self.user.customer)
        test_url = '/users/detalle/company/{}/'.format(self.view.object.pk)
        self.assertEqual(
            self.view.get_success_url(),
            test_url
        )

    def test_get_correct_object(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(test_company)
        self.view.kwargs = {'pk': test_company.pk}
        self.assertEqual(
            self.view.get_object(),
            test_company
        )

    def test_get_initial(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(test_company)
        self.user.currently_at = test_company
        self.user.save()
        self.assertEqual(self.view.get_initial()['is_new'], self.user.is_new)


class UserDeleteViewTest(utils.BaseTestCase):

    def setUp(self):
        super(UserDeleteViewTest, self).setUp()
        self.view = UserDeleteView()
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request

    def test_get_correct_object(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.view.kwargs = {'pk': test_company.pk, 'model': 'Company'}
        self.assertEqual(
            self.view.get_object(),
            test_company
        )

    def test_delete_object(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.view.kwargs = {'pk': test_company.pk, 'model': 'Company'}
        self.assertEqual(self.view.delete(request=self.request).status_code, 200)


class CompanyChangeViewTest(utils.BaseTestCase):

    def setUp(self):
        super(CompanyChangeViewTest, self).setUp()
        self.view = CompanyChangeView()
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request
        company = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company)
        self.user.currently_at = company

    def test_get_and_change_method(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.view.kwargs = {'company': test_company.company_name}
        self.user.company.add(test_company)
        self.assertEqual(
            self.view.get(self.request).status_code,
            200
        )
        self.assertEqual(
            self.user.currently_at,
            test_company
        )

    def test_get_and_permissiondenied(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.view.kwargs = {'company': test_company.company_name}
        with self.assertRaises(PermissionDenied):
            self.view.get(self.request)
        self.assertNotEqual(self.user.currently_at, test_company)

    def test_get_and_change_method_two_companies_same_name(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        factories.CompanyFactory(company_name=test_company)
        self.view.kwargs = {'company': test_company.company_name}
        self.user.company.add(test_company)
        self.assertEqual(
            self.view.get(self.request).status_code,
            200
        )
        self.assertEqual(
            self.user.currently_at,
            test_company
        )


class CompanyChangeViewFromListTest(utils.BaseTestCase):

    def test_get_change_from_list(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.groups.add(self.user_group, self.proyectos_group)
        self.user.company.add(company_test)
        with self.login(username=self.user.username, password='password'):
            response = self.client.get(reverse('users:company_detail', kwargs={'pk': company_test.pk}))
            self.assertRedirects(response, reverse('proyectos:proyect_dashboard'))

    def test_get_change_from_list_raises_permission_denied(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        company_test_2 = factories.CompanyFactory(customer=self.user.customer)
        self.user.groups.add(self.user_group, self.proyectos_group)
        self.user.company.add(company_test_2)
        with self.login(username=self.user.username, password='password'):
            response = self.client.get(reverse('users:company_detail', kwargs={'pk': company_test.pk}))
            self.assertEqual(response.status_code, 403, response.status_code)


class CompanyListViewTest(utils.BaseTestCase):

    def setUp(self):
        super(CompanyListViewTest, self).setUp()
        self.view = CompanyListView()
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request
        company = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company)
        self.user.currently_at = company

    def test_get_correct_queryset(self):
        test_company = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(test_company)
        test_companies_qs = [repr(a) for a in self.user.company.order_by('-company_name')]
        self.assertQuerysetEqual(
            self.view.get_queryset(),
            test_companies_qs
        )

    def test_get_context_data_has_model_name_attr(self):
        self.view.object_list = [repr(a) for a in self.user.company.order_by('-company_name')]
        self.view.kwargs = {}
        self.view.user_groups = self.user.groups.all()
        self.view.nivel_permiso_usuario = self.view.request.user.nivel_acceso.nivel
        self.view.nivel_permiso_vista = self.view.permiso_requerido
        self.assertEqual(
            self.view.get_context_data()['model'],
            'Company'
        )


class RemoveIsNewUserStatusTest(utils.BaseTestCase):

    def test_post(self):
        self.user.is_new = True
        request = self.get_request(self.user),
        view = self.get_instance(
            RemoveIsNewUserStatus,
            request=request,
            pk=self.user.pk
        )
        response = view.post(request)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'exito': True})


class PasswordRedirectViewTest(utils.BaseTestCase):

    def test_get_redirect_url_password_change(self):
        request = self.get_request(self.user),
        view = self.get_instance(
            PasswordRedirectView,
            request=request,
            pk=self.user.pk
        )
        view_url = view.get_redirect_url()
        self.assertEqual(view_url, reverse('account_change_password'))
