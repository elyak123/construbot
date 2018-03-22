from django.test import RequestFactory

from test_plus.test import TestCase
from django.urls import reverse
from construbot.users.models import User
# from . import factories


class AccountAdapterTest(TestCase):
    def test_singup_correct_requirements(self):
        request = self.client.post(reverse('account_signup'), data={
            'email': 'bla@example.com',
            'username': 'Joe',
            'password1': 'super_secret',
            'password2': 'super_secret',
            'first_name': 'Joe',
            'last_name': 'Doe',
            'company': 'My own company',
        })
        self.assertEqual(User.objects.count(), 1)
