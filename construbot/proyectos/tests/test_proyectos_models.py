import tempfile
import shutil
from unittest import mock
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import override_settings, tag
from test_plus.test import CBVTestCase
from construbot.users.models import NivelAcceso
from construbot.users.tests import factories as user_factories
from construbot.proyectos import models
from . import factories

MOCK_MEDIA_ROOT = tempfile.mkdtemp()


class ClienteModelTest(CBVTestCase):

    def test_correct_absolute_url(self):
        cliente = factories.ClienteFactory()
        self.assertEqual(
            cliente.get_absolute_url(),
            '/proyectos/cliente/detalle/{}/'.format(cliente.pk)
        )

    def test_contratos_ordenados_query_correct(self):
        cliente = factories.ClienteFactory()
        contrato_1 = factories.ContratoFactory(contraparte=cliente)
        contrato_2 = factories.ContratoFactory(contraparte=cliente)
        factories.ContratoFactory()
        contratos_ordenados = cliente.get_contratos_ordenados()
        qs_control = [repr(x) for x in sorted([contrato_1, contrato_2], key=lambda x: x.fecha, reverse=True)]
        self.assertQuerysetEqual(contratos_ordenados, qs_control)


class SitioModelTest(CBVTestCase):

    def test_sitio_absolute_url_is_correct(self):
        sitio = factories.SitioFactory()
        self.assertEqual(sitio.get_absolute_url(), '/proyectos/sitio/detalle/{}/'.format(sitio.pk))

    def test_query_contratos_ordenados(self):
        sitio_cliente = factories.ClienteFactory()
        sitio = factories.SitioFactory(cliente=sitio_cliente)
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


class ContratoModelTest(CBVTestCase):

    def test_contrato_absolute_url(self):
        contrato = factories.ContratoFactory()
        self.assertEqual(contrato.get_absolute_url(), '/proyectos/contrato/detalle/{}/'.format(contrato.pk))


