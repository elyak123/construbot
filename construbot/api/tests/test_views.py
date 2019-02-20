from django.test import tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.tests import utils

User = get_user_model()


class TestApiViews(utils.BaseTestCase):

    def test_email_uniqueness(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.post(reverse('api:get_user'), data={'email': self.user.email})
        self.assertFalse(response.data['unique'])

    def test_create_customer_user_and_company_raises_not_valid_email(self):
        self.client.login(username=self.user.username, password='password')
        email_test = 'Soy correo mal formado'
        response = self.client.post(
            reverse('api:creation'), data={'customer': 'nuevo_customer', 'email': email_test}
        )
        self.assertFalse(response.json()['success'])

    def test_create_customer_user_and_company(self):
        self.client.login(username=self.user.username, password='password')
        email_test = 'me@gmail.com'
        response = self.client.post(
            reverse('api:creation'), data={'customer': 'nuevo_customer', 'email': email_test}
        )
        self.assertTrue(response.json()['success'])
        self.assertEqual(email_test, User.objects.get(id=response.json()['id']).email)
        self.assertFalse(response.data['usable'])

    def test_change_user_password(self):
        self.client.login(username=self.user.username, password='password')
        test_pwd = 'gatitos'
        response = self.client.post(reverse('api:change_pwd'), data={'id_usr': self.user.id, 'pwd': test_pwd})
        self.client.logout()
        self.assertTrue(self.client.login(username=self.user.username, password='gatitos'))
        self.assertTrue(response.data['pass'])
