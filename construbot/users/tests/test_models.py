from . import factories
from django.test import tag
from django.contrib.auth import get_user_model
from construbot.users.models import Customer, NivelAcceso
from . import utils

User = get_user_model()


class TestUser(utils.BaseTestCase):

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            self.user.email  # This is the default email for self.make_user()
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(),
            '/users/detalle/{}/'.format(self.user.username)
        )

    def test_no_soy_administrador(self):
        soy_admin = self.user.is_administrator()
        self.assertEqual(soy_admin, False)

    def test_si_soy_admin(self):
        self.user.groups.add(self.admin_group)
        self.user.save()
        soy_admin = self.user.is_administrator()
        self.assertEqual(soy_admin, True)

    def test_creacion_superusuario_no_es_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='super_user',
                email='bla@bla.com',
                password='top_secret',
                is_staff=False,
                is_superuser=True
            )

    def test_creacion_superusuario_no_es_super(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='super_user',
                email='bla@bla.com',
                password='top_secret',
                is_staff=True,
                is_superuser=False
            )

    def test_correcta_creacion_superusuario(self):
        superuser = User.objects.create_superuser(
            username='super_user',
            email='bla@bla.com',
            password='top_secret',
            is_staff=True,
            is_superuser=True
        )
        self.assertEqual(superuser.username, 'super_user')

    def test_superusuario_contiene_company(self):
        superuser = User.objects.create_superuser(
            username='super_user',
            email='bla@bla.com',
            password='top_secret',
            is_staff=True,
            is_superuser=True
        )
        self.assertIsInstance(superuser.customer, Customer)

    def test_superusuario_tiene_nivel_6(self):
        superuser = User.objects.create_superuser(
            username='super_user',
            email='bla@bla.com',
            password='top_secret',
            is_staff=True,
            is_superuser=True
        )
        self.assertIsInstance(superuser.nivel_acceso, 6)

    def test_super_usuario_tiene_nivel_acceso(self):
        superuser = User.objects.create_superuser(
            username='super_user',
            email='bla@bla.com',
            password='top_secret',
            is_staff=True,
            is_superuser=True
        )
        self.assertIsInstance(superuser.nivel_acceso, NivelAcceso)


class TestCustomer(utils.BaseTestCase):
    def test_customer_repr_dont_raises_error(self):
        customer = Customer.objects.create()
        customer_2 = factories.CustomerFactory()
        self.assertEqual(repr(customer), '<Customer: %s>' % customer.id)
        self.assertEqual(repr(customer_2), '<Customer: %s>' % customer_2.customer_name)


class TestFactories(utils.BaseTestCase):

    def test_UserFactory_saved_to_db(self):
        user = factories.UserFactory(nivel_acceso=self.auxiliar_permission)
        user.full_clean()
        user.save()
        # Just checking it was saved to db
        self.assertIn('user', user.username)

    def test_Company_Factory_saved(self):
        company = factories.CompanyFactory()
        company.full_clean()
        company.save()
        self.assertIn('company', company.company_name)
