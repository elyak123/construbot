from construbot.users.tests import factories as user_factories
from construbot.proyectos.tests import factories
from random import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from construbot.proyectos.models import Contrato, Company
from django.utils.six.moves import input
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class Command(BaseCommand):

    def handle(self, *args, **options):
        if settings.DEBUG:
            call_command('flush')
            self.user_factory = user_factories.UserFactory
            self.create_customer(5)
            self.create_core_groups()
            self.create_user(10)
            self.create_companies(30)
            self.create_clientes(100)
            self.create_sitios(200)
            self.create_destinatarios(200)
            self.create_contratos(1500)
            self.create_units(200)
            self.create_concepts(5000)
            self.stdout.write(self.style.SUCCESS(
            "La base de datos ha sido eliminada y poblada exitosamente con:\n" +
            "- {0} Customer\n- {1} Usuarios\n- {2} Compañías\n- {3}".format(
                len(self.customer),
                len(self.users),
                len(self.company),
                len(self.clientes)) +
            " Clientes\n- {0} Sitios\n- {1} Contratos\n".format(len(self.sitios), len(self.contratos)) +
            "- {0} Unidades\n- {1} Conceptos.".format(len(self.units), len(self.concepts))
            ))
        else:
            raise ImproperlyConfigured('No tienes settings.DEBUG activado, la operación no se puede completar.')

    def create_customer(self, number):
        self.customer = []
        for i in range(0, number):
            self.customer.append(user_factories.CustomerFactory(customer_name="customer_{0}".format(i)))

    def create_core_groups(self):
        self.groups = [
            user_factories.GroupFactory(name="proyectos"),
            user_factories.GroupFactory(name="Administrators"),
            user_factories.GroupFactory(name="users"),
        ]

    def create_user(self, number):
        self.users = []
        if self.customer:
            for i in range(0, number):
                self.users.append(self.user_factory(
                    username="user_{0}".format(i),
                    password="password",
                    customer=self.customer[round(random()*len(self.customer)-1)],
                    groups=self.groups
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
            for comp in Company.objects.all():
                self.users[round(random()*len(self.users)-1)].company.add(comp)
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
            if self.company:
                rand = round(random() * len(self.company)-1)
                self.sitios.append(
                    factories.SitioFactory(
                        company=self.company[rand],
                        sitio_name='sitio_{0}'.format(i)
                    )
                )
            else:
                raise ImproperlyConfigured('¡No existen compañías para asignarles a los sitios!')

    def create_destinatarios(self, number):
        self.destinatarios = []
        for i in range(0, number):
            if self.clientes:
                self.destinatarios.append(factories.DestinatarioFactory(
                    cliente=self.clientes[round(random() * len(self.clientes)-1)],
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

    def create_units(self, number):
        self.units = []
        for i in range(0, number):
            self.units.append(factories.UnitFactory(unit='unit{0}'.format(i)))

    def create_concepts(self, number):
        self.concepts = []
        for i in range(0, number):
            if self.contratos and self.units:
                self.concepts.append(factories.ConceptoFactory(
                    code=i,
                    concept_text="Concepto{0}".format(i),
                    project=self.contratos[round(random() * len(self.contratos)-1)],
                    unit=self.units[round(random() * len(self.units)-1)],
                ))
            else:
                raise ImproperlyConfigured('¡No existen contratos y/o unidades para asignarles a los conceptos!')
