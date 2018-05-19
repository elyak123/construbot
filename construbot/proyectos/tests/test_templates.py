from construbot.users.tests import factories
from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase

class TestProyectsURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        company_test = factories.CompanyFactory(customer=self.user.customer)
        administrador = factories.GroupFactory(name="Administrators")
        proyectos = factories.GroupFactory(name="Proyectos")
        users = factories.GroupFactory(name="Users")
        for group in administrador, proyectos, users:
            self.user.groups.add(group)
        self.user.company.add(company_test)
        self.user.currently_at = company_test

    def test_proyects_dashboard_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        self.assertTemplateUsed(response, 'proyectos/index.html')

    def test_contrato_list_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_contratos'))
        self.assertTemplateUsed(response, 'proyectos/contrato_list.html')

    def test_clientes_list_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_clientes'))
        self.assertTemplateUsed(response, 'proyectos/cliente_list.html')

    def test_sitios_list_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_sitios'))
        self.assertTemplateUsed(response, 'proyectos/sitio_list.html')

    def test_destinatarios_list_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_destinatarios'))
        self.assertTemplateUsed(response, 'proyectos/destinatario_list.html')

    # def test_catalogo_edit_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:catalogo_conceptos', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_catalogo_list_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:catalogo_conceptos_listado', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/concept_list.html')

    # def test_contrato_detail_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:contrato_detail', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_cliente_detail_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:cliente_detail', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_sitio_detail_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:sitio_detail', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_destinatario_detail_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:destinatario_detail', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_estimate_detail_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:estimate_detail', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    def test_nuevo_contrato_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_cliente_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_cliente'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_sitio_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_sitio'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_destinatario_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_destinatario'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    # def test_nueva_estimacion_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:nueva_estimacion', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/estimate_form.html')

    # def test_editar_contrato_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:editar_contrato', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_editar_cliente_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:editar_cliente', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_editar_sitio_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:editar_sitio', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_editar_destinatario_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:editar_destinatario', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_editar_estimacion_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:editar_estimacion', kwargs={'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')

    # def test_delete_models_uses_correct_template(self):
    #     self.client.login(username=self.user.username, password='password')
    #     response = self.client.get(reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': 1}))
    #     self.assertTemplateUsed(response, 'proyectos/')