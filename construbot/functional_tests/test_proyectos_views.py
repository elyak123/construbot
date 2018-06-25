from .functional_tests_base import FunctionalTest
from construbot.proyectos.models import Cliente, Sitio, Destinatario, Contrato
from django.contrib.auth.models import Group
from django.test import tag


@tag("index")
class TestCorrectIndex(FunctionalTest):
    def test_correct_view_index_admin(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//strong[contains(text(), 'Contratos Vigentes')]"))

    def test_index_when_empty_company(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//strong[contains(text(), 'Contratos Vigentes')]"))
        self.browser.find_element_by_xpath("//td[contains(text(), '¡No hay contratos vigentes!')]")


@tag("lists")
class TestCorrectListsViews(FunctionalTest):
    def test_correct_contrato_list(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 0, 15, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("div_list"))
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(10, len(list_elements))
        self.browser.find_element_by_xpath("//span[contains(text(), 'Siguiente')]").click()
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(5, len(list_elements))

    def test_correct_cliente_list(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(15, 1, 0, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("div_list"))
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(10, len(list_elements))
        self.browser.find_element_by_xpath("//span[contains(text(), 'Siguiente')]").click()
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(5, len(list_elements))

    def test_correct_sitio_list(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(15, 1, 0, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("div_list"))
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(10, len(list_elements))
        self.browser.find_element_by_xpath("//span[contains(text(), 'Siguiente')]").click()
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(5, len(list_elements))

    def test_correct_destinatario_list(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(1, 12, 0, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-people").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("div_list"))
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(10, len(list_elements))
        self.browser.find_element_by_xpath("//span[contains(text(), 'Siguiente')]").click()
        list_elements = self.browser.find_elements_by_class_name("div_list")
        self.assertEqual(2, len(list_elements))


@tag("creation")
class TestCreatingObjects(FunctionalTest):
    def test_create_contrato(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
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
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Reporte de contrato ')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Reporte de contrato ')]")

    def test_create_catalogo_conceptos(self):
        self.user_login(self.user.username, "password")
        contratos = self.create_proyect_objects(1, 0, 2, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[@href='/proyectos/contrato/detalle/{0}/']".format(contratos[0].id)))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/contrato/detalle/{0}/']".format(contratos[0].id)).click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[contains(text(), 'aquí')]"))
        self.browser.execute_script("arguments[0].scrollIntoView(true);", self.browser.find_element_by_xpath("//a[contains(text(), 'aquí')]"))
        self.browser.find_element_by_xpath("//a[contains(text(), 'aquí')]").click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_concept_set-0-code"))
        for i in range(0,4):
            self.browser.find_element_by_id('id_concept_set-%i-code'%i).send_keys('%i'%i)
            self.browser.find_element_by_id('id_concept_set-%i-concept_text'%i).click()
            self.browser.find_element_by_id('id_concept_set-%i-concept_text'%i).send_keys('Concepto {0}'.format(i))
            self.browser.find_element_by_id('id_concept_set-%i-total_cuantity'%i).clear()
            self.browser.find_element_by_id('id_concept_set-%i-total_cuantity'%i).send_keys('%i'%(i+1))
            self.browser.find_element_by_id('id_concept_set-%i-unit_price'%i).clear()
            self.browser.find_element_by_id('id_concept_set-%i-unit_price'%i).send_keys('100')
            self.browser.find_element_by_xpath("//select[@id = 'id_concept_set-%i-unit']/following-sibling::span/child::span/child::span"%i).click()
            self.browser.find_element_by_class_name('select2-search__field').send_keys("unit-{0}".format(i))
            self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Create \"unit-{0}\"')]".format(i)))
            self.browser.find_element_by_xpath("//*[contains(text(), 'Create \"unit-{0}\"')]".format(i)).click()
            if i != 3:
                self.browser.find_element_by_class_name("add-form-row").click()
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("oi-chevron-left"))
        self.browser.find_element_by_class_name("oi-chevron-left").click()
        for i in range(0,4):
            self.browser.find_element_by_xpath("//td[contains(text(), '{0}')]".format(i))
            self.browser.find_element_by_xpath("//td[contains(text(), 'Concepto para probar la creación de conceptos')]")
            self.browser.find_element_by_xpath("//td[contains(text(), 'unit-{0}')]".format(i))
            self.browser.find_element_by_xpath("//td[contains(text(), '{0}.00')]".format(i))
            self.browser.find_element_by_xpath("//td[contains(text(), '$ 100.00')]")

    @tag("estimate")
    def test_create_estimate(self):
        self.user_login(self.user.username, "password")
        contratos = self.create_proyect_objects(4, 4, 2, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[@href='/proyectos/contrato/detalle/{0}/']".format(contratos[0].id)))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/contrato/detalle/{0}/']".format(contratos[0].id)).click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[contains(text(), 'aquí')]"))
        self.browser.find_element_by_xpath("//a[contains(text(), 'aquí')]").click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_concept_set-0-code"))
        for i in range(0,4):
            self.browser.find_element_by_id('id_concept_set-%i-code'%i).send_keys('%i'%i)
            self.browser.find_element_by_id('id_concept_set-%i-concept_text'%i).click()
            self.browser.find_element_by_id('id_concept_set-%i-concept_text'%i).send_keys('Concepto {0}'.format(i))
            self.browser.find_element_by_id('id_concept_set-%i-total_cuantity'%i).clear()
            self.browser.find_element_by_id('id_concept_set-%i-total_cuantity'%i).send_keys('%i'%(i+1))
            self.browser.find_element_by_id('id_concept_set-%i-unit_price'%i).clear()
            self.browser.find_element_by_id('id_concept_set-%i-unit_price'%i).send_keys('100')
            self.browser.find_element_by_xpath("//select[@id = 'id_concept_set-%i-unit']/following-sibling::span/child::span/child::span"%i).click()
            self.browser.find_element_by_class_name('select2-search__field').send_keys("unit-{0}".format(i))
            self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Create \"unit-{0}\"')]".format(i)))
            self.browser.find_element_by_xpath("//*[contains(text(), 'Create \"unit-{0}\"')]".format(i)).click()
            if i != 3:
                self.browser.find_element_by_class_name("add-form-row").click()
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("oi-chevron-left"))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/estimacion/nuevo/{0}/']".format(contratos[0].id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_consecutive"))
        self.browser.find_element_by_id("id_supervised_by").click()
        self.browser.find_element_by_xpath("//option[contains(text(), '{0}')]".format(self.user.username)).click()
        self.browser.find_element_by_id("id_start_date").click()
        self.browser.find_element_by_id("id_finish_date").click()
        self.browser.find_element_by_id("id_consecutive").click()
        self.browser.find_elements_by_class_name("select2-search--inline")[0].click()
        self.browser.find_elements_by_class_name("select2-search__field")[0].send_keys("destinatario")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//li[contains(text(), 'destinatario_3')]"))
        self.browser.find_element_by_class_name("select2-results__option--highlighted").click()
        self.browser.find_elements_by_class_name("select2-search--inline")[1].click()
        self.browser.find_elements_by_class_name("select2-search__field")[1].send_keys("destinatario")
        self.wait_for(lambda:self.browser.find_element_by_class_name("select2-results__option--highlighted"))
        self.browser.find_element_by_class_name("select2-results__option--highlighted").click()
        self.browser.find_element_by_id("id_auth_date").click()
        for i in range(0,4):
            self.browser.find_element_by_id("id_estimateconcept_set-"+str(i)+"-cuantity_estimated").send_keys("10")
            self.browser.find_element_by_id("id_estimateconcept_set-"+str(i)+"-observations").click()
            self.browser.find_element_by_id("id_estimateconcept_set-"+str(i)+"-observations").send_keys("Observacion numero {0}".format(i+1))
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name("title"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del contrato {0}')]".format(contratos[0].contrato_name))
        self.browser.find_element_by_xpath("//a[contains(text(), 'Estimación 1')]")
        
    def test_cliente_creation(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_cliente_name'))
        self.browser.find_element_by_id("id_cliente_name").send_keys("CLIENTE DE PRUEBA 1")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente CLIENTE DE PRUEBA 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente CLIENTE DE PRUEBA 1')]")

    def test_sitio_creation(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_sitio_name'))
        self.browser.find_element_by_id("id_sitio_name").send_keys("SITIO DE PRUEBA 1")
        self.browser.find_element_by_id('id_sitio_location').send_keys("LOCACION DE PRUEBA 1")
        self.browser.find_element_by_xpath('//span[@aria-labelledby="select2-id_cliente-container"]').click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('select2-search__field'))
        self.browser.find_element_by_class_name('select2-search__field').send_keys("clie")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]").click()
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio SITIO DE PRUEBA 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio SITIO DE PRUEBA 1')]")

    def test_destinatario_creation(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-people").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_class_name('oi-plus').click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_destinatario_text'))
        self.browser.find_element_by_id('id_destinatario_text').send_keys("DESTINATARIO DE PRUEBA 1")
        self.browser.find_element_by_id('id_puesto').send_keys("SOME")
        self.browser.find_element_by_xpath('//span[@aria-labelledby="select2-id_cliente-container"]').click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('select2-search__field'))
        self.browser.find_element_by_class_name('select2-search__field').send_keys("clie")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'cliente_1')]").click()
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de DESTINATARIO DE PRUEBA 1')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de DESTINATARIO DE PRUEBA 1')]")


