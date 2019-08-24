import tempfile
import string
import datetime
from unittest import mock
import factory
import factory.fuzzy
from django.core.files.images import ImageFile
from construbot.users.tests.factories import CompanyFactory, UserFactory
from construbot.proyectos import models

# CONTRPARTE_TIPOS = [x[0] for x in models.Contraparte.TIPOS]


class ClienteFactory(factory.django.DjangoModelFactory):
    cliente_name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='cliente_')
    company = factory.SubFactory(CompanyFactory)
    # tipo = factory.fuzzy.FuzzyChoice(CONTRPARTE_TIPOS)

    class Meta:
        model = models.Contraparte


class SitioFactory(factory.django.DjangoModelFactory):
    sitio_name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='sitio_')
    cliente = factory.SubFactory(ClienteFactory)

    class Meta:
        model = models.Sitio


class DestinatarioFactory(factory.django.DjangoModelFactory):
    destinatario_text = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='destinatario_')
    puesto = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters)
    contraparte = factory.SubFactory(ClienteFactory)

    class Meta:
        model = models.Destinatario


class ContratoFactory(factory.django.DjangoModelFactory):
    folio = factory.Sequence(lambda n: n)
    code = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters + string.digits)
    fecha = factory.fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    contrato_name = factory.fuzzy.FuzzyText(
        length=8,
        chars=string.ascii_letters + string.digits,
        prefix='nombre_'
    )
    contrato_shortName = factory.fuzzy.FuzzyText(
        length=8,
        chars=string.ascii_letters + string.digits,
        prefix='short_'
    )
    status = True
    monto = factory.fuzzy.FuzzyDecimal(100000.76, 10000000.56, precision=2)
    contraparte = factory.SubFactory(ClienteFactory)
    sitio = factory.SubFactory(SitioFactory)
    path = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_letters + string.digits)
    depth = 1

    class Meta:
        model = models.Contrato


class EstimateFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ContratoFactory)
    consecutive = factory.fuzzy.FuzzyInteger(0, 25)
    draft_by = factory.SubFactory(UserFactory)
    supervised_by = factory.SubFactory(UserFactory)
    start_date = factory.fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    finish_date = factory.fuzzy.FuzzyDate(datetime.date(2008, 1, 1))

    class Meta:
        model = models.Estimate


class UnitFactory(factory.django.DjangoModelFactory):
    unit = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='unit_')
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = models.Units


class ConceptoFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: n)
    concept_text = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='text_')
    project = factory.SubFactory(ContratoFactory)
    unit = factory.SubFactory(UnitFactory)
    total_cuantity = factory.fuzzy.FuzzyDecimal(1, 35, precision=2)
    unit_price = factory.fuzzy.FuzzyDecimal(100000.76, 10000000.56, precision=2)

    class Meta:
        model = models.Concept


class EstimateConceptFactory(factory.django.DjangoModelFactory):
    estimate = factory.SubFactory(EstimateFactory)
    concept = factory.SubFactory(ConceptoFactory)
    cuantity_estimated = factory.fuzzy.FuzzyDecimal(1, 25, precision=2)
    observations = factory.fuzzy.FuzzyText(length=140, chars=string.ascii_letters, prefix='observacion_')

    class Meta:
        model = models.EstimateConcept


class FuzzyImage(factory.fuzzy.BaseFuzzyAttribute):

    def __init__(self, *args, **kwargs):
        super(FuzzyImage, self).__init__(*args, **kwargs)

    def fuzz(self):
        file = tempfile.NamedTemporaryFile(suffix='.png')
        image = ImageFile(file, name='file.png')
        return image


class ImageEstimateConceptFactory(factory.django.DjangoModelFactory):
    image = FuzzyImage()
    estimateconcept = factory.SubFactory(EstimateConceptFactory)

    class Meta:
        model = models.ImageEstimateConcept
