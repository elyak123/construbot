from unittest import skip
from django.test import RequestFactory, tag
from construbot.users.tests import utils
from construbot.users.tests import factories as user_factories
# from construbot.proyectos import models
from . import factories


class BaseModelTesCase(utils.BaseTestCase):

    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()
        self.request = self.get_request(self.user)


class ClienteModelTest(BaseModelTesCase):

    def test_correct_absolute_url(self):
        cliente = factories.ClienteFactory()
        self.assertEqual(
            cliente.get_absolute_url(),
            '/proyectos/cliente/detalle/{}/'.format(cliente.pk)
        )

    def test_contratos_ordenados_query_correct(self):
        cliente = factories.ClienteFactory()
        contrato_1 = factories.ContratoFactory(cliente=cliente)
        contrato_2 = factories.ContratoFactory(cliente=cliente)
        factories.ContratoFactory()
        contratos_ordenados = cliente.get_contratos_ordenados()
        qs_control = [repr(x) for x in sorted([contrato_1, contrato_2], key=lambda x: repr(x.fecha), reverse=True)]
        self.assertQuerysetEqual(contratos_ordenados, qs_control)


class SitioModelTest(BaseModelTesCase):

    def test_sitio_absolute_url_is_correct(self):
        sitio = factories.SitioFactory()
        self.assertEqual(sitio.get_absolute_url(), '/proyectos/sitio/detalle/{}/'.format(sitio.pk))

    def test_query_contratos_ordenados(self):
        sitio_company = user_factories.CompanyFactory()
        sitio = factories.SitioFactory(company=sitio_company)
        sitio_contrato_1 = factories.ContratoFactory(sitio=sitio)
        sitio_contrato_2 = factories.ContratoFactory(sitio=sitio)
        factories.ContratoFactory()
        contratos_ordenados = sitio.get_contratos_ordenados()
        control = [repr(x) for x in sorted(
            [sitio_contrato_1, sitio_contrato_2], key=lambda x: repr(x.fecha), reverse=True)
        ]
        self.assertQuerysetEqual(contratos_ordenados, control)


class ContratoModelTest(BaseModelTesCase):

    def test_contrato_absolute_url(self):
        contrato = factories.ContratoFactory()
        self.assertEqual(contrato.get_absolute_url(), '/proyectos/contrato/detalle/{}/'.format(contrato.pk))


class EstimateModelTest(BaseModelTesCase):
    @skip
    def test_estimacion_absolute_url(self):
        estimacion = factories.EstimateFactory()
        self.assertEqual(estimacion.get_absolute_url(), '/proyectos/estimacion/detalle/{}/'.format(estimacion.pk))