@tag("edition")
class TestEditingObjects(FunctionalTest):
    def test_contrato_edit(self):
        self.user_login(self.user.username, "password")
        contratos = self.create_proyect_objects(5, 5, 3, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-bookmark").click()
        self.wait_for(lambda:self.browser.find_element_by_class_name('oi-plus'))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/editar/contrato/{0}/']".format(contratos[2].id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_contrato_name"))
        self.browser.find_element_by_id("id_contrato_name").clear()
        self.browser.find_element_by_id("id_contrato_name").send_keys("EDICION NUMERO 1 A CONTRATO")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Reporte de contrato ')]"))
        self.browser.find_element_by_xpath("//th[contains(text(), '{0}. {1}')]".format(contratos[2].folio, contratos[2].contrato_shortName))

    def test_destinatario_edit(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        destinatario = Destinatario.objects.first()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-people").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[@href='/proyectos/editar/destinatario/{0}/']".format(destinatario.id)))
        self.browser.find_element_by_xpath("//a[@href='/proyectos/editar/destinatario/{0}/']".format(destinatario.id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_destinatario_text"))
        self.browser.find_element_by_id("id_destinatario_text").send_keys("EDICION NUMERO 1 A DESTINATARIO")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de {0}')]".format(destinatario.destinatario_text)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle de {0}')]".format(destinatario.destinatario_text))

    def test_sitio_edition(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        sitio = Sitio.objects.first()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/sitio/{0}/"]'.format(sitio.id)))
        self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/sitio/{0}/"]'.format(sitio.id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_sitio_name'))
        self.browser.find_element_by_id("id_sitio_name").send_keys("EDICION NUMERO 1 A SITIO")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio {0}')]".format(sitio.sitio_name)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del sitio {0}')]".format(sitio.sitio_name))

    def test_cliente_edit(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        cliente = Cliente.objects.first()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/cliente/{0}/"]'.format(cliente.id)))
        self.browser.find_element_by_xpath('//a[@href="/proyectos/editar/cliente/{0}/"]'.format(cliente.id)).click()
        self.wait_for(lambda:self.browser.find_element_by_id('id_cliente_name'))
        self.browser.find_element_by_id("id_cliente_name").send_keys("EDICION NUMERO 1 A CLIENTE")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente {0}')]".format(cliente.cliente_name)))
        self.browser.find_element_by_xpath("//h2[contains(text(), ' Detalle del cliente {0}')]".format(cliente.cliente_name))


@tag("delete")
class TestDeleteObjects(FunctionalTest):
    def test_contrato_delete(self):
        self.user_login(self.user.username, "password")
        contratos = self.create_proyect_objects(5, 5, 3, 0)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
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

    def test_cliente_delete(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        clientes = Cliente.objects.all()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_xpath("//span[contains(text(), 'Clientes')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(clientes), len(vinculos))
        vinculos[0].click()
        self.wait_for(lambda:self.browser.find_element_by_id("button_confirm"))
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(clientes)-1, len(vinculos))
        for i in range(1, len(clientes)):
            self.browser.find_element_by_xpath("//a[contains(text(), '{0}')]".format(clientes[i].cliente_name))

    def test_sitio_delete(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        sitios = Sitio.objects.all()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-map-marker").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(sitios), len(vinculos))
        vinculos[0].click()
        self.wait_for(lambda:self.browser.find_element_by_id("button_confirm"))
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(sitios)-1, len(vinculos))
        for i in range(1, len(sitios)):
            self.browser.find_element_by_xpath("//a[contains(text(), '{0}')]".format(sitios[i].sitio_name))
    
    def test_destinatario_delete(self):
        self.user_login(self.user.username, "password")
        self.create_proyect_objects(5, 5, 0, 0)
        destinatarios = Destinatario.objects.all()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Proyectos')]").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]"))
        catalogos = self.browser.find_element_by_xpath("//*[contains(text(), 'Catalogos')]")
        hover = self.actions.move_to_element(catalogos)
        hover.perform()
        self.browser.find_element_by_class_name("oi-people").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(destinatarios), len(vinculos))
        vinculos[0].click()
        self.wait_for(lambda:self.browser.find_element_by_id("button_confirm"))
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath('//a[contains(text(), "Eliminar")]'))
        vinculos = self.browser.find_elements_by_xpath('//a[contains(text(), "Eliminar")]')
        self.assertEqual(len(destinatarios)-1, len(vinculos))
        for i in range(1, len(destinatarios)):
            self.browser.find_element_by_xpath("//a[contains(text(), '{0}')]".format(destinatarios[i].destinatario_text))
