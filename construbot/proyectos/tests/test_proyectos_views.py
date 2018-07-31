import json
import decimal
from unittest import mock
from django.shortcuts import reverse
from django.core.management import call_command
from django.utils.six import StringIO
from django.test import RequestFactory, tag
from django.contrib.auth.models import Group
from django.http import Http404
from construbot.users.tests import utils
from construbot.proyectos import views
from construbot.proyectos.models import Destinatario, Sitio, Cliente, Contrato, Estimate
from construbot.users.models import User, Company, Customer
from . import factories


class BaseViewTest(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)

    def assertNotRaises(self, func, exception, message):
        try:
            func()
        except exception:
            self.fail(message)


class ProyectDashboardViewTest(BaseViewTest):

    def test_view_gets_correct_object(self):
        pdv = views.ProyectDashboardView
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        proyectos_group = Group.objects.create(name='Proyectos')
        pdv.user_groups = [proyectos_group]
        pdv.permiso_administracion = True
        view = self.get_instance(
            views.ProyectDashboardView,
            request=self.request
        )
        obj = view.get_context_data()
        self.assertEqual(obj['object'], company_test)


class DynamicListTest(BaseViewTest):

    def test_context_contains_models_name(self):
        view = self.get_instance(
            views.DynamicList,
            request=self.request
        )
        view.model = mock.Mock()
        view.model.__name__ = 'Foo'
        view.get_menu = lambda: {}
        view.app_label_name = 'proyectos'
        view.permiso_administracion = True
        view.object_list = []
        context = view.get_context_data()
        self.assertIn('model', context)
        self.assertEqual(context['model'], 'Foo')


class DynamicDetailTest(BaseViewTest):

    def test_DynamicListView_returns_correct_object_name_for_template(self):
        view = self.get_instance(
            views.DynamicDetail,
            request=self.request
        )
        object_name = view.get_context_object_name(Contrato())
        self.assertEqual(object_name, 'contrato')


