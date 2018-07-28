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
    UserCreateView
)
from ..forms import UsuarioInterno


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
        self.view.object = self.view.get_object()
        self.assertEqual(
            self.view.get_success_url(),
            '/users/detalle/{}/'.format(self.user.username)
        )

    def test_get_object(self):
        # Expect: self.user, as that is the request's user object
        self.view.kwargs = {'username': self.user.username}
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
