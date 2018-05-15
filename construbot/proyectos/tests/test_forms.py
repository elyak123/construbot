from . import factories
from django.test import RequestFactory, tag
from construbot.users.tests import factories as user_factories
from construbot.users.tests import utils
from construbot.proyectos import forms, models
import decimal


class ContratoFormTest(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)

    def test_contrato_form_creation_is_valid(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(company=contrato_company)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company.company_name,
                     }
        form = forms.ContratoForm(data=form_data)
        form.request = self.request
        self.assertTrue(form.is_valid())

    def test_contrato_form_saves_on_db(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(company=contrato_company)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company.company_name,
                     }
        form = forms.ContratoForm(data=form_data)
        form.request = self.request
        form.is_valid()
        form.save()
        try:
            contrato = models.Contrato.objects.get(contrato_name='TEST CONTRATO 1', cliente=contrato_cliente)
        except models.Contrato.DoesNotExist:
            self.fail('Contrato no fue guardado en base de datos.')
        self.assertIsInstance(contrato, models.Contrato)

    def test_form_actually_changes_contrato(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(company=contrato_company)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company.company_name,
                     }
        form = forms.ContratoForm(data=form_data, instance=contrato_factory)
        form.request = self.request
        form.is_valid()
        form.save()
        self.assertEqual(form.instance.monto, decimal.Decimal('1222.12'))


class ClienteFormTest(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)

    def test_cliente_form_creation_is_valid(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        form_data = {'cliente_name': 'Juanito', 'company': cliente_company.id}
        form = forms.ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_cliente_form_saves_on_db(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        form_data = {'cliente_name': 'Juanito', 'company': cliente_company.id}
        form = forms.ClienteForm(data=form_data)
        form.is_valid()
        form.save()
        cliente = models.Cliente.objects.get(cliente_name='Juanito')
        self.assertIsInstance(form.instance, models.Cliente)
        self.assertEqual(form.instance.id, cliente.id)
