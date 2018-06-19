# from django.core.management import call_command
from django.test import tag
from django.test.utils import override_settings
from construbot.users.tests import utils
from construbot.proyectos.management.commands.poblar import Command
from construbot.users.models import Customer

class BaseCommandTest(utils.BaseTestCase):

    def assertNotRaises(self, func, exception, message):
        try:
            func()
        except exception:
            self.fail(message)


class PoblarCommandTesting(BaseCommandTest):

    @override_settings(DEBUG=True)
    def test_create_correct_user(self):
        nombres = ['customer_0', 'customer_1', 'customer_2']
        Command.create_customer(self, 3)
        customers = Customer.objects.all().order_by('customer_name')
        i=0
        for customer in nombres:
            self.assertEqual(customer, customers[i].customer_name)
            i = i+1
