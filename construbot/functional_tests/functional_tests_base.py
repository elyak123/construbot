import os
import time
from random import random
from datetime import datetime, timedelta
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.contrib.auth.models import Permission
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from construbot.users.tests import factories as user_factories
from construbot.proyectos.tests import factories
from construbot.proyectos.models import Company, Sitio, Destinatario, Contrato
from selenium.webdriver.common.action_chains import ActionChains
from django.conf import settings

MAX_WAIT = 10


@override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True
        self.actions = ActionChains(self.browser)
        self.live_server_url = os.environ.get('STAGING_SERVER')

    def user_login(self):
        url = self.live_server_url + '/accounts/login/'
        self.browser.get(url)
        username_field = self.browser.find_element_by_name('login')
        password_field = self.browser.find_element_by_name('password')
        username_field.send_keys(settings.USERNAME_TEST)
        password_field.send_keys(settings.PWD_TEST)
        password_field.send_keys(Keys.ENTER)

    # def create_proyect_objects(self, n_clientsitios, n_destinatarios, n_contratos, n_companies):
    #     clientes = []
    #     sitios = []
    #     for i in range(0, n_clientsitios):
    #         clientes.append(factories.ClienteFactory(
    #             company=self.user.currently_at, cliente_name='cliente_{0}'.format(i))
    #         )
    #         sitios.append(factories.SitioFactory(
    #             cliente=clientes[round(random() * len(clientes)-1)], sitio_name='sitio_{0}'.format(i)))

    #     destinatarios = []
    #     for i in range(0, n_destinatarios):
    #         destinatarios.append(factories.DestinatarioFactory(
    #             cliente=clientes[round(random() * n_clientsitios-1)], destinatario_text='destinatario_{0}'.format(i))
    #         )

    #     if n_companies:
    #         company=[]
    #         for i in range(0, n_companies):
    #             company = user_factories.CompanyFactory(customer=self.user.customer)
    #             self.user.company.add(company)
    #             self.user2.company.add(company)

    #     if n_contratos:
    #         date = datetime.now()
    #         comp = clientes[0].company
    #         contratos=[]
    #         for i in range(0, n_contratos):
    #             date += timedelta(days=1)
    #             max_id = len(Contrato.objects.filter(cliente__company=comp))
    #             contratos.append(factories.ContratoFactory(
    #                 folio=max_id + 1,
    #                 code="CON{0}".format(i),
    #                 fecha=date,
    #                 contrato_name='Contrato numero {0}'.format(i),
    #                 contrato_shortName="ConNum{0}".format(i),
    #                 cliente=clientes[0],
    #                 sitio=sitios[0],
    #             ))
    #         return contratos

    def fast_multiselect(self, element_id, labels):
            select = Select(self.browser.find_element_by_id(element_id))
            select.deselect_all()
            for label in labels:
                select.select_by_visible_text(label)

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