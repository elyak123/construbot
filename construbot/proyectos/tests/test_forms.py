import decimal
from unittest import mock
from django.shortcuts import reverse
from django.test import tag
from construbot.users.tests import factories as user_factories
from construbot.users.tests import utils
from construbot.proyectos import forms, models
from . import factories


class BaseFormTest(utils.BaseTestCase):

    def setUp(self):
        super(BaseFormTest, self).setUp()
        self.request = self.get_request(self.user)


class ContratoFormTest(BaseFormTest):

    def test_contrato_form_creation_is_valid_when_is_new_user(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        self.user.is_new = True
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company.company_name,
                     'users': [self.user.id],
                     'anticipo': 0.0,
                     }
        form = forms.ContratoForm(data=form_data)
        form.request = self.request
        self.assertTrue(form.is_valid())

    def test_contrato_form_saves_on_db(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company.company_name,
                     'users': [self.user.id],
                     'anticipo': 0.0,
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
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company.company_name,
                     'users': [self.user.id],
                     'anticipo': 0.0,
                     }
        form = forms.ContratoForm(data=form_data, instance=contrato_factory)
        form.request = self.request
        form.is_valid()
        form.save()
        self.assertEqual(form.instance.monto, decimal.Decimal('1222.12'))


class ClienteFormTest(BaseFormTest):

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


class DestinatarioFormTest(BaseFormTest):

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
        form_data = {'destinatario_text': "Un wey"}
        form = forms.DestinatarioForm(data=form_data)
        form.request = self.request
        self.assertFalse(form.is_valid())

    def test_form_actually_changes_destinatario(self):
        destinatario = factories.DestinatarioFactory()
        self.user.currently_at = destinatario.cliente.company
        form_data = {'company': destinatario.cliente.company.id, 'destinatario_text': 'Ing. Rodrigo Cruz',
                     'puesto': 'Gerente', 'cliente': destinatario.cliente.id}
        form = forms.DestinatarioForm(data=form_data, instance=destinatario)
        form.request = self.request
        form.is_valid()
        sitio_obj = models.Destinatario.objects.get(pk=destinatario.pk)
        self.assertEqual(destinatario.destinatario_text, 'Ing. Rodrigo Cruz')
        self.assertEqual(sitio_obj.pk, destinatario.pk)


class CatalogoConceptosFormsetTest(BaseFormTest):

    def test_creacion_de_catalogo_conceptos(self):
        contrato = factories.ContratoFactory()
        unit = factories.UnitFactory(company=contrato.cliente.company)
        formset = forms.ContractConceptInlineForm({
            'concept_set-INITIAL_FORMS': '0',
            'concept_set-TOTAL_FORMS': '1',
            'concept_set-0-code': 'SOME',
            'concept_set-0-concept_text': 'Concepto',
            'concept_set-0-unit': str(unit.id),
            'concept_set-0-total_cuantity': '100',
            'concept_set-0-unit_price': '10',
            'concept_set-0-DELETE': 'False',
            'concept_set-0-project': str(contrato.id),
        }, instance=contrato)
        self.assertTrue(formset.is_valid(), formset.errors)

    def test_creacion_de_catalogo_mismo_concepto_renders_error(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato = factories.ContratoFactory(cliente__company=contrato_company)
        self.user.groups.add(self.proyectos_group)
        self.user.groups.add(self.admin_group)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.client.login(username=self.user.username, password='password')
        unit = factories.UnitFactory(company=contrato_company)
        formset_data = {
            'concept_set-INITIAL_FORMS': '0',
            'concept_set-TOTAL_FORMS': '2',
            'concept_set-0-code': 'SOME',
            'concept_set-0-concept_text': 'Concepto',
            'concept_set-0-unit': str(unit.id),
            'concept_set-0-total_cuantity': '100',
            'concept_set-0-unit_price': '10',
            'concept_set-0-DELETE': 'False',
            'concept_set-0-project': str(contrato.id),
            'concept_set-1-code': 'SOME',
            'concept_set-1-concept_text': 'Concepto',
            'concept_set-1-unit': str(unit.id),
            'concept_set-1-total_cuantity': '100',
            'concept_set-1-unit_price': '10',
            'concept_set-1-DELETE': 'False',
            'concept_set-1-project': str(contrato.id),
        }
        response = self.client.post(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato.pk}), formset_data)
        self.assertFormsetError(response, 'formset', None, field=None, errors=['Please correct the duplicate data for concept_text.'])
        self.assertEqual(response.status_code, 200)

    def test_creacion_de_catalogo_unidad_differente_company_renders_error(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        self.user.groups.add(self.proyectos_group)
        self.user.groups.add(self.admin_group)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.client.login(username=self.user.username, password='password')
        unit = factories.UnitFactory()
        unit_2 = factories.UnitFactory(company=contrato_company)
        formset_data = {
            'concept_set-INITIAL_FORMS': '0',
            'concept_set-TOTAL_FORMS': '2',
            'concept_set-0-code': 'SOME',
            'concept_set-0-concept_text': 'Concepto',
            'concept_set-0-unit': str(unit_2.id),
            'concept_set-0-total_cuantity': '100',
            'concept_set-0-unit_price': '10',
            'concept_set-0-DELETE': 'False',
            'concept_set-0-project': str(contrato.id),
            'concept_set-1-code': 'SOME',
            'concept_set-1-concept_text': 'Concepto',
            'concept_set-1-unit': str(unit.id),
            'concept_set-1-total_cuantity': '100',
            'concept_set-1-unit_price': '10',
            'concept_set-1-DELETE': 'False',
            'concept_set-1-project': str(contrato.id),
        }
        response = self.client.post(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato.pk}), formset_data)
        self.assertFormsetError(response, 'formset', 1, field='unit', errors=['El concepto debe pertenecer a la misma compañia que su unidad.'])
        self.assertEqual(response.status_code, 200)


