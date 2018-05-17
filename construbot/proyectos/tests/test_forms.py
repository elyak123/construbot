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
        form.request = self.request
        self.assertTrue(form.is_valid())

    def test_cliente_form_saves_on_db(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        form_data = {'cliente_name': 'Juanito', 'company': cliente_company.id}
        form = forms.ClienteForm(data=form_data)
        form.request = self.request
        form.is_valid()
        form.save()
        cliente = models.Cliente.objects.get(cliente_name='Juanito')
        self.assertIsInstance(form.instance, models.Cliente)
        self.assertEqual(form.instance.id, cliente.id)

    def test_cliente_edit_form_changes_instance(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        cliente_factory = factories.ClienteFactory(company=cliente_company, cliente_name='Pepe')
        form_data = {'cliente_name': 'Juanito', 'company': cliente_company.id}
        form = forms.ClienteForm(data=form_data, instance=cliente_factory)
        form.request = self.request
        form.is_valid()
        form.save()
        self.assertEqual(form.instance.cliente_name, 'Juanito')
        self.assertEqual(form.instance.pk, cliente_factory.pk)


class DestinatarioFormTest(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)

    def test_destinatario_form_creation_is_valid(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        self.user.currently_at = destinatario_company
        form_data = {
            'company': destinatario_company.id,
            'destinatario_text': "Un wey",
            'cliente': destinatario_cliente.id
        }
        form = forms.DestinatarioForm(data=form_data)
        form.request = self.request
        self.assertTrue(form.is_valid())

    def test_destinatario_form_saves_obj_in_database(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        self.user.currently_at = destinatario_company
        form_data = {
            'company': destinatario_company.id,
            'destinatario_text': 'Un wey',
            'cliente': destinatario_cliente.id
        }
        form = forms.DestinatarioForm(data=form_data)
        form.request = self.request
        form.is_valid()
        form.save()
        destinatario = forms.Destinatario.objects.get(destinatario_text='Un wey')
        self.assertIsInstance(form.instance, forms.Destinatario)
        self.assertEqual(form.instance.id, destinatario.id)

    def test_destinatario_form_creation_No_client_is_NOT_valid(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = destinatario_company
        form_data = {'company': destinatario_company.id, 'destinatario_text': "Un wey"}
        form = forms.DestinatarioForm(data=form_data)
        form.request = self.request
        self.assertFalse(form.is_valid())

    def test_form_actually_changes_destinatario(self):
        destinatario = factories.DestinatarioFactory()
        self.user.currently_at = destinatario.company
        form_data = {'company': destinatario.company.id, 'destinatario_text': 'Ing. Rodrigo Cruz',
                     'puesto': 'Gerente', 'cliente': destinatario.cliente.id}
        form = forms.DestinatarioForm(data=form_data, instance=destinatario)
        form.request = self.request
        form.is_valid()
        sitio_obj = models.Destinatario.objects.get(pk=destinatario.pk)
        self.assertEqual(destinatario.destinatario_text, 'Ing. Rodrigo Cruz')
        self.assertEqual(sitio_obj.pk, destinatario.pk)


class SitioFormTest(utils.BaseTestCase):

    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)

    def test_sitio_form_creation_is_not_valid_with_another_company(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        sitio_company_2 = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'company': sitio_company_2.id}
        form = forms.SitioForm(data=form_data)
        form.request = self.request
        self.assertFalse(form.is_valid())

    def test_sitio_form_creation_is_valid(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'company': sitio_company.id}
        form = forms.SitioForm(data=form_data)
        form.request = self.request
        self.assertTrue(form.is_valid())

    def test_form_actually_changes_sitio(self):
        sitio = factories.SitioFactory()
        self.user.currently_at = sitio.company
        form_data = {'sitio_name': 'Ex-Taller de Ferrocarriles', 'sitio_location': 'Aguascalientes, Ags.',
                     'company': sitio.company.id}
        form = forms.SitioForm(data=form_data, instance=sitio)
        form.request = self.request
        form.is_valid()
        sitio_obj = models.Sitio.objects.get(pk=sitio.pk)
        self.assertEqual(sitio.sitio_location, 'Aguascalientes, Ags.')
        self.assertEqual(sitio_obj.pk, sitio.pk)

    def test_sitio_form_saves_obj_in_db(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'company': sitio_company.id}
        form = forms.SitioForm(data=form_data)
        form.request = self.request
        form.is_valid()
        form.save()
        sitio = models.Sitio.objects.get(sitio_name='Tamaulipas')
        self.assertIsInstance(form.instance, models.Sitio)
        self.assertEqual(form.instance.id, sitio.id)