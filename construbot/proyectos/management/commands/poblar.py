from random import random
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.exceptions import ImproperlyConfigured
from construbot.users.tests import factories as user_factories
from construbot.users.utils import establish_access_levels
from construbot.users.models import NivelAcceso
from construbot.proyectos.tests import factories
from construbot.proyectos.models import Contrato


class Command(BaseCommand):

    def handle(self, *args, **options):
        if settings.DEBUG:
            call_command('flush')
            self.user_factory = user_factories.UserFactory
            self.create_customer(5)
            self.create_core_groups()
            establish_access_levels()
            self.create_user(20)
            self.create_companies(30)
            self.create_clientes(100)
            self.create_sitios(200)
            self.create_destinatarios(200)
            self.create_contratos(1500)
            self.create_concepts(5000)
            self.stdout.write(self.style.SUCCESS(
                "La base de datos ha sido eliminada y poblada exitosamente con:\n" +
                "- {0} Customer\n- {1} Usuarios\n- {2} Compañías\n- {3}".format(
                    len(self.customer),
                    len(self.users),
                    len(self.company),
                    len(self.clientes)) +
                " Clientes\n- {0} Sitios\n- {1} Contratos\n".format(len(self.sitios), len(self.contratos)) +
                "- {0} Conceptos.".format(len(self.concepts))
            ))
        else:
            raise ImproperlyConfigured('No tienes settings.DEBUG activado, la operación no se puede completar.')

    def create_customer(self, number):
        self.customer = []
        for i in range(0, number):
            self.customer.append(user_factories.CustomerFactory(customer_name="customer_{0}".format(i)))

    def create_core_groups(self):
        self.groups = [
            user_factories.GroupFactory(name="Proyectos"),
            user_factories.GroupFactory(name="Administrators"),
            user_factories.GroupFactory(name="Users"),
        ]

    def create_user(self, number):
        self.users = []
        if self.customer:
            for i in range(0, number):
                self.users.append(self.user_factory(
                    username="user_{0}".format(i),
                    password="password",
                    customer=self.customer[round(random()*len(self.customer)-1)],
                    groups=self.groups,
                    nivel_acceso=NivelAcceso.objects.get(nivel=4)
                ))
        else:
            raise ImproperlyConfigured('¡No hay customer para asignar a usuario!')

    def create_companies(self, number):
        self.company = []
        if self.customer:
            for i in range(0, number):
                self.company.append(
                    factories.CompanyFactory(
                        customer=self.customer[round(random()*len(self.customer)-1)],
                        company_name='company_{0}'.format(i)
                        )
                    )
        else:
            raise ImproperlyConfigured('¡No existen customer para asignar a las compañías!')

        if self.users:
            for usr in range(0, len(self.users)-1):
                for company in range(0, len(self.company)):
                    if (round(random()*1.1)) and self.users[usr].customer == self.company[company].customer:
                        self.users[usr].company.add(self.company[company])
        else:
            raise ImproperlyConfigured('¡No existen usuarios para asignarles las compañías!')

    def create_clientes(self, number):
        self.clientes = []
        for i in range(0, number):
            if self.company:
                rand = round(random() * len(self.company)-1)
                self.clientes.append(
                    factories.ClienteFactory(
                        company=self.company[rand],
                        cliente_name='cliente_{0}'.format(i))
                    )
            else:
                raise ImproperlyConfigured('¡No existen compañías para asignarles a los clientes!')

    def create_sitios(self, number):
        self.sitios = []
        for i in range(0, number):
            if self.clientes:
                rand = round(random() * len(self.company)-1)
                self.sitios.append(
                    factories.SitioFactory(
                        cliente=self.clientes[rand],
                        sitio_name='sitio_{0}'.format(i)
                    )
                )
            else:
                raise ImproperlyConfigured('¡No existen compañías para asignarles a los sitios!')

    def create_destinatarios(self, number):
        self.destinatarios = []
        for i in range(0, number):
            if self.clientes:
                cliente = self.clientes[round(random() * len(self.clientes)-1)]
                self.destinatarios.append(factories.DestinatarioFactory(
                    cliente=cliente,
                    destinatario_text='destinatario_{0}'.format(i))
                )
            else:
                raise ImproperlyConfigured('¡No existen clientes para asignarles a los destinatarios!')

    def create_contratos(self, number):
        self.contratos = []
        date = datetime.now()
        if self.clientes and self.sitios:
            for i in range(0, number):
                date = date + timedelta(days=1)
                count_cl = round(random() * len(self.clientes)-1)
                count_sit = round(random() * len(self.sitios)-1)
                comp = self.clientes[count_cl].company
                max_id = len(Contrato.objects.filter(cliente__company=comp))
                self.contratos.append(factories.ContratoFactory(
                    folio=max_id + 1,
                    code="CON{0}".format(i),
                    fecha=date,
                    contrato_name='Contrato numero {0}'.format(i),
                    contrato_shortName="ConNum{0}".format(i),
                    cliente=self.clientes[count_cl],
                    sitio=self.sitios[count_sit],)
                )
        else:
            raise ImproperlyConfigured('¡No existen clientes y/o sitios para asignarles a los contratos!')

    def create_concepts(self, number):
        self.concepts = []
        for i in range(0, number):
            if self.contratos:
                contrato = self.contratos[round(random() * len(self.contratos)-1)]
                self.concepts.append(factories.ConceptoFactory(
                    code=i,
                    concept_text="Concepto{0}".format(i),
                    project=contrato,
                    unit=factories.UnitFactory(
                        unit='unit{0}'.format(i),
                        company=contrato.cliente.company)
                ))
            else:
                raise ImproperlyConfigured('¡No existen contratos y/o unidades para asignarles a los conceptos!')

    def random_index_from_list(self, _list):
        index = round(random() * (len(_list) - 1))
        return index