class SitioFormTest(BaseFormTest):

    def test_sitio_form_creation_is_not_valid_with_another_company(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        sitio_company_2 = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'company': sitio_company_2.id}
        form = forms.SitioForm(data=form_data)
        form.request = self.request
        self.assertFalse(form.is_valid())

    def test_sitio_form_creation_is_valid(self):
        sitio_cliente = factories.ClienteFactory(company__customer=self.user.customer)
        self.user.currently_at = sitio_cliente.company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'cliente': sitio_cliente.id}
        form = forms.SitioForm(data=form_data)
        form.request = self.request
        self.assertTrue(form.is_valid())

    def test_form_actually_changes_sitio(self):
        sitio = factories.SitioFactory()
        self.user.currently_at = sitio.cliente.company
        form_data = {'sitio_name': 'Ex-Taller de Ferrocarriles', 'sitio_location': 'Aguascalientes, Ags.',
                     'cliente': sitio.cliente.id}
        form = forms.SitioForm(data=form_data, instance=sitio)
        form.request = self.request
        form.is_valid()
        sitio_obj = models.Sitio.objects.get(pk=sitio.pk)
        self.assertEqual(sitio.sitio_location, 'Aguascalientes, Ags.')
        self.assertEqual(sitio_obj.pk, sitio.pk)

    def test_sitio_form_saves_obj_in_db(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        sitio_cliente = factories.ClienteFactory(company=sitio_company)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'cliente': sitio_cliente.id}
        form = forms.SitioForm(data=form_data)
        form.request = self.request
        form.is_valid()
        form.save()
        sitio = models.Sitio.objects.get(sitio_name='Tamaulipas')
        self.assertIsInstance(form.instance, models.Sitio)
        self.assertEqual(form.instance.id, sitio.id)


class BaseCleanFormTest(BaseFormTest):

    def test_clean_BaseCleanFormTest_company_is_None(self):
        forms.BaseCleanForm._meta = mock.Mock()
        form = forms.BaseCleanForm()
        form.cleaned_data = {'company': None}
        with self.assertRaises(forms.forms.ValidationError):
            form.clean()

    def test_clean_BaseCleanFormTest_different_currently_at(self):
        forms.BaseCleanForm._meta = mock.Mock()
        forms.BaseCleanForm.request = mock.Mock()
        form = forms.BaseCleanForm()
        form.cleaned_data = {'company': mock.Mock()}
        with self.assertRaises(forms.forms.ValidationError):
            form.clean()
