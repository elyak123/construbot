from construbot.core.functional_tests_base import FunctionalTest
from django.core.urlresolvers import reverse
from selenium.webdriver.common.action_chains import ActionChains
from construbot.proyectos.models import Cliente, Sitio, Destinatario, Contrato

class TestCorrectView(FunctionalTest):

    def test_correct_view_index_admin(self):
        self.user_login()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//strong[contains(text(), 'Contratos Vigentes')]"))

    def test_create_contrato(self):
        self.user_login()
        self.create_proyect_objects(0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_folio'))
        self.browser.find_element_by_id("id_code").send_keys("PRUEBA-1")
        self.browser.find_element_by_id("id_fecha").click()
        self.browser.find_element_by_id("id_contrato_name").send_keys("PRUEBA DE CONTRATO 1")
        self.browser.find_element_by_id("id_contrato_shortName").send_keys("PDC1")
        self.browser.find_element_by_xpath('//span[@aria-labelledby="select2-id_cliente-container"]').click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('select2-search__field'))
        self.browser.find_element_by_class_name('select2-search__field').send_keys("clie")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]").click()
        self.browser.find_element_by_xpath('//span[@aria-labelledby="select2-id_sitio-container"]').click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('select2-search__field'))
        self.browser.find_element_by_class_name('select2-search__field').send_keys("sitio")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'sitio_1')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'sitio_1')]").click()
        self.browser.find_element_by_id("id_monto").send_keys("10000")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del contrato PRUEBA DE CONTRATO 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del contrato PRUEBA DE CONTRATO 1')]")

    def test_contrato_edit(self):
        self.user_login()
        contratos = self.create_proyect_objects(3)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/editar/contrato/{0}/']".format(contratos[2].id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_contrato_name"))
        self.browser.find_element_by_id("id_contrato_name").clear()
        self.browser.find_element_by_id("id_contrato_name").send_keys("EDICION NUMERO 1 A CONTRATO")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        contratos = Contrato.objects.all()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del contrato {0}')]".format(contratos[2].contrato_name)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del contrato {0}')]".format(contratos[2].contrato_name))

    def test_contrato_delete(self):
        self.user_login()
        contratos = self.create_proyect_objects(3)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(contratos), len(vinculos))
        vinculos[0].click()
        self.wait_for(lambda:self.browser.find_element_by_id("button_confirm"))
        self.browser.find_element_by_id("button_confirm").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(contratos)-1, len(vinculos))
        self.browser.find_element_by_xpath("//a[contains(text(), '2. {0}')]".format(contratos[1].contrato_name))
        self.browser.find_element_by_xpath("//a[contains(text(), '1. {0}')]".format(contratos[0].contrato_name))

    def test_cliente_creation(self):
        self.user_login()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_cliente_name'))
        self.browser.find_element_by_id("id_cliente_name").send_keys("CLIENTE DE PRUEBA 1")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente CLIENTE DE PRUEBA 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente CLIENTE DE PRUEBA 1')]")

    def test_cliente_edit(self):
        self.user_login()
        self.create_proyect_objects(0)
        cliente = Cliente.objects.first()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/cliente/{0}/"]'.format(cliente.id)))
        self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/cliente/{0}/"]'.format(cliente.id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_cliente_name'))
        self.browser.find_element_by_id("id_cliente_name").send_keys("EDICION NUMERO 1 A CLIENTE")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente {0}')]".format(cliente.cliente_name)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente {0}')]".format(cliente.cliente_name))

    def test_cliente_delete(self):
        self.user_login()
        self.create_proyect_objects(0)
        clientes = Cliente.objects.all()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(clientes), len(vinculos))
        vinculos[0].click()
        self.wait_for(lambda:self.browser.find_element_by_id("button_confirm"))
        self.browser.find_element_by_id("button_confirm").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(clientes)-1, len(vinculos))
        for i in range(0, len(clientes)-1):
            self.browser.find_element_by_xpath("//a[contains(text(), '{0}. {1}')]".format(i+1, clientes[i+1].cliente_name))

    def test_sitio_creation(self):
        self.user_login()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_sitio_name'))
        self.browser.find_element_by_id("id_sitio_name").send_keys("SITIO DE PRUEBA 1")
        self.browser.find_element_by_id('id_sitio_location').send_keys("LOCACION DE PRUEBA 1")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio SITIO DE PRUEBA 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio SITIO DE PRUEBA 1')]")

    def test_sitio_edition(self):
        self.user_login()
        self.create_proyect_objects(0)
        sitio = Sitio.objects.first()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/sitio/{0}/"]'.format(sitio.id)))
        self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/sitio/{0}/"]'.format(sitio.id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_sitio_name'))
        self.browser.find_element_by_id("id_sitio_name").send_keys("EDICION NUMERO 1 A SITIO")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio {0}')]".format(sitio.sitio_name)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio {0}')]".format(sitio.sitio_name))

    def test_sitio_delete(self):
        self.user_login()
        self.create_proyect_objects(0)
        sitios = Sitio.objects.all()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(sitios), len(vinculos))
        vinculos[0].click()
        self.wait_for(lambda:self.browser.find_element_by_id("button_confirm"))
        self.browser.find_element_by_id("button_confirm").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(sitios)-1, len(vinculos))
        for i in range(0, len(sitios)-1):
            self.browser.find_element_by_xpath("//a[contains(text(), '{0}. {1}')]".format(i+1, sitios[i+1].sitio_name))

    def test_destinatario_creation(self):
        self.user_login()
        self.create_proyect_objects(0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-people").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_tratamiento'))
        self.browser.find_element_by_id("id_tratamiento").send_keys("LIC.")
        self.browser.find_element_by_id('id_destinatario_text').send_keys("DESTINATARIO DE PRUEBA 1")
        self.browser.find_element_by_id('id_puesto').send_keys("SOME")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.browser.find_element_by_xpath('//span[@aria-labelledby="select2-id_cliente-container"]').click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('select2-search__field'))
        self.browser.find_element_by_class_name('select2-search__field').send_keys("clie")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]").click()
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de DESTINATARIO DE PRUEBA 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de DESTINATARIO DE PRUEBA 1')]")

    def test_destinatario_edit(self):
        self.user_login()
        self.create_proyect_objects(0)
        destinatario = Destinatario.objects.first()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = ActionChains(self.browser).move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-people").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[@href='/proyectos/editar/destinatario/{0}/']".format(destinatario.id)))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/editar/destinatario/{0}/']".format(destinatario.id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_destinatario_text"))
        self.browser.find_element_by_id("id_destinatario_text").send_keys("EDICION NUMERO 1 A DESTINATARIO")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de {0}')]".format(destinatario.destinatario_text)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de {0}')]".format(destinatario.destinatario_text))
