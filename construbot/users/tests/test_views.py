from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, override_settings, tag
from django.urls import reverse
from django.contrib.auth.models import Group
from construbot.users.models import Company
from . import factories
from . import utils

from ..views import (
    UserRedirectView,
    UserUpdateView, UserDetailView,
    UserCreateView, CompanyCreateView,
    CompanyEditView, UserDeleteView,
    CompanyChangeView, CompanyListView
)
from ..forms import (
    UsuarioInterno, UsuarioEdit, UsuarioEditNoAdmin,
    CompanyForm
)

class BaseUserTestCase(utils.BaseTestCase):

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
            '/proyectos/'
        )


class TestUserUpdateView(BaseUserTestCase):

    def setUp(self):
        super(TestUserUpdateView, self).setUp()
        self.view = UserUpdateView()
        # Generate a fake request
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request

    def test_get_success_url(self):
        self.view.kwargs = {'username': 'testuser'}
        self.view.object = self.view.get_object()
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
        test_kwargs = {'initial': {}, 'prefix': None, 'user': self.user}
        self.assertEqual(
            self.view.get_form_kwargs(),
            test_kwargs
        )

    def test_returns_admin_form(self):
        self.view.permiso_administracion = True
        self.assertEqual(
            self.view.get_form_class(),
            UsuarioEdit
        )

    def test_returns_no_admin_form(self):
        self.view.permiso_administracion = False
        self.assertEqual(
            self.view.get_form_class(),
            UsuarioEditNoAdmin
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
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        response = self.client.get(reverse('users:list'))
        self.assertEqual(response.status_code, 200)

    def test_list_users_renders_correct_error(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertEqual(response.status_code, 403)

    def test_view_list_users_only_in_current_company(self):
        self.additional_users_different_customer()
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('users:list'))
        self.assertNotContains(response, 'foreign_user')


class TestDetailUserView(BaseUserTestCase):
    def test_detail_view_another_user_requires_admin_perms(self):
        group, created = Group.objects.get_or_create(name='Users')
        company = Company.objects.create(
            company_name='another_company',
            customer=self.user.customer
        )
        self.user.company.add(company)
        self.user.groups.add(group)
        view = self.get_instance(
            UserDetailView,
            request=self.get_request(self.user),
        )
        view.kwargs = {'username': 'another_user'}
        with self.assertRaises(PermissionDenied):
            view.test_func()

    def test_detail_view_another_user_requires_admin_perms(self):
        group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
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

class TestUserCreateView(BaseUserTestCase):
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
        view.permiso_administracion = True
        other_user = self.make_user(username='bla')
        other_user_company = Company.objects.create(
            company_name='other_user_company',
            customer=other_user.customer
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
        view.object = self.make_user(username='some_user')
        success_url = view.get_success_url()
        self.assertEqual('/users/detalle/some_user/', success_url)

    def test_user_creation_check_200(self):
        company = Company.objects.create(
            company_name='200_company',
            customer=self.user.customer
        )
        group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.user.company.add(company)
        with self.login(username=self.user.username, password='password'):
            response = self.get_check_200('users:new')
            self.assertEqual(response.status_code, 200)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
    def test_user_created_can_login(self):
        company = Company.objects.create(
            company_name='some_company',
            customer=self.user.customer
        )
        users_group, created = Group.objects.get_or_create(name='Users')
        self.user.groups.add(users_group)
        group, created = Group.objects.get_or_create(name='Administrators')
        self.user.groups.add(group)
        self.user.company.add(company)
        with self.login(username=self.user.username, password='password'):
            data = {
                'customer': str(self.user.customer.id),
                'username': 'test_user_tres',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'lkjas@hola.com',
                'groups': [str(users_group.id)],
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


class TestCompanyCreateView(BaseUserTestCase):

    def setUp(self):
        super(TestCompanyCreateView, self).setUp()
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


class TestCompanyEditView(BaseUserTestCase):

    def setUp(self):
        super(TestCompanyEditView, self).setUp()
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

class TestUserDeleteView(BaseUserTestCase):

    def setUp(self):
        super(TestUserDeleteView, self).setUp()
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

class TestCompanyChangeView(BaseUserTestCase):

    def setUp(self):
        super(TestCompanyChangeView, self).setUp()
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


class TestCompanyListView(BaseUserTestCase):

    def setUp(self):
        super(TestCompanyListView, self).setUp()
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
        self.view.kwargs={}
        self.view.user_groups = self.user.groups.all()
        self.view.permiso_administracion = True
        self.assertEqual(
            self.view.get_context_data()['model'],
            'Company'
        )
