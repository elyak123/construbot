import json
import decimal
from io import StringIO
from unittest import mock
from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse
from django.test import RequestFactory, tag
from construbot.users.tests import utils
from construbot.proyectos import views
from construbot.proyectos.models import Destinatario, Contrato, Estimate
from construbot.users.tests import factories as user_factories
from . import factories


class BaseViewTest(utils.BaseTestCase):

    def setUp(self):
        super(BaseViewTest, self).setUp()
        self.request = self.get_request(self.user)

    def assertNotRaises(self, func, exception, message):
        try:
            func()
        except exception:
            self.fail(message)


class BaseViewTestTest(utils.BaseTestCase):

    @mock.patch.object(BaseViewTest, 'fail')
    def test_assert_not_raises(self, mock_fail):
        my_function = mock.Mock()
        function_result = mock.MagicMock()
        my_function.return_value = function_result
        instance = BaseViewTest()
        instance.assertNotRaises(my_function(), Exception, 'Not raised')
        my_function.assert_called_with()
        mock_fail.assert_not_called()


class ProyectDashboardViewTest(BaseViewTest):

    def test_view_gets_correct_object(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        view = self.get_instance(
            views.ProyectDashboardView,
            request=self.request
        )
        view.user_groups = [self.proyectos_group]
        view.nivel_permiso_usuario = self.request.user.nivel_acceso.nivel
        obj = view.get_context_data()
        self.assertEqual(obj['object'], company_test)


class DynamicListTest(BaseViewTest):

    def test_context_contains_models_name(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        view = self.get_instance(
            views.DynamicList,
            request=self.request
        )
        view.model = mock.Mock()
        view.model.__name__ = 'Foo'
        view.get_menu = lambda: {}
        view.app_label_name = 'proyectos'
        view.nivel_permiso_usuario = self.request.user.nivel_acceso.nivel
        view.object_list = []
        context = view.get_context_data()
        self.assertIn('model', context)
        self.assertEqual(context['model'], 'Foo')


class DynamicDetailTest(BaseViewTest):

    def test_DynamicDetailView_returns_correct_object_name_for_template(self):
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
        contrato = factories.ContratoFactory(contraparte=cliente_test)
        contrato.users.add(self.user)
        factories.ContratoFactory()  # Contrato # 2
        contrato_3 = factories.ContratoFactory(contraparte=cliente_test)
        contrato_3.users.add(self.user)
        view = self.get_instance(
            views.ContratoListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(y) for y in sorted([contrato, contrato_3], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(qs, qs_test)

    def test_contrato_same_customer_not_assigned_to_user_doesnt_appear(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        cliente_test = factories.ClienteFactory(company=company_test)
        contrato = factories.ContratoFactory(contraparte=cliente_test)
        contrato.users.add(self.user)
        factories.ContratoFactory(contraparte=cliente_test)  # Contrato # 2
        contrato_3 = factories.ContratoFactory(contraparte=cliente_test)
        contrato_3.users.add(self.user)
        view = self.get_instance(
            views.ContratoListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(y) for y in sorted([contrato, contrato_3], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(qs, qs_test)

    def test_contrato_same_customer_same_company_not_assigned_to_direccion_user_does_appear(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato = factories.ContratoFactory(contraparte__company=company_test)
        contrato_2 = factories.ContratoFactory(contraparte__company=company_test)  # Contrato # 2
        contrato_3 = factories.ContratoFactory(contraparte__company=company_test)
        view = self.get_instance(
            views.ContratoListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(y) for y in sorted([contrato, contrato_2, contrato_3], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(qs, qs_test)

    def test_contrato_same_customer_assigned_to_user_other_company_doesnt_appear(self):
        company_test_1 = factories.CompanyFactory(customer=self.user.customer)
        company_test_2 = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test_1
        cliente_test = factories.ClienteFactory(company=company_test_1)
        contrato = factories.ContratoFactory(contraparte=cliente_test)
        contrato.users.add(self.user)
        contrato_2 = factories.ContratoFactory(contraparte__company=company_test_2)
        contrato_3 = factories.ContratoFactory(contraparte=cliente_test)
        contrato_3.users.add(self.user)
        contrato_2.users.add(self.user)
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
        factories.ClienteFactory()
        contrato_1 = factories.ContratoFactory(contraparte=cliente)
        contrato_2 = factories.ContratoFactory(contraparte=cliente_2)
        self.user.contrato_set.add(contrato_1, contrato_2)
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
        factories.SitioFactory()
        contrato_1 = factories.ContratoFactory(sitio=sitio)
        contrato_2 = factories.ContratoFactory(sitio=sitio_2)
        self.user.contrato_set.add(contrato_1, contrato_2)
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
        destinatario = factories.DestinatarioFactory(contraparte=destinatario_cliente)
        destinatario_2 = factories.DestinatarioFactory(contraparte=destinatario_cliente_2)
        destinatario_3 = factories.DestinatarioFactory()
        contrato_1 = factories.ContratoFactory(contraparte=destinatario_cliente)
        contrato_2 = factories.ContratoFactory(contraparte=destinatario_cliente_2)
        self.user.contrato_set.add(contrato_1, contrato_2)
        view = self.get_instance(
            views.DestinatarioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted(
            [destinatario, destinatario_2], key=lambda x: repr(x).lower(), reverse=False
        )]
        self.assertQuerysetEqual(qs, qs_test)

    def test_destinatario_query_same_client_company_coordinador(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        self.request.user.nivel_acceso = self.coordinador_permission
        self.request.user.save()
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company, tipo='CLIENTE')
        destinatario_cliente_2 = factories.ClienteFactory(company=destinatario_company, tipo='CLIENTE')
        destinatario_cliente_3 = factories.ClienteFactory(company=destinatario_company, tipo='CLIENTE')
        destinatario = factories.DestinatarioFactory(contraparte=destinatario_cliente)
        destinatario_2 = factories.DestinatarioFactory(contraparte=destinatario_cliente_2)
        destinatario_3 = factories.DestinatarioFactory(contraparte=destinatario_cliente_3)
        contrato_1 = factories.ContratoFactory(contraparte=destinatario_cliente)
        contrato_2 = factories.ContratoFactory(contraparte=destinatario_cliente_2)
        contrato_3 = factories.ContratoFactory(contraparte=destinatario_cliente_3)
        self.user.contrato_set.add(contrato_1, contrato_2)
        view = self.get_instance(
            views.DestinatarioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted(
            [destinatario, destinatario_2], key=lambda x: repr(x).lower(), reverse=False
        )]
        self.assertQuerysetEqual(qs, qs_test)

    def test_destinatario_query_same_client_company_director(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        self.request.user.nivel_acceso = self.director_permission
        self.request.user.save()
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company, tipo='CLIENTE')
        destinatario_cliente_2 = factories.ClienteFactory(company=destinatario_company, tipo='CLIENTE')
        destinatario_cliente_3 = factories.ClienteFactory(company=destinatario_company, tipo='CLIENTE')
        destinatario = factories.DestinatarioFactory(contraparte=destinatario_cliente)
        destinatario_2 = factories.DestinatarioFactory(contraparte=destinatario_cliente_2)
        destinatario_3 = factories.DestinatarioFactory(contraparte=destinatario_cliente_3)
        view = self.get_instance(
            views.DestinatarioListView,
            request=self.request
        )
        qs = view.get_queryset()
        qs_test = [repr(q) for q in sorted(
            [destinatario, destinatario_2, destinatario_3], key=lambda x: repr(x).lower(), reverse=False
        )]
        self.assertQuerysetEqual(qs, qs_test)


class ContratoDetailTest(BaseViewTest):

    def test_assert_request_returns_correct_contrato_object(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        contrato.users.add(self.request.user)
        view = self.get_instance(
            views.ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_assert_request_returns_correct_contrato_object_not_assigned_admin_user(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        self.request.user.groups.add(self.admin_group)
        view = self.get_instance(
            views.ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_assert_contrato_request_returns_permissiondenied_without_its_company(self):
        contrato = factories.ContratoFactory(contraparte__company__customer=self.user.customer)
        view = self.get_instance(
            views.ContratoDetailView,
            pk=contrato.pk,
            request=self.request
        )
        with self.assertRaises(PermissionDenied):
            view.get_object()


class SubcontratosReportTest(BaseViewTest):

    @mock.patch.object(views.DynamicDetail, 'get_context_data')
    @mock.patch.object(Estimate, 'especial')
    @mock.patch.object(views.SubcontratosReport, 'test_func', return_value=True)
    def test_report_context_data_complete(self, mock_test_func, mock_especial, mock_context):
        with mock.patch('construbot.proyectos.views.path_processing') as path_processing:
            path_processing.return_value = 'somepath'
            mock_context.return_value = {}
            estimate_especial_reporte_subestimaciones = mock.Mock()
            estimate_especial_reporte_subestimaciones.return_value = "reporte_subestimaciones"
            estimate_especial_total_acumulado_subestimaciones = mock.Mock()
            estimate_especial_total_acumulado_subestimaciones.return_value = ["acumulado_subestimaciones"]
            estimate_especial_total_actual_subestimaciones = mock.Mock()
            estimate_especial_total_actual_subestimaciones.return_value = ["total_actual_subestimaciones"]
            estimate_especial_total_anterior_subestimaciones = mock.Mock()
            estimate_especial_total_anterior_subestimaciones.return_value = ["anterior_subestimaciones"]
            estimate_especial_total_contratado_subestimaciones = mock.Mock()
            estimate_especial_total_contratado_subestimaciones.return_value = ["total_contratado_subestimaciones"]
            mock_especial.reporte_subestimaciones = estimate_especial_reporte_subestimaciones
            mock_especial.total_acumulado_subestimaciones = estimate_especial_total_acumulado_subestimaciones
            mock_especial.total_actual_subestimaciones = estimate_especial_total_actual_subestimaciones
            mock_especial.total_anterior_subestimaciones = estimate_especial_total_anterior_subestimaciones
            mock_especial.total_contratado_subestimaciones = estimate_especial_total_contratado_subestimaciones
            view = self.get_instance(
                views.SubcontratosReport,
                pk=1,
                request=self.request
            )
            estimate_object = mock.Mock()
            estimate_object.path = 'blabla'
            view.object = estimate_object
            control_dict = {
                'subestimaciones': 'reporte_subestimaciones',
                'acumulado': 'acumulado_subestimaciones',
                'actual': 'total_actual_subestimaciones',
                'anterior': 'anterior_subestimaciones',
                'contratado': 'total_contratado_subestimaciones'
            }
            self.assertDictEqual(view.get_context_data(), control_dict)
            estimate_especial_reporte_subestimaciones.assert_called_with(
                view.object.start_date, view.object.finish_date, view.object.project.depth, 'somepath'
            )
            estimate_especial_total_acumulado_subestimaciones.assert_called_with(
                view.object.start_date, view.object.finish_date, view.object.project.depth, 'somepath'
            )
            estimate_especial_total_actual_subestimaciones.assert_called_with(
                view.object.start_date, view.object.finish_date, view.object.project.depth, 'somepath'
            )
            estimate_especial_total_anterior_subestimaciones.assert_called_with(
                view.object.start_date, view.object.finish_date, view.object.project.depth, 'somepath'
            )
            estimate_especial_total_contratado_subestimaciones.assert_called_with(
                view.object.start_date, view.object.finish_date, view.object.project.depth, 'somepath'
            )


class SubcContratoCreationTest(utils.CBVTestCase):

    @mock.patch.object(Contrato.objects, 'get')
    @mock.patch.object(views.SubcontratosReport, 'test_func', return_value=True)
    @mock.patch.object(views.ContratoCreationView, 'dispatch')
    def test_subcontratocreation_dispatch_hascontrato_instance(self, mock_dispatch, mock_test_func, mock_contrato_get):
        mock_dispatch.return_value = mock.Mock()
        mock_contrato = mock.Mock()
        mock_contrato_get.return_value = mock_contrato
        view = self.get_instance(
            views.SubcontratoCreationView,
            pk=1,
            request=self.request
        )
        view.dispatch(view.request)
        self.assertEqual(view.contrato, mock_contrato)
        mock_contrato_get.assert_called_with(pk=1)

    @mock.patch.object(views.ContratoCreationView, 'get_form')
    def test_subcontratocreattion_get_form_hascontrato(self, mock_get_form):
        mock_form = mock.Mock()
        mock_get_form.return_value = mock_form
        mock_contrato = mock.Mock()
        view = self.get_instance(
            views.SubcontratoCreationView,
            pk=1,
            request=self.request
        )
        view.contrato = mock_contrato
        form = view.get_form()
        self.assertEqual(form.contrato, mock_contrato)

    def test_subcontratocreation_max_id_executes_children_count(self):
        view = self.get_instance(
            views.SubcontratoCreationView,
            pk=1,
            request=self.request
        )
        mock_contrato = mock.Mock()
        contrato_get_children_count = mock.Mock()
        contrato_get_children_count.return_value = 3
        mock_contrato.get_children_count = contrato_get_children_count
        view.contrato = mock_contrato
        self.assertEqual(view.get_max_id(), 3)
        contrato_get_children_count.assert_called_once()

    def test_get_depth_subcontrato(self):
        view = self.get_instance(
            views.SubcontratoCreationView,
            pk=1,
            request=self.request
        )
        mock_contrato = mock.Mock()
        contrato_get_depth = mock.Mock()
        contrato_get_depth.return_value = 1
        mock_contrato.get_depth = contrato_get_depth
        view.contrato = mock_contrato
        self.assertEqual(view.get_depth(), 2)
        contrato_get_depth.assert_called_once()

    @mock.patch.object(views.ContratoCreationView, 'get_initial', return_value={})
    def test_subcontratocreation_get_initial(self, mock_initial):
        view = self.get_instance(
            views.SubcontratoCreationView,
            pk=1,
            request=self.request
        )
        mock_contrato = mock.Mock()
        mock_contrato_sitio = mock.Mock()
        mock_contrato.sitio = mock_contrato_sitio
        view.contrato = mock_contrato
        obj = view.get_initial()
        self.assertDictEqual(obj, {'sitio': mock_contrato.sitio})

    @mock.patch.object(views.ProyectosMenuMixin, 'get_context_data', return_value={})
    def test_get_context_data_subcontrato(self, mock_initial):
        view = self.get_instance(
            views.SubcontratoCreationView,
            pk=1,
            request=self.request
        )
        context = view.get_context_data()
        self.assertTrue(context.get('subcontrato'))


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

    def test_assert_cliente_request_raises_permissiondenied_with_no_currently_at(self):
        cliente = factories.ClienteFactory(company__customer=self.user.customer)
        view = self.get_instance(
            views.ClienteDetailView,
            pk=cliente.pk,
            request=self.request
        )
        with self.assertRaises(PermissionDenied):
            view.get_object()

    def test_assert_cliente_contratos_ordenados_only_assigned(self):
        cliente = factories.ClienteFactory(company__customer=self.user.customer)
        factories.ContratoFactory(contraparte=cliente)
        contrato2 = factories.ContratoFactory(contraparte=cliente)
        contrato2.users.add(self.user)
        contrato3 = factories.ContratoFactory(contraparte=cliente)
        contrato3.users.add(self.user)
        self.user.currently_at = cliente.company
        self.user.save()
        view = self.get_instance(
            views.ClienteDetailView,
            pk=cliente.pk,
            request=self.request
        )
        view.object = cliente
        qs = view.contratos_ordenados()
        qs_test = [repr(q) for q in sorted(
            [contrato2, contrato3], key=lambda x: x.fecha, reverse=True
        )]
        self.assertQuerysetEqual(qs, qs_test)


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

    def test_assert_sitio_request_returns_permissiondenied_without_its_company(self):
        sitio_company = factories.CompanyFactory(customer=self.user.customer)
        sitio_cliente = factories.ClienteFactory(company=sitio_company)
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        view = self.get_instance(
            views.SitioDetailView,
            pk=sitio.pk,
            request=self.request
        )
        with self.assertRaises(PermissionDenied):
            view.get_object()


class DestinatarioDetailTest(BaseViewTest):

    def test_assert_request_returns_correct_destinatario_object(self):
        destinatario_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = destinatario_company
        destinatario_cliente = factories.ClienteFactory(company=destinatario_company)
        destinatario = factories.DestinatarioFactory(contraparte=destinatario_cliente)
        view = self.get_instance(
            views.DestinatarioDetailView,
            pk=destinatario.pk,
            request=self.request
        )
        obj = view.get_object()
        self.assertEqual(obj, destinatario)

    def test_destinatario_assert_request_returns_permissiondenied_without_its_company(self):
        destinatario = factories.DestinatarioFactory(contraparte__company__customer=self.user.customer)
        view = self.get_instance(
            views.DestinatarioDetailView,
            pk=destinatario.pk,
            request=self.request
        )
        with self.assertRaises(PermissionDenied):
            view.get_object()


class ContratoCreationTest(BaseViewTest):

    def test_get_initial_returns_1_when_no_contratos(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = contrato_company
        self.request.user.company.add(contrato_company)
        self.request.user.groups.add(self.admin_group)
        dicc = {
            'currently_at': contrato_company.company_name, 'folio': 1, 'users': [self.request.user.id],
            'depth': 1, 'path': 'random', 'numchild': 0,
            }
        view = self.get_instance(
            views.ContratoCreationView,
            request=self.request,
        )
        dicc_test = view.get_initial()
        self.assertDictEqual(dicc_test, dicc)

    def test_get_initial_returns_the_next_id_when_contratos_exist(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato = factories.ContratoFactory(contraparte__company=contrato_company)
        self.request.user.currently_at = contrato_company
        self.request.user.company.add(contrato_company)
        self.request.user.groups.add(self.admin_group)
        dicc = {
            'currently_at': contrato_company.company_name,
            'folio': contrato.folio + 1,
            'users': [self.request.user.id],
            'depth': 1, 'path': 'random', 'numchild': 0,
        }
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
        view.nivel_permiso_usuario = self.request.user.nivel_acceso.nivel
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

    def test_contrato_creation_denied_user_auxiliar(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company
        self.user.save()
        self.user.company.add(company)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertEqual(response.status_code, 403)

    def test_contrato_creation_granted_user_coordinador(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        self.user.groups.add(self.proyectos_group)
        self.user.currently_at = company
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.user.company.add(company)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertEqual(response.status_code, 200)


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
                'contraparte': destinatario_cliente.id
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
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        contrato.users.add(self.request.user)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        destinatario = factories.DestinatarioFactory(contraparte=cliente_contrato)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(self.proyectos_group)
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
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
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

    def test_estimate_post_concept_same_text_not_raises(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        contrato.users.add(self.request.user)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        destinatario = factories.DestinatarioFactory(contraparte=cliente_contrato)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        concepto_2 = factories.ConceptoFactory(concept_text=concepto_1.concept_text)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(self.proyectos_group)
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
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
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

    def test_estimate_post_correctly_admin_user_not_assigned(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        destinatario = factories.DestinatarioFactory(contraparte=cliente_contrato)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(self.proyectos_group)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
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
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
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
        contrato = factories.ContratoFactory(contraparte__company=contrato_company)
        factories.ClienteFactory(company=contrato_company)
        destinatario = factories.DestinatarioFactory(contraparte=factories.ClienteFactory())
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(self.proyectos_group)
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
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertFormError(response, 'form', None, 'Destinatarios y contratos no pueden ser de empresas diferentes')

    def test_estimate_post_pagada_sin_fecha_pago(self):
        contrato = factories.ContratoFactory()
        destinatario = factories.DestinatarioFactory(contraparte=contrato.contraparte)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato.contraparte.company)
        self.user.currently_at = contrato.contraparte.company
        self.user.groups.add(self.proyectos_group)
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
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
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
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        destinatario = factories.DestinatarioFactory(contraparte=cliente_contrato)
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(self.proyectos_group)
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
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertFormsetError(response, 'generator_inline_concept', 0, 'cuantity_estimated', ['Introduzca un número.'])
        self.assertEqual(response.status_code, 200)

    def test_estimate_auth_by_gen_other_company_fail(self):
        contrato_company = factories.CompanyFactory(customer=self.user.customer)
        contrato_cliente = factories.ClienteFactory(company=contrato_company)
        contrato = factories.ContratoFactory(contraparte=contrato_cliente)
        cliente_contrato = factories.ClienteFactory(company=contrato_company)
        destinatario = factories.DestinatarioFactory(contraparte=contrato_cliente)
        destinatario2 = factories.DestinatarioFactory(contraparte=factories.ClienteFactory())
        concepto_1 = factories.ConceptoFactory(project=contrato)
        self.user.company.add(contrato_company)
        self.user.currently_at = contrato_company
        self.user.groups.add(self.proyectos_group)
        self.client.login(username=self.user.username, password='password')
        form_data = {
            'consecutive': '3',
            'supervised_by': str(self.user.id),
            'start_date': '2018-04-29',
            'finish_date': '2018-05-15',
            'draft_by': str(self.user.id),
            'project': str(contrato.id),
            'auth_by': str(destinatario.id),
            'auth_by_gen': str(destinatario2.id),
            'auth_date': '2018-05-15',
            'estimateconcept_set-TOTAL_FORMS': '1',
            'estimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-MAX_NUM_FORMS': '5',
            'estimateconcept_set-0-concept': concepto_1.concept_text,
            'estimateconcept_set-0-cuantity_estimated': '2',
            'estimateconcept_set-0-vertices_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-vertices_set-MAX_NUM_FORMS': '1000',
            'estimateconcept_set-0-imageestimateconcept_set-TOTAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-INITIAL_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MIN_NUM_FORMS': '0',
            'estimateconcept_set-0-imageestimateconcept_set-MAX_NUM_FORMS': '1000'
        }
        response = self.client.post(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato.pk}), form_data)
        self.assertFormError(response, 'form', None, 'Destinatarios y contratos no pueden ser de empresas diferentes')


class EstimateEditTest(BaseViewTest):

    def test_estimate_edit_saves_forms_when_valid(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        contrato = factories.ContratoFactory(contraparte__company=company)
        estimacion = factories.EstimateFactory(
            project=contrato,
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user
        )
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
            mock_save = mock.MagicMock()
            mock_save.return_value = estimacion
            mock_form.save = mock_save
            view.form_valid(mock_form)
        self.assertTrue(mock_form.save.called)
        self.assertTrue(mock_formset.is_valid.called)
        self.assertTrue(mock_formset.save.called)

    @mock.patch.object(views.EstimateEditView, 'form_invalid')
    def test_estimate_edit_executes_form_invalid_on_formset_invalid(self, mock_method):
        company = factories.CompanyFactory(customer=self.user.customer)
        cliente = factories.ClienteFactory(company=company)
        contrato = factories.ContratoFactory(contraparte=cliente)
        estimacion = factories.EstimateFactory(
            project=contrato,
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user
        )
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
        contrato = factories.ContratoFactory(contraparte=cliente)
        estimacion = factories.EstimateFactory(
            project=contrato,
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user
        )
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
        mock_formset_klass.assert_called_once()
        mock_formset.is_valid.assert_called_once()


class ContratoEditViewTest(BaseViewTest):

    def test_obtiene_objeto_correctamente(self):
        contrato = factories.ContratoFactory(contraparte__company__customer=self.user.customer)
        self.user.currently_at = contrato.contraparte.company
        contrato.users.add(self.request.user)
        view = self.get_instance(
            views.ContratoEditView,
            request=self.request,
            pk=contrato.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)

    def test_get_object_raises_permissiondenied_without_its_company(self):
        contrato = factories.ContratoFactory(contraparte__company__customer=self.user.customer)
        view = self.get_instance(
            views.ContratoEditView,
            request=self.request,
            pk=contrato.pk
        )
        with self.assertRaises(PermissionDenied):
            view.get_object()

    def test_get_initial_has_currently_at(self):
        contrato = factories.ContratoFactory(contraparte__company__customer=self.user.customer)
        self.user.currently_at = contrato.contraparte.company
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
        contrato_factory = factories.ContratoFactory(contraparte=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        contrato_factory.users.add(self.request.user)
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
            self.assertFormError(view, 'form', 'currently_at', 'Este campo es requerido.')


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

    def test_get_cliente_object_raises_permissiondenied_not_currently_at(self):
        cliente = factories.ClienteFactory()
        view = self.get_instance(
            views.ClienteEditView,
            request=self.request,
            pk=cliente.pk,
        )
        with self.assertRaises(PermissionDenied):
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

    def test_get_sitio_object_raises_permissiondenied_not_currently_at(self):
        sitio = factories.SitioFactory()
        view = self.get_instance(
            views.SitioEditView,
            request=self.request,
            pk=sitio.pk,
        )
        with self.assertRaises(PermissionDenied):
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
        self.user.currently_at = destinatario.contraparte.company
        view = self.get_instance(
            views.DestinatarioEditView,
            request=self.request,
            pk=destinatario.pk,
        )
        obj = view.get_object()
        self.assertEqual(obj, destinatario)

    def test_get_destinatario_object_raises_permissiondenied_not_currently_at(self):
        destinatario = factories.DestinatarioFactory()
        view = self.get_instance(
            views.DestinatarioEditView,
            request=self.request,
            pk=destinatario.pk,
        )
        with self.assertRaises(PermissionDenied):
            view.get_object()

    def test_destinatario_get_initial_has_company(self):
        destinatario = factories.DestinatarioFactory()
        self.user.currently_at = destinatario.contraparte.company
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
        contrato_inline = factories.ContratoFactory(contraparte=cliente_inline)
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
        contrato_inline = factories.ContratoFactory(contraparte=cliente_inline)
        view = self.get_instance(
            views.CatalogoConceptosInlineFormView,
            request=self.request,
            pk=contrato_inline.pk
        )
        test_url = '/proyectos/contrato/detalle/%i/' % contrato_inline.pk
        self.assertEqual(view.get_success_url(), test_url)


class CatalogoRetencionesInlineFormTest(utils.BaseTestCase):

    @mock.patch('construbot.proyectos.views.shortcuts.get_object_or_404')
    @mock.patch('construbot.proyectos.views.load_workbook')
    @mock.patch.object(views.Retenciones.objects, 'create')
    def test_importar_excel_guarda_retenciones(self, mock_create, mock_workbook, mock_404):
        mock_contrato = mock.Mock()
        mock_404.return_value = mock_contrato
        workbook_active = mock.Mock()
        workbook_active_iter_rows = mock.Mock()
        workbook_active_iter_rows.return_value = [['Nombre', 'PORCENTAJE', 50]]
        workbook_active.iter_rows = workbook_active_iter_rows
        ws = mock.Mock()
        ws.active = workbook_active
        mock_workbook.return_value = ws
        request = self.factory.post('bla/bla', data={'contrato': 2, 'excel-file': StringIO('test')})
        mock_user = mock.Mock()
        user_currently_at = mock.Mock()
        mock_user.currently_at = user_currently_at
        request.user = mock_user
        view = self.get_instance(
            views.CatalogoRetencionesInlineFormView,
            request=request
        )
        view.importar_excel()
        mock_create.assert_called_once_with(nombre='Nombre', valor=50, tipo='PERCENTAGE', project=mock_contrato)

    @mock.patch('construbot.proyectos.views.shortcuts.get_object_or_404')
    @mock.patch('construbot.proyectos.views.load_workbook')
    @mock.patch.object(views.Retenciones.objects, 'create')
    def test_importar_excel_guarda_retenciones_monto(self, mock_create, mock_workbook, mock_404):
        mock_contrato = mock.Mock()
        mock_404.return_value = mock_contrato
        workbook_active = mock.Mock()
        workbook_active_iter_rows = mock.Mock()
        workbook_active_iter_rows.return_value = [['Nombre', 'monto', 50]]
        workbook_active.iter_rows = workbook_active_iter_rows
        ws = mock.Mock()
        ws.active = workbook_active
        mock_workbook.return_value = ws
        request = self.factory.post('bla/bla', data={'contrato': 2, 'excel-file': StringIO('test')})
        mock_user = mock.Mock()
        user_currently_at = mock.Mock()
        mock_user.currently_at = user_currently_at
        request.user = mock_user
        view = self.get_instance(
            views.CatalogoRetencionesInlineFormView,
            request=request
        )
        view.importar_excel()
        mock_create.assert_called_once_with(nombre='Nombre', valor=50, tipo='AMOUNT', project=mock_contrato)


class CatalogoConceptosTest(BaseViewTest):

    @mock.patch.object(views.CatalogosView, 'importar_excel')
    @mock.patch.object(views.UpdateView, 'post')
    def test_importar_excel_excecuted_on_excelfile_in_request(self, mock_post, mock_importar):
        factory = self.factory.post('bla/bla', data={'excel-file': StringIO('test')})
        self.post(views.CatalogosView, request=factory)
        mock_importar.assert_called_with()
        mock_post.assert_called_with(factory)

    def test_json_formed_correctly(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = company
        unit = factories.UnitFactory(unit='meter')
        cliente = factories.ClienteFactory(company=company)
        contrato = factories.ContratoFactory(contraparte=cliente)
        for iterator in range(3):
            factories.ConceptoFactory(
                code=str(iterator),
                concept_text='text_%s' % iterator,
                unit=unit,
                total_cuantity=1000 + iterator,
                unit_price=2 + iterator,
                project=contrato,
            )
        instance = self.get_instance(
            views.CatalogoConceptos,
            request=self.request,
        )
        instance.contrato = contrato
        response = instance.get(self.request)
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

    def test_catalogo_edit_raises_permission_denied(self):
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        contrato_factory = factories.ContratoFactory(contraparte__company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        request = self.client.get(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(request.status_code, 403)

    @mock.patch.object(views.CatalogoConceptos, 'get_contrato')
    def test_get_assignment_args(self, mock_contrato):
        _contrato = factories.ContratoFactory()
        mock_contrato.return_value = _contrato
        _contrato.users.add(self.request.user)
        instance = self.get_instance(
            views.CatalogoConceptos,
            request=self.request,
        )

        instance_contrato, instance_qs = instance.get_assignment_args()
        mock_contrato.assert_called_once()
        test_qs = [repr(_contrato)]
        self.assertEqual(_contrato, instance_contrato)
        self.assertQuerysetEqual(instance_qs, test_qs)

    def test_get_contrato(self):
        company = factories.CompanyFactory(customer=self.user.customer)
        contrato = factories.ContratoFactory(contraparte__company=company)
        self.user.currently_at = company
        contrato.users.add(self.user)
        instance = self.get_instance(
            views.CatalogoConceptos,
            request=self.request,
            pk=contrato.pk
        )
        instance_contrato = instance.get_contrato()
        self.assertEqual(instance_contrato, contrato)


class DynamicDeleteTest(BaseViewTest):

    @mock.patch('django.shortcuts.get_object_or_404')
    def test_get_object_calls_get_obj_or_404(self, mock_404):
        contrato = factories.ContratoFactory()
        mock_404.return_value = contrato
        self.user.currently_at = contrato.contraparte.company
        view = self.get_instance(
            views.DynamicDelete,
            request=self.request,
            model='Contrato',
            pk=contrato.pk
        )
        obj = view.get_object()
        self.assertEqual(obj, contrato)
        mock_404.assert_called_once()

    def test_dynamic_delete_gets_object(self):
        company_delete = factories.CompanyFactory(customer=self.user.customer)
        cliente_delete = factories.ClienteFactory(company=company_delete, tipo='CLIENTE')
        contrato_object = factories.ContratoFactory(folio=1, contraparte=cliente_delete)
        contrato_object.users.add(self.request.user)
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
    def test_delete_method_calls_functions_for_Contrato(self, mock_object):
        with mock.patch.object(views.DynamicDelete, 'folio_handling', return_value=None) as mock_folio:
            contrato_delete = mock.Mock()
            contrato_delete.pk = 1
            contrato_delete.folio = 1
            request = RequestFactory().post(
                reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_delete.pk}),
                data={'value': 'confirm'}
            )
            view = self.get_instance(
                views.DynamicDelete,
                request=request,
            )
            response = view.delete(request)
        mock_object.assert_called_once()
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"exito": True})

    @mock.patch.object(views.DynamicDelete, 'get_object')
    def test_delete_method_calls_functions_for_Estimate(self, mock_object):
        with mock.patch.object(views.DynamicDelete, 'folio_handling', return_value=None) as mock_folio:
            estimate_delete = mock.Mock()
            estimate_delete.pk = 1
            estimate_delete.consecutive = 1
            request = RequestFactory().post(
                reverse('proyectos:eliminar', kwargs={'model': 'Estimate', 'pk': estimate_delete.pk}),
                data={'value': 'confirm'}
            )
            view = self.get_instance(
                views.DynamicDelete,
                request=request,
            )
            response = view.delete(request)
        mock_object.assert_called_once()
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"exito": True})

    @mock.patch.object(views.DynamicDelete, 'get_company_query')
    def test_folio_handling_perfoms_correct_qs(self, mock_query):
        company_delete = factories.CompanyFactory(customer=self.user.customer)
        cliente_delete = factories.ClienteFactory(company=company_delete)
        contrato_delete = factories.ContratoFactory(folio=1, contraparte=cliente_delete)
        contrato_delete_2 = factories.ContratoFactory(folio=2, contraparte=cliente_delete)
        contrato_delete_3 = factories.ContratoFactory(folio=3, contraparte=cliente_delete)
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
            {'contraparte__company': self.user.currently_at, 'folio__gt': view.object.folio}, 'folio'
        )
        view.folio_handling()
        contrato_delete_2.refresh_from_db()
        contrato_delete_3.refresh_from_db()
        mock_query.assert_called_once()
        self.assertEqual(contrato_delete_2.folio, 1)
        self.assertEqual(contrato_delete_3.folio, 2)

    @mock.patch.object(views.DynamicDelete, 'get_object')
    def test_get_company_query_with_estimate(self, mock_object):
        estimate = factories.EstimateFactory(
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user
        )
        mock_object.return_value = estimate
        request = RequestFactory().post(
            reverse('proyectos:eliminar', kwargs={'model': 'Estimate', 'pk': estimate.pk}),
            data={'value': 'confirm'}
        )
        self.user.currently_at = estimate.project.contraparte.company
        request.user = self.user
        view = self.get_instance(
            views.DynamicDelete,
            request=request,
            model='Estimate',
            pk=estimate.pk
        )
        view.object = view.get_object()
        control_dict = {
            'project__contraparte__company': self.request.user.currently_at,
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
        self.user.currently_at = contrato.contraparte.company
        request.user = self.user
        view = self.get_instance(
            views.DynamicDelete,
            request=request,
            model='Estimate',
            pk=contrato.pk
        )
        view.object = view.get_object()
        control_dict = {
            'contraparte__company': self.request.user.currently_at,
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

    def test_autocomplete_returns_the_correct_company_object(self):
        company1 = factories.CompanyFactory(company_name="CömPaNy", customer=self.user.customer)
        company2 = factories.CompanyFactory(company_name="CóMPaNy", customer=self.user.customer)
        self.user.company.add(company1)
        self.user.company.add(company2)
        self.user.currently_at = company1
        view = self.get_instance(
            views.CompanyAutocomplete,
            request=self.request,
        )
        view.q = "com"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [company1, company2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)

    def test_if_company_autocomplete_returns_none(self):
        company1 = factories.CompanyFactory(company_name="CömPaNy", customer=self.user.customer)
        company2 = factories.CompanyFactory(company_name="CóMPaNy", customer=self.user.customer)
        self.user.currently_at = company1
        view = self.get_instance(
            views.CompanyAutocomplete,
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
            'company': self.request.user.currently_at,
            'tipo': 'CLIENTE'
        }
        self.assertDictEqual(instance.get_key_words(), dict_control)

    def test_cliente_autocomplete_get_post_key_words_correct_dict(self):
        instance = views.ClienteAutocomplete()
        company = factories.CompanyFactory(customer=self.user.customer)
        self.request.user.currently_at = company
        instance.request = self.request
        instance.q = 'hola'
        dict_control = {
            'company': self.request.user.currently_at,
            'tipo': 'CLIENTE'
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
        instance.forwarded = {'contraparte': str(cliente.id)}
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
        view.forwarded = {'contraparte': str(cliente_autocomplete.id)}
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
        contrato = factories.ContratoFactory(contraparte__company=self.request.user.currently_at)
        instance.forwarded = {'project': contrato.id}
        dict_control = {
            'destinatario_text__unaccent__icontains': 'hola',
            'contraparte': contrato.contraparte
        }
        self.assertDictEqual(instance.get_key_words(), dict_control)

    def test_destinatario_get_post_keywords_correct_dict(self):
        instance = views.DestinatarioAutocomplete()
        instance.create_field = 'destinatario_text'
        self.request.user.currently_at = factories.CompanyFactory(customer=self.user.customer)
        instance.request = self.request
        contrato = factories.ContratoFactory(contraparte__company=self.request.user.currently_at)
        instance.forwarded = {'project': contrato.id}
        dict_control = {'contraparte': contrato.contraparte}
        self.assertDictEqual(instance.get_post_key_words(), dict_control)

    def test_integration_for_post_in_destinatario(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        contrato = factories.ContratoFactory(contraparte__company=company_autocomplete)
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
        unit = factories.UnitFactory(unit="Kilo", company=company_autocomplete)
        unit_2 = factories.UnitFactory(unit="Kilogramo", company=company_autocomplete)
        view = self.get_instance(
            views.UnitAutocomplete,
            request=self.request,
        )
        view.q = "kil"
        qs = view.get_queryset()
        qs_test = [repr(a) for a in [unit, unit_2]]
        self.assertQuerysetEqual(qs, qs_test, ordered=False)

    def test_unit_autocomplete_returns_the_correct_key_words_no_create_field(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        view = self.get_instance(
            views.UnitAutocomplete,
            request=self.request,
        )
        view.q = "some search"
        dicc = {'unit__unaccent__icontains': view.q, 'company': company_autocomplete}
        dicc_test = view.get_key_words()
        self.assertDictEqual(dicc, dicc_test)

    def test_unit_autocomplete_returns_the_correct_key_words_create_field(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        view = self.get_instance(
            views.UnitAutocomplete,
            request=self.request,
        )
        view.q = "some search"
        view.create_field = 'unit'
        dicc = {'unit__unaccent__icontains': view.q, 'company': company_autocomplete}
        dicc_test = view.get_key_words()
        self.assertDictEqual(dicc, dicc_test)

    def test_unit_autocomplete_creates_instance_correctly(self):
        company_autocomplete = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_autocomplete
        request = RequestFactory().post(
            reverse('proyectos:unit-autocomplete', kwargs={}),
            data={'text': 'Kg'}
        )
        request.user = self.user
        view = self.get_instance(
            views.UnitAutocomplete,
            request=request,
        )
        view.q = request.GET.get('q', '')
        view.create_field = 'unit'
        obj = view.create_object(request.POST.get('text'))
        self.assertEqual(obj.unit, 'Kg')
        self.assertTrue(isinstance(obj.pk, int))


class UserAutocompleteTest(BaseViewTest):

    def test_user_username_autocomplete_get_queryset(self):
        instance = views.UserAutocomplete()
        instance.q = 'user-'
        company_test = factories.CompanyFactory(customer=self.request.user.customer)
        self.request.user.company.add(company_test)
        self.request.user.currently_at = company_test
        instance.request = self.request
        qs = instance.get_queryset()
        qs_test = [repr(a) for a in sorted([self.user])]
        self.assertQuerysetEqual(qs, qs_test)

    def test_user_email_autocomplete_get_queryset(self):
        instance = views.UserAutocomplete()
        instance.q = '@example'
        company_test = factories.CompanyFactory(customer=self.request.user.customer)
        self.request.user.company.add(company_test)
        self.request.user.currently_at = company_test
        instance.request = self.request
        qs = instance.get_queryset()
        qs_test = [repr(a) for a in sorted([self.request.user])]
        self.assertQuerysetEqual(qs, qs_test)
