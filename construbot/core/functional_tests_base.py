from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium                   import webdriver
from django.contrib.auth.models import Permission
from selenium.common.exceptions import WebDriverException
import os
import time
from construbot.users.tests import factories as user_factories
from construbot.proyectos.tests import factories
from selenium.webdriver.common.keys import Keys
from construbot.proyectos.models import Company, Sitio, Destinatario, Contrato
from random import random
from datetime import datetime, timedelta

MAX_WAIT = 4


@override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        
        self.user_factory = user_factories.UserFactory
        self.user = self.user_factory()
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        admin = user_factories.GroupFactory(name='Administrators')
        users = user_factories.GroupFactory(name='users')
        proyects = user_factories.GroupFactory(name='proyectos')
        for group in admin, users, proyects:
            self.user.groups.add(group)
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.user2 = self.user_factory()
        self.user2.company.add(company_test)
        self.user2.currently_at = company_test

    def user_login(self):
        url = self.live_server_url + '/accounts/login/'
        self.browser.get(url)
        username_field = self.browser.find_element_by_name('login')
        password_field = self.browser.find_element_by_name('password')
        username_field.send_keys(self.user.username)
        password_field.send_keys('password')
        password_field.send_keys(Keys.ENTER)

    def create_proyect_objects(self, n_contratos):
        clientes = []
        sitios = []
        for i in range(0, 5):
            clientes.append(factories.ClienteFactory(
                company=self.user.currently_at, cliente_name='cliente_{0}'.format(i))
            )
            sitios.append(factories.SitioFactory(
                company=self.user.currently_at, sitio_name='sitio_{0}'.format(i)))

        destinatarios = []
        for i in range(0, 5):
            destinatarios.append(factories.DestinatarioFactory(
                cliente=clientes[round(random() * 4)], destinatario_text='destinatario_{0}'.format(i))
            )

        if n_contratos:
            date = datetime.now()
            comp = clientes[0].company
            contratos=[]
            for i in range(0, n_contratos):
                date += timedelta(days=1)
                max_id = len(Contrato.objects.filter(cliente__company=comp))
                contratos.append(factories.ContratoFactory(
                    folio=max_id + 1,
                    code="CON{0}".format(i),
                    fecha=date,
                    contrato_name='Contrato numero {0}'.format(i),
                    contrato_shortName="ConNum{0}".format(i),
                    cliente=clientes[0],
                    sitio=sitios[0],
                ))
            return contratos

    def tearDown(self):
        self.browser.quit()

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)