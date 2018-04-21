from django.test import RequestFactory
from django.http import Http404
from construbot.users.tests import utils
from construbot.users.tests import factories as user_factories
from .views import (ContratoListView, ClienteListView, SitioListView, DestinatarioListView,
                    ContratoDetailView, ClienteDetailView, SitioDetailView, CatalogoConceptos,
                    DestinatarioDetailView, ContratoCreationView, ClienteCreationView,
                    SitioCreationView, DestinatarioCreationView, ContratoEditView, CatalogoConceptosInlineFormView,
                    SitioAutocomplete, ClienteAutocomplete, UnitAutocomplete)
from .forms import (ContratoForm, ClienteForm, SitioForm, DestinatarioForm)
from . import factories
import json


class BaseViewTest(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)


class ContratoListTest(BaseViewTest):
    def test_contrato_different_customer_doesnt_appear(self):
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        cliente_test = factories.ClienteFactory(company=company_test)
        contrato = factories.ContratoFactory(cliente=cliente_test)
        contrato_2 = factories.ContratoFactory()
        contrato_3 = factories.ContratoFactory(cliente=cliente_test)
        view = self.get_instance(
            ContratoListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(y) for y in sorted([contrato, contrato_3], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(qs, qs_test)


class ClienteListTest(BaseViewTest):
    def test_cliente_query_only_same_client(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        cliente = factories.ClienteFactory(company=cliente_company, cliente_name='cliente_bLdYMUBC')
        cliente_2 = factories.ClienteFactory(company=cliente_company, cliente_name='cliente_JBFQADJV')
        cliente_3 = factories.ClienteFactory()
        view = self.get_instance(
            ClienteListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(a) for a in sorted([cliente, cliente_2], key=lambda x: repr(x).lower(), reverse=False)]
        self.assertQuerysetEqual(qs, qs_test)


class SitioListTest(BaseViewTest):
    def test_sitio_query_only_same_company(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        sitio = factories.SitioFactory(company=sitio_company)
        sitio_2 = factories.SitioFactory(company=sitio_company)
        sitio_3 = factories.SitioFactory()
        view = self.get_instance(
            SitioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted([sitio, sitio_2], key=lambda x: repr(x).lower(), reverse=False)]
        self.assertQuerysetEqual(qs, qs_test)


class DestinatarioListTest(BaseViewTest):
    def test_destinatario_query_same_client_company(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario_cliente_2 = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        destinatario_2 = factories.DestinatarioFactory(cliente=destinatario_cliente_2)
        destinatario_3 = factories.DestinatarioFactory()
        view = self.get_instance(
            DestinatarioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted(
            [destinatario, destinatario_2], key=lambda x: repr(x).lower(), reverse=False
        )]
        self.assertQuerysetEqual(qs, qs_test)


class ContratoDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_contrato_object(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        view = self.get_instance(
            ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_assert_contrato_request_returns_404_with_no_currently_at(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        view = self.get_instance(
            ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            obj = view.get_object()


class ClienteDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_cliente_object(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = cliente_company
        cliente = factories.ClienteFactory(company=cliente_company)
        view = self.get_instance(
            ClienteDetailView,
            pk=cliente.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, cliente)

    def test_assert_cliente_request_returns_404_with_no_currently_at(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        cliente = factories.ClienteFactory(company=cliente_company)
        view = self.get_instance(
            ClienteDetailView,
            pk=cliente.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            obj = view.get_object()


class SitioDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_sitio_object(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = sitio_company
        sitio = factories.SitioFactory(company=sitio_company)
        view = self.get_instance(
            SitioDetailView,
            pk=sitio.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, sitio)

    def test_assert_sitio_request_returns_404_with_no_currently_at(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        sitio = factories.SitioFactory(company=sitio_company)
        view = self.get_instance(
            SitioDetailView,
            pk=sitio.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            obj = view.get_object()


class DestinatarioDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_destinatario_object(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(
            cliente=destinatario_cliente,
            company=destinatario_company
        )
        view = self.get_instance(
            DestinatarioDetailView,
            pk=destinatario.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, destinatario)

    def test_assert_request_returns_404_with_no_currently_at(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        view = self.get_instance(
            DestinatarioDetailView,
            pk=destinatario.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            view.get_object()


class ContratoCreationTest(BaseViewTest):
    def test_get_initial_returns_1_when_no_contratos(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        dicc = {"currently_at": contrato_company.company_name, "folio": 1}
        view = self.get_instance(
            ContratoCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_get_initial_returns_the_next_id_when_contratos_exist(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        self.request.user.currently_at = contrato_company
        dicc = {"currently_at": contrato_company.company_name, "folio": contrato.folio + 1}
        view = self.get_instance(
            ContratoCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_get_context_data_has_same_company_that_currently_at(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        view = self.get_instance(
            ContratoCreationView,
            request=self.request
        )
        view.get_menu = lambda: []
        view.permiso_administracion = True
        view.object = None
        dicc_test = view.get_context_data()
        self.assertEqual(dicc_test['company'], contrato_company)

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
        view = self.get_instance(
            ContratoCreationView,
            request=self.request
        )
        form = ContratoForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertTrue(view.form_valid(form))

    def test_contrato_form_creation_is_not_valid_with_another_company(self):
        contrato_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_company_2 = user_factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(company=contrato_company)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company_2.company_name,
                     }
        view = self.get_instance(
            ContratoCreationView,
            request=self.request
        )
        view.get_context_data = lambda form: {}
        form = ContratoForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertFalse(hasattr(ContratoCreationView, 'object'))
        self.assertEqual(view.form_valid(form).status_code, 200)


class ClienteCreationTest(BaseViewTest):
    def test_get_initial_returns_the_correct_company(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = cliente_company
        dicc = {"company": cliente_company}
        view = self.get_instance(
            ClienteCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_cliente_form_creation_is_valid(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        form_data = {'cliente_name': "Juanito", 'company': cliente_company.id}
        view = self.get_instance(
            ClienteCreationView,
            request=self.request
        )
        form = ClienteForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertTrue(view.form_valid(form))

    def test_cliente_form_creation_is_not_valid_with_another_company(self):
        cliente_company = user_factories.CompanyFactory(customer=self.user.customer)
        cliente_company_2 = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        form_data = {'cliente_name': "Juanito", 'company': cliente_company_2.id}
        view = self.get_instance(
            ClienteCreationView,
            request=self.request
        )
        view.get_context_data = lambda form: {}
        form = ClienteForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertFalse(hasattr(ClienteCreationView, 'object'))
        self.assertEqual(view.form_valid(form).status_code, 200)


class SitioCreationTest(BaseViewTest):
    def test_get_initial_returns_the_correct_company(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = sitio_company
        dicc = {"company": sitio_company}
        view = self.get_instance(
            SitioCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_sitio_form_creation_is_valid(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'company': sitio_company.id}
        view = self.get_instance(
            SitioCreationView,
            request=self.request
        )
        form = SitioForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertTrue(view.form_valid(form))

    def test_sitio_form_creation_is_not_valid_with_another_company(self):
        sitio_company = user_factories.CompanyFactory(customer=self.user.customer)
        sitio_company_2 = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = sitio_company
        form_data = {'sitio_name': "Tamaulipas", 'sitio_location': "Some place", 'company': sitio_company_2.id}
        view = self.get_instance(
            SitioCreationView,
            request=self.request
        )
        view.get_context_data = lambda form: {}
        form = SitioForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertFalse(hasattr(SitioCreationView, 'object'))
        self.assertEqual(view.form_valid(form).status_code, 200)


class DestinatarioCreationTest(BaseViewTest):
    def test_get_initial_returns_the_correct_company(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        dicc = {"company": destinatario_company}
        view = self.get_instance(
            DestinatarioCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_destinatario_form_creation_is_valid(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = destinatario_company
        form_data = {'company': destinatario_company.id, 'destinatario_text': "Un wey"}
        view = self.get_instance(
            DestinatarioCreationView,
            request=self.request
        )
        form = DestinatarioForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertTrue(view.form_valid(form))

    def test_destinatario_form_creation_is_not_valid_with_another_company(self):
        destinatario_company = user_factories.CompanyFactory(customer=self.user.customer)
        destinatario_company_2 = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = destinatario_company
        form_data = {'company': destinatario_company_2.id, 'destinatario_text': "Un wey"}
        view = self.get_instance(
            DestinatarioCreationView,
            request=self.request
        )
        view.get_context_data = lambda form: {}
        form = DestinatarioForm(data=form_data)
        validez = form.is_valid()
        self.assertTrue(validez)
        self.assertFalse(hasattr(DestinatarioCreationView, 'object'))
        self.assertEqual(view.form_valid(form).status_code, 200)


class ContratoEditViewTest(BaseViewTest):
    def test_obtiene_objeto_correctamente(self):
        contrato = factories.ContratoFactory(cliente__company__customer=self.user.customer)
        self.user.currently_at = contrato.cliente.company
        view = self.get_instance(
            ContratoEditView,
            request=self.request,
            pk=contrato.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_get_object_raises_404_not_currently_at(self):
        contrato = factories.ContratoFactory(cliente__company__customer=self.user.customer)
        view = self.get_instance(
            ContratoEditView,
            request=self.request,
            pk=contrato.pk
        )
        with self.assertRaises(Http404):
            view.get_object()

class CatalogoConceptosInlineFormTest(BaseViewTest):
    def test_get_correct_contract_object(self):
        company_inline = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_inline
        cliente_inline = factories.ClienteFactory(company=company_inline)
        contrato_inline = factories.ContratoFactory(cliente=cliente_inline)
        view = self.get_instance(
            CatalogoConceptosInlineFormView,
            request=self.request,
            pk=contrato_inline.pk
        )
        test_obj = view.get_object()
        self.assertEqual(test_obj, contrato_inline)

    def test_correct_success_url(self):
        company_inline = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_inline
        cliente_inline = factories.ClienteFactory(company=company_inline)
        contrato_inline = factories.ContratoFactory(cliente=cliente_inline)
        view = self.get_instance(
            CatalogoConceptosInlineFormView,
            request=self.request,
            pk=contrato_inline.pk
        )
        test_url = '/proyectos/contrato/detalle/%i/' % contrato_inline.pk
        self.assertEqual(view.get_success_url(), test_url)


class CatalogoConceptosTest(BaseViewTest):
    def test_json_formed_correctly(self):
        company = user_factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = company
        unit = factories.UnitFactory(unit='meter')
        cliente = factories.ClienteFactory(company=company)
        contrato = factories.ContratoFactory(cliente=cliente)
        for iterator in range(3):
            factories.ConceptoFactory(
                code=str(iterator),
                concept_text='text_%s' % iterator,
                unit=unit,
                total_cuantity=1000 + iterator,
                unit_price=2 + iterator,
                project=contrato,
            )
        response = self.get(
                CatalogoConceptos,
                pk=contrato.pk,
                request=self.request,
        )
        JSON_test = {
            'conceptos': [
                {
                    'code': '0',
                    'concept_text': 'text_0',
                    'unit': 'meter',
                    'cuantity': '1000.00',
                    'unit_price': '2.00',
                },
                {
                    'code': '1',
                    'concept_text': 'text_1',
                    'unit': 'meter',
                    'cuantity': '1001.00',
                    'unit_price': '3.00',
                },
                {
                    'code': '2',
                    'concept_text': 'text_2',
                    'unit': 'meter',
                    'cuantity': '1002.00',
                    'unit_price': '4.00',
                },

            ],
        }
        JSON_test = json.dumps(JSON_test)
        JSON_view = str(response.content, encoding='utf-8')
        self.assertJSONEqual(JSON_view, JSON_test)


class ClienteAutocompleteTest(BaseViewTest):
    def test_if_autocomplete_returns_the_correct_cliente_object(self):
        company_autocomplete = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        cliente = factories.ClienteFactory(cliente_name="ÁáRón", company=company_autocomplete)
        cliente_2 = factories.ClienteFactory(cliente_name="äAROn", company=company_autocomplete)
        view = self.get_instance(
            ClienteAutocomplete,
            request=self.request,
        )
        view.q = "aar"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [cliente, cliente_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)


class SitioAutocompleteTest(BaseViewTest):
    def test_if_autocomplete_returns_the_correct_sitio_object(self):
        company_autocomplete = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        sitio = factories.SitioFactory(sitio_name="PÁbellón de Arteaga", company=company_autocomplete)
        sitio_2 = factories.SitioFactory(sitio_name="Pabéllón del Sol", company=company_autocomplete)
        view = self.get_instance(
            SitioAutocomplete,
            request=self.request,
        )
        view.q = "Pábé"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [sitio, sitio_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)


class UnitAutocompleteTest(BaseViewTest):
    def test_if_autocomplete_returns_the_correct_unit_object(self):
        company_autocomplete = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        unit = factories.UnitFactory(unit="Kilo")
        unit_2 = factories.UnitFactory(unit="Kilogramo")
        view = self.get_instance(
            UnitAutocomplete,
            request=self.request,
        )
        view.q = "kil"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [unit, unit_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)

    def test_if_autocomplete_returns_the_correct_key_words(self):
        company_autocomplete = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        view = self.get_instance(
            UnitAutocomplete,
            request=self.request,
        )
        view.q = "some search"
        dicc = {'unit__unaccent__icontains': view.q}
        dicc_test = view.get_key_words()
        self.assertDictEqual(dicc, dicc_test)