class EstimateModelTest(CBVTestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.auxiliar_permission, aux_created = NivelAcceso.objects.get_or_create(nivel=1, nombre='Auxiliar')
        self.user = self.user_factory(nivel_acceso=self.auxiliar_permission)

    def test_estimacion_absolute_url(self):
        estimacion = factories.EstimateFactory(
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user,
        )
        self.assertEqual(
            estimacion.get_absolute_url(), '/proyectos/contrato/detalle/{}/'.format(estimacion.project.pk)
        )

    def test_total_estimate_method(self):
        contrato = factories.ContratoFactory()
        estimacion = factories.EstimateFactory(
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user,
            project=contrato
        )
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
    def test_anotaciones_conceptos(self, mock_properties):
        estimacion = factories.EstimateFactory(
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user,
        )
        estimacion.anotaciones_conceptos()
        try:
            mock_properties.assert_called_once()
        except AttributeError:
            self.assertEqual(mock_properties.call_count, 1)

    def test_amortizacion_anticipo_calcula_diff_positiva(self):
        estimacion = factories.EstimateFactory(
            supervised_by=self.user, draft_by=self.user, project__anticipo=Decimal('30.00')
        )
        estimacion_conceptos = mock.Mock()
        estimacion_conceptos_importe_total_contratado = mock.Mock()
        estimacion_conceptos_importe_total_contratado.return_value = {'total': Decimal('6748332.90')}
        estimacion_conceptos_importe_total_acumulado = mock.Mock()
        estimacion_conceptos_importe_total_acumulado.return_value = {'total': Decimal('6769073.97')}
        estimacion.conceptos = estimacion_conceptos
        estimacion.conceptos.importe_total_acumulado = estimacion_conceptos_importe_total_acumulado
        estimacion.conceptos.importe_total_contratado = estimacion_conceptos_importe_total_contratado
        estimacion.total = {'total': Decimal('2983666.88')}
        amortizacion = estimacion.amortizacion_anticipo()
        self.assertEqual(round(amortizacion, 2), Decimal('888877.74'))


class ConceptoSetTest(CBVTestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.auxiliar_permission, aux_created = NivelAcceso.objects.get_or_create(nivel=1, nombre='Auxiliar')
        self.user = self.user_factory(nivel_acceso=self.auxiliar_permission)

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
        contrato = factories.ContratoFactory(contraparte__tipo='CLIENTE')
        estimacion_1 = factories.EstimateFactory(
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user,
            project=contrato, consecutive=1
        )
        estimacion_2 = factories.EstimateFactory(
            draft_by=self.user,  # se ocupa porque si no truena
            supervised_by=self.user,
            project=contrato, consecutive=2
        )
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

    def test_anotacion_estimacion(self):
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

    @mock.patch.object(ImageFile, '_get_image_dimensions')
    def test_concept_image_count(self, mock_dimensions):
        mock_dimensions.return_value = (500, 380)
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        ecset = models.EstimateConcept.especial.filter(estimate=estimate1).order_by('pk')
        for concepto in ecset:
            factories.ImageEstimateConceptFactory(estimateconcept=concepto)
            factories.ImageEstimateConceptFactory(estimateconcept=concepto)
        conceptos = models.Concept.especial.filter(estimate_concept=estimate1).concept_image_count()
        for concept in conceptos:
            self.assertEqual(concept.image_count, 2)

    @mock.patch.object(models.ConceptSet, 'annotate')
    def test_vertice_count_correct_call(self, mock_annotate):
        models.Concept.especial.concept_vertice_count()
        mock_annotate.assert_called_once_with(vertice_count=models.models.Count('estimateconcept__vertices', distinct=True))

    @mock.patch.object(ImageFile, '_get_image_dimensions')
    def test_total_imagenes_estimacion(self, mock_dimensions):
        mock_dimensions.return_value = (500, 380)
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        ecset = models.EstimateConcept.especial.filter(estimate=estimate1).order_by('pk')
        for concepto in ecset:
            factories.ImageEstimateConceptFactory(estimateconcept=concepto)
            factories.ImageEstimateConceptFactory(estimateconcept=concepto)
        conceptos = models.Concept.especial.filter(estimate_concept=estimate1).concept_image_count()
        self.assertEqual(conceptos.total_imagenes_estimacion()['total_images'], 6)

    def test_importe_total_esta_estimacion(self):
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        conceptos = models.Concept.especial.filter(estimate_concept=estimate2).order_by('pk')
        self.assertEqual(
            conceptos.esta_estimacion(estimate2.consecutive).importe_total_esta_estimacion()['total'],
            4698
        )

    def test_importe_total_anterior(self):
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        conceptos = models.Concept.especial.filter(estimate_concept=estimate2).order_by('pk')
        self.assertEqual(conceptos.estimado_anterior(estimate2.consecutive).importe_total_anterior()['total'], 4130)

    def test_importe_total_acumulado(self):
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        conceptos = models.Concept.especial.filter(estimate_concept=estimate2).order_by('pk')
        self.assertEqual(conceptos.estimado_a_la_fecha(estimate2.consecutive).importe_total_acumulado()['total'], 8828)

    @mock.patch.object(ImageFile, '_get_image_dimensions')
    def test_anotar_imagenes(self, mock_dimensions):
        mock_dimensions.return_value = (500, 380)
        estimate1, estimate2 = self.generacion_estimaciones_con_conceptos()
        ecset = models.EstimateConcept.especial.filter(estimate=estimate1).order_by('pk')
        for estimate_cpt in ecset:
            factories.ImageEstimateConceptFactory(estimateconcept=estimate_cpt)
            factories.ImageEstimateConceptFactory(estimateconcept=estimate_cpt)
        conceptos = models.Concept.especial.filter(
                        estimate_concept=estimate1
                    ).add_estimateconcept_ids(estimate1.consecutive)
        concepto = conceptos.first()
        imagenes = concepto.anotar_imagenes()
        imagenes_control = models.ImageEstimateConcept.objects.filter(estimateconcept__concept=concepto)
        represetnation_img_control = [repr(x) for x in imagenes_control]
        self.assertQuerysetEqual(
            imagenes,
            represetnation_img_control,
            msg='\n{} {}\n{} {}'.format(
                imagenes[0].id,
                imagenes_control[0].id,
                imagenes[1].id,
                imagenes_control[1].id
            ),
            ordered=False
        )


class ConceptTest(CBVTestCase):

    def test_unit_different_company_from_concept_raises(self):
        with self.assertRaises(ValidationError):
            concept_company = user_factories.CompanyFactory()
            unit = factories.UnitFactory()
            concept = factories.ConceptoFactory(unit=unit, project__contraparte__company=concept_company)
            concept.full_clean()

    def test_importe_contratado(self):
        concepto = factories.ConceptoFactory(total_cuantity=50, unit_price=12)
        self.assertEqual(concepto.importe_contratado(), 600)

    def test_concept_unique_together(self):
        contrato = factories.ContratoFactory()
        factories.ConceptoFactory(concept_text='hola', project=contrato)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                factories.ConceptoFactory(concept_text='hola', project=contrato)

    def test_unit_price_operations(self):
        concept = factories.ConceptoFactory(unit_price=2)
        concept.anterior = 3450
        self.assertEqual(concept.unit_price_operations('anterior'), 1725)

    def test_unit_price_operations_raises_error(self):
        concept = factories.ConceptoFactory()
        with self.assertRaises(AttributeError):
            concept.unit_price_operations('anterior')

    def test_unit_price_operations_returns_zero(self):
        concept = factories.ConceptoFactory()
        concept.anterior = None
        self.assertEqual(concept.unit_price_operations('anterior'), 0)

    @mock.patch.object(models.Concept, 'unit_price_operations')
    def test_cantidad_estimado_anterior(self, mock_operations):
        concept = factories.ConceptoFactory()
        concept.cantidad_estimado_anterior()
        mock_operations.assert_called_once_with('anterior')

    @mock.patch.object(models.Concept, 'unit_price_operations')
    def test_cantidad_estimado_ala_fecha(self, mock_operations):
        concept = factories.ConceptoFactory()
        concept.cantidad_estimado_ala_fecha()
        mock_operations.assert_called_once_with('acumulado')

    @mock.patch.object(models.Concept, 'unit_price_operations')
    def test_cantidad_esta_estimacion(self, mock_operations):
        concept = factories.ConceptoFactory()
        concept.cantidad_esta_estimacion()
        mock_operations.assert_called_once_with('estaestimacion')

    def test_anotar_imagenes_raises_error(self):
        # anotar imagenes se encuentra en la clase anterior debido a los subqueries
        # necesarios para ejecutar los metodos.
        concept = factories.ConceptoFactory()
        with self.assertRaises(AttributeError):
            concept.anotar_imagenes()

    def test_company_unit_and_company_concept_same_thing(self):
        with self.assertRaises(ValidationError):
            company = user_factories.CompanyFactory()
            unit = factories.UnitFactory()
            concept = factories.ConceptoFactory(unit=unit, project__contraparte__company=company)
            concept.full_clean()


@override_settings(MEDIA_ROOT=MOCK_MEDIA_ROOT)
class ImageEstimateConceptTest(CBVTestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.auxiliar_permission, aux_created = NivelAcceso.objects.get_or_create(nivel=1, nombre='Auxiliar')
        self.user = self.user_factory(nivel_acceso=self.auxiliar_permission)

    def tearDown(self):
        shutil.rmtree(MOCK_MEDIA_ROOT, ignore_errors=True)

    def get_test_image_file(self):
        file = tempfile.NamedTemporaryFile(suffix='.png')
        image = ImageFile(file, name='file.png')
        return image

    @mock.patch.object(ImageFile, '_get_image_dimensions')
    def test_guardado_de_imagen(self, mock_dimensions):
        mock_dimensions.return_value = (500, 380)
        concepto = factories.EstimateConceptFactory(
            estimate__draft_by=self.user,  # se ocupa porque si no truena
            estimate__supervised_by=self.user
        )
        image = self.get_test_image_file()
        imagen = models.ImageEstimateConcept.objects.create(image=image, estimateconcept=concepto)
        self.assertTrue(models.ImageEstimateConcept.objects.filter(estimateconcept=concepto).exists())
        self.assertTrue(isinstance(imagen.id, int))
