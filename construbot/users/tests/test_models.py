from . import factories
from django.contrib.auth.models import Group
from test_plus.test import TestCase
from construbot.users.models import User, Company


class TestUser(TestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            'testuser'  # This is the default username for self.make_user()
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(),
            '/users/testuser/'
        )

    def test_no_soy_administrador(self):
        soy_admin = self.user.is_administrator()
        self.assertEqual(soy_admin, False)

    def test_si_soy_admin(self):
        admin_group = Group.objects.create(name='Administrators')
        self.user.groups.add(admin_group)
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


class TestFactories(TestCase):

    def test_UserFactory_saved_to_db(self):
        user = factories.UserFactory()
        user.full_clean()
        user.save()
        # Just checking it was saved to db
        self.assertIn('user', user.username)

    # def test_user_and_its_company_same_customer(self):
    #     user = factories.UserFactory()
    #     user.full_clean()
    #     user.save()
    #     company = Company.objects.create(company_name='My_company', customer=user.customer)
    #     self.assertEqual(user.customer, company.customer)

    def test_Company_Factory_saved(self):
        company = factories.CompanyFactory()
        company.full_clean()
        company.save()
        self.assertIn('company', company.company_name)
