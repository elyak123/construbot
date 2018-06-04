import shutil
import tempfile
from unittest import skip, mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, override_settings, tag
from construbot.users.tests import utils
#from construbot.core.utils import fuzz
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
        try:
            mock_properties.assert_called_once()
        except AttributeError:
            self.assertEqual(mock_properties.call_count, 1)

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ConceptoSetTest(BaseModelTesCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def generacion_estimaciones_con_conceptos(self):
        conceptos_list = [
            {'code': 'CCA', 'total_cuantity': 1200, 'unit_price': 3},
            {'code': 'TOPO', 'total_cuantity': 800, 'unit_price': 8},
            {'code': 'OTRO', 'total_cuantity': 8000, 'unit_price': 0.2},
        ]
        estimate_concept_list = [
            {'estimate_cons': 1, 'code': 'CCA', 'cuantity_estimated': 300},
            {'estimate_cons': 1, 'code': 'TOPO', 'cuantity_estimated': 370},
            {'estimate_cons': 1, 'code': 'OTRO', 'cuantity_estimated': 1350},
            {'estimate_cons': 2, 'code': 'CCA', 'cuantity_estimated': 800},
            {'estimate_cons': 2, 'code': 'TOPO', 'cuantity_estimated': 200},
            {'estimate_cons': 2, 'code': 'OTRO', 'cuantity_estimated': 3490},
        ]
        contrato = factories.ContratoFactory()
        estimacion_1 = factories.EstimateFactory(project=contrato, consecutive=1)
        estimacion_2 = factories.EstimateFactory(project=contrato, consecutive=2)
        for element in conceptos_list:
            factories.ConceptoFactory(
                code=element['code'],
                project=contrato,
                total_cuantity=element['total_cuantity'],
                unit_price=element['unit_price']
            )
        for element_dict in estimate_concept_list:
            if element_dict['estimate_cons'] == 1:
                estimacion_element = estimacion_1
            else:
                estimacion_element = estimacion_2
            concept_element = models.Concept.objects.get(project=contrato, code=element_dict['code'])
            factories.EstimateConceptFactory(
                estimate=estimacion_element,
                concept=concept_element,
                cuantity_estimated=element_dict['cuantity_estimated']
            )
        return estimacion_1, estimacion_2

    # @mock.patch('django.db.models.expressions.ResolvedOuterRef.as_sql')
    def test_anotacion_estimado_ala_fecha(self):#, mock_as_sql):
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        main_query = estimate2.anotaciones_conceptos()
        self.assertEqual(main_query[0].acumulado, 3300)
        self.assertEqual(main_query[0].anterior, 900)
        self.assertEqual(main_query[0].estaestimacion, 2400)
        self.assertEqual(main_query[1].acumulado, 4560)
        self.assertEqual(main_query[1].anterior, 2960)
        self.assertEqual(main_query[1].estaestimacion, 1600)
        self.assertEqual(main_query[2].acumulado, 968)
        self.assertEqual(main_query[2].anterior, 270)
        self.assertEqual(main_query[2].estaestimacion, 698)

    def test_concept_image_count(self):
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        ecset = models.EstimateConcept.especial.filter(estimate=estimate1).order_by('pk')
        for concepto in ecset:
            factories.ImageEstimateConceptFactory(estimateconcept=concepto)
            factories.ImageEstimateConceptFactory(estimateconcept=concepto)
        conceptos = models.Concept.especial.filter(estimate_concept=estimate1).concept_image_count()
        for concept in conceptos:
            self.assertEqual(concept.image_count, 2)
