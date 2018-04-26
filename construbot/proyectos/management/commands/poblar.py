from construbot.users.tests import factories as user_factories
from construbot.proyectos import factories
from random import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from construbot.proyectos.models import Contrato
from django.utils.six.moves import input


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('flush')
        self.user_factory = user_factories.UserFactory
        customer = []
        for i in range(0, 2):
            customer.append(user_factories.CustomerFactory(customer_name="customer_{0}".format(i)))

        groups = [
            user_factories.GroupFactory(name="proyectos"),
            user_factories.GroupFactory(name="Administrators"),
            user_factories.GroupFactory(name="users"),
        ]

        self.user = self.user_factory(
            username="carlos", password="password", customer=customer[0], groups=groups
        )

        self.user_2 = self.user_factory(
            username="daniel", password="password", customer=customer[1], groups=groups
        )

        company = []
        for i in range(0, 10):
            if i > 4:
                company.append(factories.CompanyFactory(customer=customer[0], company_name='company_{0}'.format(i)))
            else:
                company.append(factories.CompanyFactory(customer=customer[1], company_name='company_{0}'.format(i)))

        self.user.currently_at = company[0]
        self.user.company = company[0:5]
        self.user_2.currently_at = company[5]
        self.user_2.company = company[5:10]

        clientes = []
        sitios = []
        for i in range(0, 30):
            rand = round(random() * 9)
            clientes.append(factories.ClienteFactory(
                company=company[rand], cliente_name='cliente_{0}'.format(i))
            )
            sitios.append(factories.SitioFactory(
                company=company[rand], sitio_name='sitio_{0}'.format(i)))

        destinatarios = []
        for i in range(0, 30):
            destinatarios.append(factories.DestinatarioFactory(
                cliente=clientes[round(random() * 29)], destinatario_text='destinatario_{0}'.format(i))
            )

        contratos = []
        date = datetime.now()
        for i in range(0, 500):
            date = date + timedelta(days=1)
            count = round(random() * 29)
            comp = clientes[count].company
            max_id = len(Contrato.objects.filter(cliente__company=comp))
            contratos.append(factories.ContratoFactory(
                folio=max_id + 1,
                code="CON{0}".format(i),
                fecha=date,
                contrato_name='Contrato numero {0}'.format(i),
                contrato_shortName="ConNum{0}".format(i),
                cliente=clientes[count],
                sitio=sitios[count],)
            )

        units = []
        for i in range(0, 200):
            units.append(factories.UnitFactory(unit='unit{0}'.format(i)))

        concepts = []
        for i in range(0, 2000):
            concepts.append(factories.ConceptoFactory(
                code=i,
                concept_text="Concepto{0}".format(i),
                project=contratos[round(random() * 499)],
                unit=units[round(random() * 199)],
            ))

        self.stdout.write(self.style.SUCCESS(
            "La base de datos ha sido eliminada y poblada exitosamente con:\n" +
            "- 2 Customer\n- 2 Clientes\n- 10 Compañías\n- 30 Clientes\n- 30 Sitios\n- 500 Contratos\n" +
            "- 200 Unidades\n- 2000 Conceptos."
        ))
