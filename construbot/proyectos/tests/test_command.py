from unittest import mock
from django.test import tag
from django.test.utils import override_settings
from construbot.users.tests import utils
from construbot.proyectos.management.commands.poblar import Command, ImproperlyConfigured


class BaseCommandTest(utils.BaseTestCase):

    def assertNotRaises(self, func, exception, message):
        try:
            func()
        except exception:
            self.fail(message)


class PoblarCommandTesting(BaseCommandTest):

    @override_settings(DEBUG=False)
    def test_handle_raises_at_debug_false(self):
        instance = Command()
        with self.assertRaises(ImproperlyConfigured):
            instance.handle()

    @mock.patch('construbot.proyectos.management.commands.poblar.user_factories.CustomerFactory')
    def test_create_correct_customer(self, mock_customer_factory):
        instance = Command()
        instance.create_customer(3)
        calls = [
            mock.call(customer_name='customer_0'),
            mock.call(customer_name='customer_1'),
            mock.call(customer_name='customer_2')
        ]
        self.assertEqual(mock_customer_factory.call_count, 3)
        mock_customer_factory.assert_has_calls(calls, any_order=False)
        self.assertEqual(len(instance.customer), 3)
        self.assertIsInstance(instance.customer, list)

    @mock.patch('construbot.proyectos.management.commands.poblar.user_factories.GroupFactory')
    def test_create_core_groups(self, mock_group_factory):
        instance = Command()
        instance.create_core_groups()
        calls = [
            mock.call(name='proyectos'),
            mock.call(name='Administrators'),
            mock.call(name='users')
        ]
        self.assertEqual(mock_group_factory.call_count, 3)
        self.assertEqual(len(instance.groups), 3)
        mock_group_factory.assert_has_calls(calls, any_order=False)

    def test_create_user_raises_error_no_customer(self):
        instance = Command()
        instance.customer = None
        with self.assertRaises(ImproperlyConfigured):
            instance.create_user(3)

    def test_create_companies_raises_error_no_customer(self):
        instance = Command()
        instance.customer = None
        with self.assertRaises(ImproperlyConfigured):
            instance.create_companies(3)
