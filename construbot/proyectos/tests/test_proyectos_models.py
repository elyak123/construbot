from unittest import skip, mock
from django.test import RequestFactory, tag
from construbot.users.tests import utils
from construbot.users.tests import factories as user_factories
from construbot.proyectos import models
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
        control = [repr(x) for x in sorted([sitio_contrato_1, sitio_contrato_2], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(
            contratos_ordenados,
            control,
            msg='\n\nsitio.get_contratos_ordenados:\n{}.fecha = {}\n{}.fecha = {}'.format(
                contratos_ordenados[0].contrato_name,
                contratos_ordenados[0].fecha,
                contratos_ordenados[1].contrato_name,
                contratos_ordenados[1].fecha,
            )
        )


class ContratoModelTest(BaseModelTesCase):

    def test_contrato_absolute_url(self):
        contrato = factories.ContratoFactory()
        self.assertEqual(contrato.get_absolute_url(), '/proyectos/contrato/detalle/{}/'.format(contrato.pk))


class EstimateModelTest(BaseModelTesCase):

    def test_estimacion_absolute_url(self):
        estimacion = factories.EstimateFactory()
        self.assertEqual(
            estimacion.get_absolute_url(), '/proyectos/contrato/detalle/{}/'.format(estimacion.project.pk)
        )

    def test_total_estimate_method(self):
        contrato = factories.ContratoFactory()
        estimacion = factories.EstimateFactory(project=contrato)
        conceptos = [
            factories.EstimateConceptFactory(
                estimate=estimacion,
                concept__project=contrato,
                concept__unit_price=x,
                cuantity_estimated=x
            ) for x in range(10)
        ]
        aggregation = estimacion.total_estimate()
        self.assertEqual(aggregation['total'], 285)

    @mock.patch.object(models.ConceptSet, 'add_estimateconcept_properties')
    def test_anotaciones_conceotos(self, mock_properties):
        estimacion = factories.EstimateFactory()
        estimacion.anotaciones_conceptos()
        mock_properties.assert_called_once()


class ConceptoSetTest(BaseModelTesCase):
    @skip
    def test_anotacion_estimado_ala_fecha(self):
        contrato = factories.ContratoFactory()
        for concept_iterator in range(10):
            concepto = factories.ConceptoFactory(project=contrato, unit_price=concept_iterator)
            for ecset_iterator in range(10):
                concepto_estimacion = factories.EstimateConceptFactory(
                    concept=concepto, cuantity_estimated=ecset_iterator
                )

        totales = [0, 54, 108, 162, 216, 270, 324, 378, 432, 486]
        conceptos = models.Concept.especial.filter(project=contrato).estimado_a_la_fecha()
        for it, obj in enumerate(conceptos):
            self.assertEqual(obj.acumulado, totales[it])

    # se acuerda realizar la prueba en los metodos de ConceptSet
    # debido a que son una sola instrucción a la base de datos
    # una vez teniendo la prueba como base, se puede cambiar
    # ECSet.apuntar_total_estimado para quitarle el filtro y crear
    # un test solo para dicho método.
    # todo lo demás se queda igual.
    # def test_apuntar_total_estimado(self):
    #     contrato = factories.ContratoFactory()
    #     estimacion = factories.EstimateFactory(project=contrato)
    #     conceptos = [
    #         factories.EstimateConceptFactory(
    #             estimate=estimacion,
    #             concept__project=contrato,
    #             concept__unit_price=x,
    #             cuantity_estimated=x
    #         ) for x in range(10)
    #     ]

