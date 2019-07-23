from django.test import RequestFactory
from django.contrib.auth.models import Group
from test_plus.test import CBVTestCase
from construbot.users.models import NivelAcceso
from . import factories


class BaseTestCase(CBVTestCase):

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.auxiliar_permission, aux_created = NivelAcceso.objects.get_or_create(nivel=1, nombre='Auxiliar')
        self.coordinador_permission, coord_created = NivelAcceso.objects.get_or_create(nivel=2, nombre='Coordinador')
        self.director_permission, dir_created = NivelAcceso.objects.get_or_create(nivel=3, nombre='Director')
        self.corporativo_permission, corp_created = NivelAcceso.objects.get_or_create(nivel=4, nombre='Corporativo')
        self.soporte_permission, soporte_created = NivelAcceso.objects.get_or_create(nivel=5, nombre='Soporte')
        self.user_group, usr_gp_created = Group.objects.get_or_create(name='Users')
        self.proyectos_group, py_gp_created = Group.objects.get_or_create(name='Proyectos')
        self.admin_group, admin_gp_created = Group.objects.get_or_create(name='Administrators')
        self.user = self.user_factory(nivel_acceso=self.auxiliar_permission)
        self.factory = RequestFactory()

    def get_request(self, user, url='bla/bla'):
        request = self.factory.get(url)
        request.user = user
        return request