class ContratoListTest(BaseViewTest):
    def test_contrato_different_customer_doesnt_appear(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        cliente_test = factories.ClienteFactory(company=company_test)
        contrato = factories.ContratoFactory(cliente=cliente_test)
        contrato_2 = factories.ContratoFactory()
        contrato_3 = factories.ContratoFactory(cliente=cliente_test)
        view = self.get_instance(
            views.ContratoListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(y) for y in sorted([contrato, contrato_3], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(qs, qs_test)


class ClienteListTest(BaseViewTest):
    def test_cliente_query_only_same_client(self):
        cliente_company = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        cliente = factories.ClienteFactory(company=cliente_company, cliente_name='cliente_bLdYMUBC')
        cliente_2 = factories.ClienteFactory(company=cliente_company, cliente_name='cliente_JBFQADJV')
        cliente_3 = factories.ClienteFactory()
        view = self.get_instance(
            views.ClienteListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(a) for a in sorted([cliente, cliente_2], key=lambda x: repr(x).lower(), reverse=False)]
        self.assertQuerysetEqual(qs, qs_test)


class SitioListTest(BaseViewTest):
    def test_sitio_query_only_same_company(self):
        sitio_company = factories.CompanyFactory(customer=self.user.customer)
        sitio_cliente = factories.ClienteFactory(company=sitio_company)
        self.user.currently_at = sitio_company
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        sitio_2 = factories.SitioFactory(cliente__company=sitio_company)
        sitio_3 = factories.SitioFactory()
        view = self.get_instance(
            views.SitioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted([sitio, sitio_2], key=lambda x: repr(x).lower(), reverse=False)]
        self.assertQuerysetEqual(qs, qs_test)


class DestinatarioListTest(BaseViewTest):
    def test_destinatario_query_same_client_company(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario_cliente_2 = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        destinatario_2 = factories.DestinatarioFactory(cliente=destinatario_cliente_2)
        destinatario_3 = factories.DestinatarioFactory()
        view = self.get_instance(
            views.DestinatarioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted(
            [destinatario, destinatario_2], key=lambda x: repr(x).lower(), reverse=False
        )]
        self.assertQuerysetEqual(qs, qs_test)


class ContratoDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_contrato_object(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        view = self.get_instance(
            views.ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_assert_contrato_request_returns_404_with_no_currently_at(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        view = self.get_instance(
            views.ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            obj = view.get_object()


class ClienteDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_cliente_object(self):
        cliente_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = cliente_company
        cliente = factories.ClienteFactory(company=cliente_company)
        view = self.get_instance(
            views.ClienteDetailView,
            pk=cliente.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, cliente)

    def test_assert_cliente_request_returns_404_with_no_currently_at(self):
        cliente_company = factories.CompanyFactory(customer=self.user.customer)
        cliente = factories.ClienteFactory(company=cliente_company)
        view = self.get_instance(
            views.ClienteDetailView,
            pk=cliente.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            obj = view.get_object()


class SitioDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_sitio_object(self):
        sitio_company = factories.CompanyFactory(customer=self.user.customer)
        sitio_cliente = factories.ClienteFactory(company=sitio_company)
        self.request.user.currently_at = sitio_company
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        view = self.get_instance(
            views.SitioDetailView,
            pk=sitio.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, sitio)

    def test_assert_sitio_request_returns_404_with_no_currently_at(self):
        sitio_company = factories.CompanyFactory(customer=self.user.customer)
        sitio_cliente = factories.ClienteFactory(company=sitio_company)
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        view = self.get_instance(
            views.SitioDetailView,
            pk=sitio.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            view.get_object()


class DestinatarioDetailTest(BaseViewTest):
    def test_assert_request_returns_correct_destinatario_object(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        view = self.get_instance(
            views.DestinatarioDetailView,
            pk=destinatario.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, destinatario)

    def test_assert_request_returns_404_with_no_currently_at(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        view = self.get_instance(
            views.DestinatarioDetailView,
            pk=destinatario.pk,
            request=self.request
        )
        with self.assertRaises(Http404):
            view.get_object()


class ContratoCreationTest(BaseViewTest):
    def test_get_initial_returns_1_when_no_contratos(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        dicc = {"currently_at": contrato_company.company_name, "folio": 1}
        view = self.get_instance(
            views.ContratoCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_get_initial_returns_the_next_id_when_contratos_exist(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        self.request.user.currently_at = contrato_company
        dicc = {"currently_at": contrato_company.company_name, "folio": contrato.folio + 1}
        view = self.get_instance(
            views.ContratoCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_get_context_data_has_same_company_that_currently_at(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        view = self.get_instance(
            views.ContratoCreationView,
            request=self.request
        )
        view.get_menu = lambda: []
        view.permiso_administracion = True
        view.object = None
        dicc_test = view.get_context_data()
        self.assertEqual(dicc_test['company'], contrato_company)

    def test_contrato_form_creation_is_not_valid_with_another_company(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_company_2 = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     'currently_at': contrato_company_2.company_name,
                     }
        with mock.patch('construbot.proyectos.views.ContratoCreationView.get_form_kwargs') as get_form_mock:
            view = self.get_instance(
                views.ContratoCreationView,
                request=self.request
            )
            get_form_mock.return_value = {'data': form_data}
            form = view.get_form()
            view.get_context_data = lambda form: {'form': form}
            view.context = view.get_context_data(form)
            self.assertFalse(hasattr(view, 'object'))
            self.assertEqual(view.post(request=self.request).status_code, 200)
            self.assertFormError(view, 'form', None,
                                 'Actualmente te encuentras en otra compañia, '
                                 'es necesario recargar y repetir el proceso.'
                                 )


class ClienteCreationTest(BaseViewTest):
    def test_get_initial_returns_the_correct_company(self):
        cliente_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = cliente_company
        dicc = {"company": cliente_company}
        view = self.get_instance(
            views.ClienteCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_cliente_form_creation_is_not_valid_with_another_company(self):
        cliente_company = factories.CompanyFactory(customer=self.user.customer)
        cliente_company_2 = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = cliente_company
        form_data = {'cliente_name': "Juanito", 'company': cliente_company_2.id}
        with mock.patch('construbot.proyectos.views.ClienteCreationView.get_form_kwargs') as get_form_mock:
            view = self.get_instance(
                views.ClienteCreationView,
                request=self.request
            )
            get_form_mock.return_value = {'data': form_data}
            form = view.get_form()
            view.get_context_data = lambda form: {'form': form}
            view.context = view.get_context_data(form)
            self.assertFalse(hasattr(view, 'object'))
            self.assertEqual(view.post(request=self.request).status_code, 200)
            self.assertFormError(view, 'form', None,
                                 'Actualmente te encuentras en otra compañia, '
                                 'es necesario recargar y repetir el proceso.'
                                 )


class SitioCreationTest(BaseViewTest):
    def test_get_initial_returns_the_correct_company(self):
        sitio_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = sitio_company
        dicc = {"company": sitio_company}
        view = self.get_instance(
            views.SitioCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)


class DestinatarioCreationTest(BaseViewTest):
    def test_get_initial_returns_the_correct_company(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        dicc = {"company": destinatario_company}
        view = self.get_instance(
            views.DestinatarioCreationView,
            request=self.request
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    @mock.patch('construbot.proyectos.views.DestinatarioDetailView.get_context_data')
    def test_destinatario_form_redirects_correctly(self, mock_detail_context):
        with mock.patch('construbot.proyectos.views.DestinatarioCreationView.test_func') as mock_test_func:
            destinatario_company = factories.CompanyFactory(customer=self.user.customer)
            destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
            self.user.currently_at = destinatario_company
            self.user.save()
            self.user.company.add(destinatario_company)
            form_data = {
                'company': destinatario_company.id,
                'destinatario_text': 'Un wey',
                'cliente': destinatario_cliente.id
            }
            self.client.login(username=self.user.username, password='password')
            mock_test_func.return_value = True
            response = self.client.post(self.reverse('proyectos:nuevo_destinatario'), data=form_data)
            new_destinatario = Destinatario.objects.get(destinatario_text='Un wey')
            with mock.patch('construbot.proyectos.views.DestinatarioDetailView.test_func') as detail_mock:
                mock_detail_context.return_value = {}
                detail_mock.return_value = True
                self.assertRedirects(response, '/proyectos/destinatario/detalle/%s/' % new_destinatario.id)


class EstimateCreationTest(BaseViewTest):

    def test_estimate_post_correctly(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        proyectos_group = Group.objects.create(name='Proyectos')
        destinatario = factories.DestinatarioFactory(cliente=cliente_contrato)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(proyectos_group)
        self.client.login(username=self.user.username, password='password')
        form_data = {
            'consecutive': '3',
            'supervised_by': str(self.user.id),
            'start_date': '2018-04-29',
            'finish_date': '2018-05-15',
            'draft_by': str(self.user.id),
            'project': str(contrato.id),
            'auth_by': str(destinatario.id),
            'auth_date': '2018-05-15',
            'estimateconcept_set-TOTAL_FORMS': '1',
            'estimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-MAX_NUM_FORMS': '5',
            'estimateconcept_set-0-concept': concepto_1.concept_text,
            'estimateconcept_set-0-largo': '10',
            'estimateconcept_set-0-ancho': '10',
            'estimateconcept_set-0-alto': '10',
            'estimateconcept_set-0-cuantity_estimated': '2',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertNotRaises(
            lambda: Estimate.objects.get(project=contrato),
            Estimate.DoesNotExist,
            'La estimacion no fue creada.'
        )
        self.assertRedirects(
            response, reverse('proyectos:contrato_detail', kwargs={'pk': contrato.pk})
        )

    def test_estimate_post_renders_errors(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        proyectos_group = Group.objects.create(name='Proyectos')
        destinatario = factories.DestinatarioFactory(cliente=factories.ClienteFactory())
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(proyectos_group)
        self.client.login(username=self.user.username, password='password')
        form_data = {
            'consecutive': '3',
            'supervised_by': str(self.user.id),
            'start_date': '2018-04-29',
            'finish_date': '2018-05-15',
            'draft_by': str(self.user.id),
            'project': str(contrato.id),
            'auth_by': str(destinatario.id),
            'auth_date': '2018-05-15',
            'estimateconcept_set-TOTAL_FORMS': '1',
            'estimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-MAX_NUM_FORMS': '5',
            'estimateconcept_set-0-concept': concepto_1.concept_text,
            'estimateconcept_set-0-cuantity_estimated': '2',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertFormError(response, 'form', None, 'Destinatarios y contratos no pueden ser de empresas diferentes')

    def test_estimate_post_pagada_sin_fecha_pago(self):
        contrato = factories.ContratoFactory()
        proyectos_group = Group.objects.create(name='Proyectos')
        destinatario = factories.DestinatarioFactory(cliente=contrato.cliente)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato.cliente.company)
        self.user.currently_at = contrato.cliente.company
        self.user.groups.add(proyectos_group)
        self.client.login(username=self.user.username, password='password')
        form_data = {
            'consecutive': '3',
            'supervised_by': str(self.user.id),
            'start_date': '2018-04-29',
            'finish_date': '2018-05-15',
            'draft_by': str(self.user.id),
            'project': str(contrato.id),
            'auth_by': str(destinatario.id),
            'auth_date': '2018-05-15',
            'paid': True,
            'payment_date': '',
            'estimateconcept_set-TOTAL_FORMS': '1',
            'estimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-MAX_NUM_FORMS': '5',
            'estimateconcept_set-0-concept': concepto_1.concept_text,
            'estimateconcept_set-0-cuantity_estimated': '2',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertFormError(
            response, 'form', 'payment_date', 'Si la estimación fué pagada, es necesaria fecha de pago.'
        )

    def test_estimate_createview_renders_formset_errors(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(cliente=contrato_cliente)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        proyectos_group = Group.objects.create(name='Proyectos')
        destinatario = factories.DestinatarioFactory(cliente=cliente_contrato)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(proyectos_group)
        self.client.login(username=self.user.username, password='password')
        form_data = {
            'consecutive': '3',
            'supervised_by': str(self.user.id),
            'start_date': '2018-04-29',
            'finish_date': '2018-05-15',
            'draft_by': str(self.user.id),
            'project': str(contrato.id),
            'auth_by': str(destinatario.id),
            'auth_date': '2018-05-15',
            'estimateconcept_set-TOTAL_FORMS': '1',
            'estimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-MAX_NUM_FORMS': '5',
            'estimateconcept_set-0-concept': concepto_1.concept_text,
            'estimateconcept_set-0-cuantity_estimated': 'a',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertFormsetError(response, 'generator_inline_concept', 0, 'cuantity_estimated', ['Enter a number.'])
        self.assertEqual(response.status_code, 200)


class EstimateEditTest(BaseViewTest):

    def test_estimate_edit_saves_forms_when_valid(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        cliente = factories.ClienteFactory(company=company)
        contrato = factories.ContratoFactory(cliente=cliente)
        estimacion = factories.EstimateFactory(project=contrato)
        request = RequestFactory().post(
            reverse('proyectos:editar_estimacion', kwargs={'pk': estimacion.pk}),
            data={'dato': 'dato'}
        )
        view = self.get_instance(
            views.EstimateEditView,
            request=request,
            pk=contrato.pk
        )
        view.object = estimacion
        with mock.patch('construbot.proyectos.forms.estimateConceptInlineForm') as mock_function:
            mock_formset_instance = mock.Mock()
            mock_formset = mock_formset_instance()
            mock_formset.is_valid.return_value = True
            mock_function.return_value = mock_formset_instance
            mock_form = mock.Mock()
            view.form_valid(mock_form)
        self.assertTrue(mock_form.save.called)
        self.assertTrue(mock_formset.is_valid.called)
        self.assertTrue(mock_formset.save.called)

    @mock.patch.object(views.EstimateEditView, 'form_invalid')
    def test_estimate_edit_executes_form_invalid_on_formset_invalid(self, mock_method):
        company = factories.CompanyFactory(customer=self.user.customer)
        cliente = factories.ClienteFactory(company=company)
        contrato = factories.ContratoFactory(cliente=cliente)
        estimacion = factories.EstimateFactory(project=contrato)
        request = RequestFactory().post(
            reverse('proyectos:editar_estimacion', kwargs={'pk': estimacion.pk}),
            data={'dato': 'dato'}
        )
        view = self.get_instance(
            views.EstimateEditView,
            request=request,
            pk=contrato.pk
        )
        view.object = estimacion
        with mock.patch('construbot.proyectos.forms.estimateConceptInlineForm') as mock_function:
            mock_formset_instance = mock.Mock()
            mock_formset = mock_formset_instance()
            mock_formset.is_valid.return_value = False
            mock_function.return_value = mock_formset_instance
            mock_form = mock.Mock()
            view.form_valid(mock_form)
        self.assertTrue(mock_form.save.called)
        self.assertTrue(mock_formset.is_valid.called)
        self.assertFalse(mock_formset.save.called)
        self.assertTrue(mock_method.caled)

    @mock.patch.object(views.EstimateEditView, 'form_invalid')
    def test_estimate_edit_returns_same_formset_on_errors(self, mock_method):
        company = factories.CompanyFactory(customer=self.user.customer)
        cliente = factories.ClienteFactory(company=company)
        contrato = factories.ContratoFactory(cliente=cliente)
        estimacion = factories.EstimateFactory(project=contrato)
        view = self.get_instance(
            views.EstimateEditView,
            request=self.request,
            pk=contrato.pk
        )
        view.object = estimacion
        with mock.patch('construbot.proyectos.forms.estimateConceptInlineForm') as mock_function:
            mock_formset_klass = mock.Mock()
            # mock_formset = mock_formset_klass()
            mock_formset = mock.Mock()
            mock_formset_klass.return_value = mock_formset
            mock_formset.is_valid.return_value = False
            mock_function.return_value = mock_formset_klass
            mock_form = mock.Mock()
            view.form_valid(mock_form)
            view.conceptForm = view.get_formset_for_context()
        with self.assertRaises(AssertionError):
            # nunca fue llamado, por lo tanto se levanta el error
            mock_function().assert_any_call(instance=view.object)
        # son dos llamados, una por la prueba y otra por la sentencia anterior...
        self.assertEqual(mock_function.call_count, 2)
        mock_formset_klass.assert_called_with(
            self.request.POST,
            self.request.FILES,
            instance=estimacion
        )
        try:
            mock_formset_klass.assert_called_once()
            mock_formset.is_valid.assert_called_once()
        except AttributeError:
            # compatibilidad con python 3.5
            self.assertEqual(mock_formset_klass.call_count, 1)
            self.assertTrue(mock_formset.is_valid.call_count, 1)


class ContratoEditViewTest(BaseViewTest):
    def test_obtiene_objeto_correctamente(self):
        contrato = factories.ContratoFactory(cliente__company__customer=self.user.customer)
        self.user.currently_at = contrato.cliente.company
        view = self.get_instance(
            views.ContratoEditView,
            request=self.request,
            pk=contrato.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_get_object_raises_404_not_currently_at(self):
        contrato = factories.ContratoFactory(cliente__company__customer=self.user.customer)
        view = self.get_instance(
            views.ContratoEditView,
            request=self.request,
            pk=contrato.pk
        )
        with self.assertRaises(Http404):
            view.get_object()

    def test_get_initial_has_currently_at(self):
        contrato = factories.ContratoFactory(cliente__company__customer=self.user.customer)
        self.user.currently_at = contrato.cliente.company
        view = self.get_instance(
            views.ContratoEditView,
            request=self.request,
            pk=contrato.pk
        )
        init_obj = view.get_initial()
        self.assertTrue('currently_at' in init_obj)
        self.assertEqual(init_obj['currently_at'], self.user.currently_at.company_name)

    def test_contrato_edit_not_currently_returns_invalid(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        form_data = {'folio': 1, 'code': 'TEST-1', 'fecha': '1999-12-1', 'contrato_name': 'TEST CONTRATO 1',
                     'contrato_shortName': 'TC1', 'cliente': contrato_cliente.id, 'sitio': contrato_sitio.id,
                     'monto': 1222.12,
                     }
        with mock.patch('construbot.proyectos.views.ContratoEditView.get_form_kwargs') as get_form_mock:
            view = self.get_instance(
                views.ContratoEditView,
                request=self.request,
                pk=contrato_factory.pk
            )
            get_form_mock.return_value = {'data': form_data}
            form = view.get_form()
            view.get_context_data = lambda form: {'form': form}
            view.context = view.get_context_data(form)
            contrato = Contrato.objects.get(pk=contrato_factory.pk)
            self.assertEqual(contrato.monto, decimal.Decimal('90.00'))
            self.assertEqual(view.post(request=self.request).status_code, 200)
            self.assertFormError(view, 'form', 'currently_at', 'This field is required.')


class ClienteEditTest(BaseViewTest):
    def test_obtiene_objeto_cliente_correctamente(self):
        cliente = factories.ClienteFactory()
        self.user.currently_at = cliente.company
        view = self.get_instance(
            views.ClienteEditView,
            request=self.request,
            pk=cliente.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, cliente)

    def test_get_cliente_object_raises_404_not_currently_at(self):
        cliente = factories.ClienteFactory()
        view = self.get_instance(
            views.ClienteEditView,
            request=self.request,
            pk=cliente.pk,
        )
        with self.assertRaises(Http404):
            view.get_object()

    def test_get_cliente_initial_has_company(self):
        cliente = factories.ClienteFactory()
        self.user.currently_at = cliente.company
        view = self.get_instance(
            views.ClienteEditView,
            request=self.request,
            pk=cliente.pk,
        )
        init_obj = view.get_initial()
        self.assertTrue('company' in init_obj)
        self.assertEqual(init_obj['company'], self.user.currently_at)


class SitioEditTest(BaseViewTest):
    def test_obtiene_objeto_sitio_correctamente(self):
        sitio = factories.SitioFactory()
        self.user.currently_at = sitio.cliente.company
        view = self.get_instance(
            views.SitioEditView,
            request=self.request,
            pk=sitio.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, sitio)

    def test_get_sitio_object_raises_404_not_currently_at(self):
        sitio = factories.SitioFactory()
        view = self.get_instance(
            views.SitioEditView,
            request=self.request,
            pk=sitio.pk,
        )
        with self.assertRaises(Http404):
            view.get_object()

    def test_sitio_get_initial_has_company(self):
        sitio = factories.SitioFactory()
        self.user.currently_at = sitio.cliente.company
        view = self.get_instance(
            views.SitioEditView,
            request=self.request,
            pk=sitio.pk,
        )
        init = view.get_initial()
        self.assertTrue('company' in init)
        self.assertEqual(init['company'], self.user.currently_at)


class DestinatarioEditTest(BaseViewTest):
    def test_obtiene_objeto_destinatario_correctamente(self):
        destinatario = factories.DestinatarioFactory()
        self.user.currently_at = destinatario.cliente.company
        view = self.get_instance(
            views.DestinatarioEditView,
            request=self.request,
            pk=destinatario.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, destinatario)

    def test_get_destinatario_object_raises_404_not_currently_at(self):
        destinatario = factories.DestinatarioFactory()
        view = self.get_instance(
            views.DestinatarioEditView,
            request=self.request,
            pk=destinatario.pk,
        )
        with self.assertRaises(Http404):
            view.get_object()

    def test_destinatario_get_initial_has_company(self):
        destinatario = factories.DestinatarioFactory()
        self.user.currently_at = destinatario.cliente.company
        view = self.get_instance(
            views.DestinatarioEditView,
            request=self.request,
            pk=destinatario.pk,
        )
        init = view.get_initial()
        self.assertTrue('company' in init)
        self.assertEqual(init['company'], self.user.currently_at)


class CatalogoConceptosInlineFormTest(BaseViewTest):
    def test_get_correct_contract_object(self):
        company_inline = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_inline
        cliente_inline = factories.ClienteFactory(company=company_inline)
        contrato_inline = factories.ContratoFactory(cliente=cliente_inline)
        view = self.get_instance(
            views.CatalogoConceptosInlineFormView,
            request=self.request,
            pk=contrato_inline.pk
        )
        test_obj = view.get_object()
        self.assertEqual(test_obj, contrato_inline)

    def test_correct_success_url(self):
        company_inline = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_inline
        cliente_inline = factories.ClienteFactory(company=company_inline)
        contrato_inline = factories.ContratoFactory(cliente=cliente_inline)
        view = self.get_instance(
            views.CatalogoConceptosInlineFormView,
            request=self.request,
            pk=contrato_inline.pk
        )
        test_url = '/proyectos/contrato/detalle/%i/' % contrato_inline.pk
        self.assertEqual(view.get_success_url(), test_url)


class CatalogoConceptosTest(BaseViewTest):
    def test_json_formed_correctly(self):
        company = factories.CompanyFactory(customer=self.user.customer)
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
                views.CatalogoConceptos,
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


class DynamicDeleteTest(BaseViewTest):

    @mock.patch('django.shortcuts.get_object_or_404')
    def test_get_object_calls_get_obj_or_404(self, mock_404):
        contrato = factories.ContratoFactory()
        mock_404.return_value = contrato
        self.user.currently_at = contrato.cliente.company
        view = self.get_instance(
            views.DynamicDelete,
            request=self.request,
            model='Contrato',
            pk=contrato.pk
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)
        try:
            mock_404.assert_called_once()
        except AttributeError:
            self.assertEqual(mock_404.call_count, 1)

    def test_dynamic_delete_gets_object(self):
        company_delete = factories.CompanyFactory(customer=self.user.customer)
        cliente_delete = factories.ClienteFactory(company=company_delete)
        contrato_object = factories.ContratoFactory(folio=1, cliente=cliente_delete)
        request = RequestFactory().post(
            reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_object.pk}),
            data={'value': 'confirm'}
        )
        request.user = self.user
        self.user.currently_at = company_delete
        view = self.get_instance(
            views.DynamicDelete,
            request=request,
            model='Contrato',
            pk=contrato_object.pk
        )
        view_obj = view.get_object()
        self.assertEqual(contrato_object, view_obj)

    @mock.patch.object(views.DynamicDelete, 'get_object')
    def test_delete_method_calls_functions(self, mock_object):
        with mock.patch.object(views.DynamicDelete, 'folio_handling', return_value=None) as mock_folio:
            contrato_delete = mock.Mock()
            contrato_delete.pk = 1
            request = RequestFactory().post(
                reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_delete.pk}),
                data={'value': 'confirm'}
            )
            view = self.get_instance(
                views.DynamicDelete,
                request=request,
            )
            response = view.delete(request)
        try:
            mock_object.assert_called_once()
        except AttributeError:
            self.assertEqual(mock_object.call_count, 1)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"exito": True})

    @mock.patch.object(views.DynamicDelete, 'get_company_query')
    def test_folio_handling_perfoms_correct_qs(self, mock_query):
        company_delete = factories.CompanyFactory(customer=self.user.customer)
        cliente_delete = factories.ClienteFactory(company=company_delete)
        contrato_delete = factories.ContratoFactory(folio=1, cliente=cliente_delete)
        contrato_delete_2 = factories.ContratoFactory(folio=2, cliente=cliente_delete)
        contrato_delete_3 = factories.ContratoFactory(folio=3, cliente=cliente_delete)
        self.user.currently_at = company_delete
        request = RequestFactory().post(
            reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_delete.pk}),
            data={'value': 'confirm'}
        )
        request.user = self.user
        view = self.get_instance(
            views.DynamicDelete,
            request=request,
            model='Contrato',
            pk=contrato_delete.pk
        )
        view.object = contrato_delete
        view.model = contrato_delete._meta.model
        mock_query.return_value = (
            {'cliente__company': self.user.currently_at, 'folio__gt': view.object.folio}, 'folio'
        )
        view.folio_handling()
        contrato_delete_2.refresh_from_db()
        contrato_delete_3.refresh_from_db()
        try:
            mock_query.assert_called_once()
        except AttributeError:
            self.assertEqual(mock_query.call_count, 1)
        self.assertEqual(contrato_delete_2.folio, 1)
        self.assertEqual(contrato_delete_3.folio, 2)

    @mock.patch.object(views.DynamicDelete, 'get_object')
    def test_get_company_query_with_estimate(self, mock_object):
        estimate = factories.EstimateFactory()
        mock_object.return_value = estimate
        request = RequestFactory().post(
            reverse('proyectos:eliminar', kwargs={'model': 'Estimate', 'pk': estimate.pk}),
            data={'value': 'confirm'}
        )
        self.user.currently_at = estimate.project.cliente.company
        request.user = self.user
        view = self.get_instance(
            views.DynamicDelete,
            request=request,
            model='Estimate',
            pk=estimate.pk
        )
        view.object = view.get_object()
        control_dict = {
            'project__cliente__company': self.request.user.currently_at,
            'consecutive__gt': estimate.consecutive
        }
        kwargs, field = view.get_company_query('Estimate')
        self.assertDictEqual(kwargs, control_dict)

    @mock.patch.object(views.DynamicDelete, 'get_object')
    def test_get_company_query_with_contrato(self, mock_object):
        contrato = factories.ContratoFactory()
        mock_object.return_value = contrato
        request = RequestFactory().post(
            reverse('proyectos:eliminar', kwargs={'model': 'Estimate', 'pk': contrato.pk}),
            data={'value': 'confirm'}
        )
        self.user.currently_at = contrato.cliente.company
        request.user = self.user
        view = self.get_instance(
            views.DynamicDelete,
            request=request,
            model='Estimate',
            pk=contrato.pk
        )
        view.object = view.get_object()
        control_dict = {
            'cliente__company': self.request.user.currently_at,
            'folio__gt': contrato.folio
        }
        kwargs, field = view.get_company_query('Contrato')
        self.assertDictEqual(kwargs, control_dict)


class ClienteAutocompleteTest(BaseViewTest):
    def test_autocomplete_returns_the_correct_cliente_object(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        cliente = factories.ClienteFactory(cliente_name="ÁáRón", company=company_autocomplete)
        cliente_2 = factories.ClienteFactory(cliente_name="äAROn", company=company_autocomplete)
        view = self.get_instance(
            views.ClienteAutocomplete,
            request=self.request,
        )
        view.q = "aar"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [cliente, cliente_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)

    def test_if_cliente_autocomplete_returns_none(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        factories.ClienteFactory(cliente_name="ÁáRón", company=company_autocomplete)
        factories.ClienteFactory(cliente_name="äAROn", company=company_autocomplete)
        view = self.get_instance(
            views.ClienteAutocomplete,
            request=self.request,
        )
        view.q = ""
        qs = view.get_queryset()
        self.assertIsNone(qs)

    def test_cliente_get_key_words_returns_correct_dict(self):
        instance = views.ClienteAutocomplete()
        instance.q = 'hola'
        instance.create_field = 'cliente_name'
        self.request.user.currently_at = factories.CompanyFactory(customer=self.user.customer)
        instance.request = self.request
        dict_control = {
            'cliente_name__unaccent__icontains': 'hola',
            'company': self.request.user.currently_at
        }
        self.assertDictEqual(instance.get_key_words(), dict_control)

    def test_cliente_autocomplete_get_post_key_words_correct_dict(self):
        instance = views.ClienteAutocomplete()
        company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = company
        instance.request = self.request
        instance.q = 'hola'
        dict_control = {
            'company': self.request.user.currently_at
        }
        self.assertDictEqual(instance.get_post_key_words(), dict_control)

    def test_autocomplete_create_object_saves_db(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        request = RequestFactory().post(
            reverse('proyectos:cliente-autocomplete', kwargs={}),
            data={'text': 'nombre de cliente'}
        )
        request.user = self.user
        view = self.get_instance(
            views.ClienteAutocomplete,
            request=request,
        )
        view.q = request.GET.get('q', '')
        view.create_field = 'cliente_name'
        obj = view.create_object(request.POST.get('text'))
        self.assertEqual(obj.cliente_name, 'nombre de cliente')
        self.assertTrue(isinstance(obj.pk, int))


class SitioAutocompleteTest(BaseViewTest):
    def test_if_autocomplete_returns_the_correct_sitio_object(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        cliente_autocomplete = factories.ClienteFactory(company=company_autocomplete)
        self.user.currently_at = company_autocomplete
        sitio = factories.SitioFactory(sitio_name="PÁbellón de Arteaga", cliente=cliente_autocomplete)
        sitio_2 = factories.SitioFactory(sitio_name="Pabéllón del Sol", cliente=cliente_autocomplete)
        view = self.get_instance(
            views.SitioAutocomplete,
            request=self.request,
        )
        view.q = "Pábé"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [sitio, sitio_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)

    def test_if_sitio_autocomplete_returns_none(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        cliente_autocomplete = factories.ClienteFactory(company=company_autocomplete)
        self.user.currently_at = company_autocomplete
        factories.SitioFactory(sitio_name="PÁbellón de Arteaga", cliente=cliente_autocomplete)
        factories.SitioFactory(sitio_name="Pabéllón del Sol", cliente=cliente_autocomplete)
        view = self.get_instance(
            views.SitioAutocomplete,
            request=self.request,
        )
        view.q = ""
        qs = view.get_queryset()
        self.assertIsNone(qs)

    def test_sitio_get_post_kw_returns_correct_dict(self):
        instance = views.SitioAutocomplete()
        cliente = factories.ClienteFactory(company__customer=self.user.customer)
        self.user.currently_at = cliente.company
        instance.request = self.request
        instance.q = 'bla bla'
        instance.forwarded = {'cliente': str(cliente.id)}
        dict_control = {'cliente': cliente}
        self.assertDictEqual(instance.get_post_key_words(), dict_control)

    def test_integration_for_post_in_sitio(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        cliente_autocomplete = factories.ClienteFactory(company=company_autocomplete)
        self.user.currently_at = company_autocomplete
        request = RequestFactory().post(
            reverse('proyectos:sitio-autocomplete', kwargs={}),
            data={'text': 'nombre del sitio'}
        )
        request.user = self.user
        view = self.get_instance(
            views.SitioAutocomplete,
            request=request,
        )
        view.forwarded = {'cliente': str(cliente_autocomplete.id)}
        view.q = request.GET.get('q', '')
        view.create_field = 'sitio_name'
        obj = view.create_object(request.POST.get('text'))
        self.assertEqual(obj.sitio_name, 'nombre del sitio')
        self.assertTrue(isinstance(obj.pk, int))


class DestinatarioAutocompleteTest(BaseViewTest):

    def test_destinatario_autocomplete_returns_correct_dict(self):
        instance = views.DestinatarioAutocomplete()
        instance.q = 'hola'
        instance.create_field = 'destinatario_text'
        self.request.user.currently_at = factories.CompanyFactory(customer=self.user.customer)
        instance.request = self.request
        contrato = factories.ContratoFactory(cliente__company=self.request.user.currently_at)
        instance.forwarded = {'project': contrato.id}
        dict_control = {
            'destinatario_text__unaccent__icontains': 'hola',
            'cliente': contrato.cliente
        }
        self.assertDictEqual(instance.get_key_words(), dict_control)

    def test_destinatario_get_post_keywords_correct_dict(self):
        instance = views.DestinatarioAutocomplete()
        instance.create_field = 'destinatario_text'
        self.request.user.currently_at = factories.CompanyFactory(customer=self.user.customer)
        instance.request = self.request
        contrato = factories.ContratoFactory(cliente__company=self.request.user.currently_at)
        instance.forwarded = {'project': contrato.id}
        dict_control = {'cliente': contrato.cliente}
        self.assertDictEqual(instance.get_post_key_words(), dict_control)

    def test_integration_for_post_in_destinatario(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        contrato = factories.ContratoFactory(cliente__company=company_autocomplete)
        request = RequestFactory().post(
            reverse('proyectos:destinatario-autocomplete', kwargs={}),
            data={'text': 'nombre del destinatario'}
        )
        request.user = self.user
        view = self.get_instance(
            views.DestinatarioAutocomplete,
            request=request,
        )
        view.forwarded = {'project': contrato.id}
        view.q = request.GET.get('q', '')
        view.create_field = 'destinatario_text'
        obj = view.create_object(request.POST.get('text'))
        self.assertEqual(obj.destinatario_text, 'nombre del destinatario')
        self.assertTrue(isinstance(obj.pk, int))


class UnitAutocompleteTest(BaseViewTest):
    def test_unit_autocomplete_returns_the_correct_unit_object(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        unit = factories.UnitFactory(unit="Kilo")
        unit_2 = factories.UnitFactory(unit="Kilogramo")
        view = self.get_instance(
            views.UnitAutocomplete,
            request=self.request,
        )
        view.q = "kil"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [unit, unit_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)

    def test_unit_autocomplete_returns_the_correct_key_words(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        view = self.get_instance(
            views.UnitAutocomplete,
            request=self.request,
        )
        view.q = "some search"
        dicc = {'unit__unaccent__icontains': view.q}
        dicc_test = view.get_key_words()
        self.assertDictEqual(dicc, dicc_test)


class UserAutocompleteTest(BaseViewTest):

    def test_user_autocomplete_get_key_words(self):
        instance = views.UserAutocomplete()
        instance.q = 'Fulano'
        self.request.user.currently_at = factories.CompanyFactory(customer=self.user.customer)
        instance.request = self.request
        dict_control = {
            'username__unaccent__icontains': 'Fulano',
            'company': self.request.user.currently_at
        }
        self.assertDictEqual(instance.get_key_words(), dict_control)
