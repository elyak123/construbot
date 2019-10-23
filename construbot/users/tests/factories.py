import string
import factory
import factory.fuzzy
from django.contrib.auth import get_user_model
from construbot.users.models import Customer, Company, NivelAcceso
from django.contrib.auth.models import Group

User = get_user_model()


class CustomerFactory(factory.django.DjangoModelFactory):
    customer_name = factory.Sequence(lambda n: 'customer-{0}'.format(n))

    class Meta:
        model = Customer


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'group-{0}'.format(n))

    class Meta:
        model = Group


class CompanyFactory(factory.django.DjangoModelFactory):
    company_name = factory.Sequence(lambda n: 'company-{0}'.format(n))
    customer = factory.SubFactory(CustomerFactory)

    class Meta:
        model = Company


class NivelAccesoFactory(factory.django.DjangoModelFactory):
    nivel = factory.fuzzy.FuzzyInteger(0, 5)
    nombre = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_letters, prefix='nivel_')

    class Meta:
        model = NivelAcceso


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    customer = factory.SubFactory(CustomerFactory)
    nivel_acceso = factory.SubFactory(NivelAccesoFactory)

    @factory.post_generation
    def company(self, create, extracted, **kwargs):  # pragma: no cover
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for co in extracted:
                self.company.add(co)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):  # pragma: no cover
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)

    class Meta:
        model = User
        django_get_or_create = ('username', 'nivel_acceso')
