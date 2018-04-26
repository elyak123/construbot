from construbot.users.tests import factories as user_factories
from construbot.proyectos import factories
from random import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from construbot.proyectos.models import Contrato


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.user_factory = user_factories.UserFactory
        customer = user_factories.CustomerFactory(customer_name="some")
        groups = [
            user_factories.GroupFactory(name="proyectos"),
            user_factories.GroupFactory(name="Administrators"),
            user_factories.GroupFactory(name="users"),
        ]
        self.user = self.user_factory(
            username="carlos", password="daniel007b1999", customer=customer, groups=groups
        )

        company = []
        for i in range(0, 10):
            company.append(factories.CompanyFactory(customer=customer, company_name='company_{0}'.format(i)))

        self.user.currently_at = company[0]
        self.user.company = company

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
        for i in range(0, 100):
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
