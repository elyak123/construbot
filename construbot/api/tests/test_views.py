from users.tests import factories, utils
from construbot.users.models import User
from construbot.api.views import email_uniqueness
from django.test import RequestFactory, tag
from django.urls import reverse


class BaseCoreTestCase(utils.BaseTestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()


class TestApiViews(BaseCoreTestCase):

    def test_email_uniqueness(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.post(reverse('api:get_user'), data={'email': self.user.email})
        self.assertFalse(response.data['unique'])
    @tag('current')
    def test_create_customer_user_and_company_raises_not_valid_email(self):
        self.client.login(username=self.user.username, password='password')
        email_test = 'Soy correo mal formado'
        response = self.client.post(
            reverse('api:creation'), data={'customer': 'nuevo_customer', 'email': email_test}
        )
        self.assertFalse(response.json()['success'])

    @tag('current')
    def test_create_customer_user_and_company(self):
        self.client.login(username=self.user.username, password='password')
        email_test = 'me@gmail.com'
        response = self.client.post(
            reverse('api:creation'), data={'customer': 'nuevo_customer', 'email': email_test}
        )
        print(response.json())
        self.assertTrue(response.json()['success'], msg=response.json())
        self.assertEqual(email_test, User.objects.get(id=response.json()['id']).email)
        self.assertFalse(response.data['usable'])

    def test_change_user_password(self):
        self.client.login(username=self.user.username, password='password')
        test_pwd = 'gatitos'
        response = self.client.post(reverse('api:change_pwd'), data={'id_usr': self.user.id, 'pwd': test_pwd})
        self.client.logout()
        self.assertTrue(self.client.login(username=self.user.username, password='gatitos'))
        self.assertTrue(response.data['pass'])
