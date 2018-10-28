import factory
from django.contrib.auth import get_user_model
from construbot.users.models import Customer, Company
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


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    customer = factory.SubFactory(CustomerFactory)

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
        django_get_or_create = ('username', )
