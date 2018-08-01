from construbot.users.tests import factories as user_factories
from django.core.urlresolvers import reverse, resolve
from construbot.proyectos.models import Estimate
from . import factories
from test_plus.test import TestCase


class TestProyectsURLsCorrectTemplates(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        administrador = user_factories.GroupFactory(name="Administrators")
        proyectos = user_factories.GroupFactory(name="Proyectos")
        users = user_factories.GroupFactory(name="Users")
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
    @tag('current')
    def test_clientes_list_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.currently_at = company_test
        cliente_test = factories.ClienteFactory(company=company_test)
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

    def test_catalogo_edit_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/catalogo-conceptos-inline.html')

    def test_contrato_detail_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:contrato_detail', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/contrato_detail.html')

    def test_cliente_detail_uses_correct_template(self):
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:cliente_detail', kwargs={'pk': cliente.pk}))
        self.assertTemplateUsed(response, 'proyectos/cliente_detail.html')

    def test_sitio_detail_uses_correct_template(self):
        sitio_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:sitio_detail', kwargs={'pk': sitio.pk}))
        self.assertTemplateUsed(response, 'proyectos/sitio_detail.html')

    def test_destinatario_detail_uses_correct_template(self):
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:destinatario_detail', kwargs={'pk': destinatario.pk}))
        self.assertTemplateUsed(response, 'proyectos/destinatario_detail.html')

    def test_estimate_detail_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:estimate_detail', kwargs={'pk': estimate.pk}))
        self.assertTemplateUsed(response, 'proyectos/estimate_detail.html')

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

    def test_nueva_estimacion_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/estimate_form.html')

    def test_editar_contrato_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_contrato', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_cliente_uses_correct_template(self):
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_cliente', kwargs={'pk': cliente.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_sitio_uses_correct_template(self):
        sitio_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_sitio', kwargs={'pk': sitio.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_destinatario_uses_correct_template(self):
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_destinatario', kwargs={'pk': destinatario.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_estimacion_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_estimacion', kwargs={'pk': estimate.pk}))
        self.assertTemplateUsed(response, 'proyectos/estimate_form.html')

    def test_delete_models_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(
            reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_factory.pk})
        )
        self.assertTemplateUsed(response, 'core/delete.html')


class TestProyectsURLsCorrectStatusCode(TestCase):

    def setUp(self):
        self.user_factory = user_factories.UserFactory
        self.user = self.make_user()
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        administrador = user_factories.GroupFactory(name="Administrators")
        proyectos = user_factories.GroupFactory(name="Proyectos")
        users = user_factories.GroupFactory(name="Users")
        for group in administrador, proyectos, users:
            self.user.groups.add(group)
        self.user.company.add(company_test)
        self.user.currently_at = company_test

    def test_proyects_dashboard_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_contrato_list_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_contratos'))
        self.assertEqual(response.status_code, 200)

    def test_clientes_list_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_clientes'))
        self.assertEqual(response.status_code, 200)

    def test_sitios_list_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_sitios'))
        self.assertEqual(response.status_code, 200)

    def test_destinatarios_list_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_destinatarios'))
        self.assertEqual(response.status_code, 200)

    def test_catalogo_edit_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)

    def test_contrato_detail_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:contrato_detail', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)

    def test_cliente_detail_has_correct_status_code(self):
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:cliente_detail', kwargs={'pk': cliente.pk}))
        self.assertEqual(response.status_code, 200)

    def test_sitio_detail_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=contrato_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:sitio_detail', kwargs={'pk': sitio.pk}))
        self.assertEqual(response.status_code, 200)

    def test_destinatario_detail_has_correct_status_code(self):
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:destinatario_detail', kwargs={'pk': destinatario.pk}))
        self.assertEqual(response.status_code, 200)

    def test_estimate_detail_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:estimate_detail', kwargs={'pk': estimate.pk}))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_contrato_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_cliente_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_cliente'))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_sitio_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_sitio'))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_destinatario_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_destinatario'))
        self.assertEqual(response.status_code, 200)

    def test_nueva_estimacion_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)

    def test_editar_contrato_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_contrato', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)

    def test_editar_cliente_has_correct_status_code(self):
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_cliente', kwargs={'pk': cliente.pk}))
        self.assertEqual(response.status_code, 200)

    def test_editar_sitio_has_correct_status_code(self):
        sitio_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_sitio', kwargs={'pk': sitio.pk}))
        self.assertEqual(response.status_code, 200)

    def test_editar_destinatario_has_correct_status_code(self):
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_destinatario', kwargs={'pk': destinatario.pk}))
        self.assertEqual(response.status_code, 200)

    def test_editar_estimacion_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_estimacion', kwargs={'pk': estimate.pk}))
        self.assertEqual(response.status_code, 200)

    def test_delete_models_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(
            reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_factory.pk})
        )
        self.assertEqual(response.status_code, 200)
