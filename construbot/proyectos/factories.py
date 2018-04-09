import string
import datetime
import factory
import factory.fuzzy
from construbot.users.tests.factories import CompanyFactory
from .models import Cliente, Sitio, Contrato


class ClienteFactory(factory.django.DjangoModelFactory):
    cliente_name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='cliente_')
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = Cliente


class SitioFactory(factory.django.DjangoModelFactory):
    sitio_name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='sitio_')
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = Sitio


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
    cliente = factory.SubFactory(ClienteFactory)
    sitio = factory.SubFactory(SitioFactory)

    class Meta:
        model = Contrato
