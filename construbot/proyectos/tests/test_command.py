from unittest import mock
from django.test import tag
from django.test.utils import override_settings
from construbot.users.tests import utils
from construbot.proyectos.management.commands import poblar


class BaseCommandTest(utils.BaseTestCase):

    def assertNotRaises(self, func, exception, message):
        try:
            func()
        except exception:
            self.fail(message)


class PoblarCommandTesting(BaseCommandTest):

    @override_settings(DEBUG=False)
    def test_handle_raises_at_debug_false(self):
        instance = poblar.Command()
        with self.assertRaises(poblar.ImproperlyConfigured):
            instance.handle()

    @mock.patch('construbot.proyectos.management.commands.poblar.user_factories.CustomerFactory')
    def test_create_correct_customer(self, mock_customer_factory):
        instance = poblar.Command()
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
        instance = poblar.Command()
        instance.create_core_groups()
        calls = [
            mock.call(name='Proyectos'),
            mock.call(name='Users')
        ]
        self.assertEqual(mock_group_factory.call_count, 2)
        self.assertEqual(len(instance.groups), 2)
        mock_group_factory.assert_has_calls(calls, any_order=False)

    def test_create_user_raises_error_no_customer(self):
        instance = poblar.Command()
        instance.customer = None
        with self.assertRaises(poblar.ImproperlyConfigured):
            instance.create_user(3)

    def test_create_companies_raises_error_no_customer(self):
        instance = poblar.Command()
        instance.customer = None
        with self.assertRaises(poblar.ImproperlyConfigured):
            instance.create_companies(3)
    @tag('current')
    @override_settings(DEBUG=True)
    @mock.patch('construbot.proyectos.management.commands.poblar.call_command')
    @mock.patch('construbot.proyectos.management.commands.poblar.establish_access_levels')
    @mock.patch.object(poblar.Command, 'create_customer')
    @mock.patch.object(poblar.Command, 'create_core_groups')
    @mock.patch.object(poblar.Command, 'create_user')
    @mock.patch.object(poblar.Command, 'create_companies')
    @mock.patch.object(poblar.Command, 'create_clientes')
    @mock.patch.object(poblar.Command, 'create_sitios')
    @mock.patch.object(poblar.Command, 'create_destinatarios')
    @mock.patch.object(poblar.Command, 'create_contratos')
    @mock.patch.object(poblar.Command, 'create_concepts')
    def test_handle(
            self, concepts, contratos, destinatarios, sitios, clientes,
            companies, users, groups, customer, levels, call_poblar):
        manager = mock.MagicMock()
        concepts.return_value = mock.MagicMock()
        contratos.return_value = mock.MagicMock()
        destinatarios.return_value = mock.MagicMock()
        sitios.return_value = mock.MagicMock()
        clientes.return_value = mock.MagicMock()
        companies.return_value = mock.MagicMock()
        users.return_value = mock.MagicMock()
        groups.return_value = mock.MagicMock()
        customer.return_value = mock.MagicMock()
        levels.return_value = mock.MagicMock()
        call_poblar.Command.return_value = mock.MagicMock()
        attrs = {
            'create_customer': customer,
            'create_core_groups': groups,
            'create_user': users,
            'create_companies': companies,
            'create_clientes': clientes,
            'create_sitios': sitios,
            'create_destinatarios': destinatarios,
            'create_contratos': contratos,
            'create_concepts': concepts,
        }
        manager.configure_mock(**attrs)
        command = poblar.Command()
        command.stdout.write = mock.MagicMock()
        command.customer = customer.return_value
        command.users = users.return_value
        command.company = companies.return_value
        command.clientes = clientes.return_value
        command.sitios = sitios.return_value
        command.contratos = contratos.return_value
        command.concepts = concepts.return_value
        command.handle()
        # import pdb; pdb.set_trace()
        customer.assert_called_once_with(5)
        groups.assert_called_once_with()
        levels.assert_called_once_with()
        users.assert_called_once_with(20)
        companies.assert_called_once_with(30)
        clientes.assert_called_once_with(100)
        sitios.assert_called_once_with(200)
        contratos.assert_called_once_with(1500)
        concepts.assert_called_once_with(5000)
