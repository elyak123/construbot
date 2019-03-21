import os
from unittest import skipIf
from django.urls import reverse
from django.test import tag
from construbot.users.tests import utils, factories as user_factories
from construbot.proyectos.models import Estimate
from . import factories


class TestBaseTemplates(utils.BaseTestCase):
    def setUp(self):
        super(TestBaseTemplates, self).setUp()
        for group in self.admin_group, self.proyectos_group, self.user_group:
            self.user.groups.add(group)
        company_test = user_factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_test)
        self.user.currently_at = company_test


class ProyectDashboardIndexTemplate(TestBaseTemplates):

    def test_proyects_dashboard_uses_correct_template_if_not_is_new(self):
        self.user.is_new = False
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        self.assertTemplateUsed(response, 'proyectos/index.html')

    @skipIf(os.environ.get('TRAVIS_ENVIRON', False), 'Do not run over Travis')
    def test_proyects_dashboard_correct_html_if_is_new_and_coordinador(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.is_new = True
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        url_remove_is_new = reverse('users:remove_is_new', kwargs={'pk': self.user.pk})
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        nuevo_contrato_url = reverse('proyectos:nuevo_contrato')
        text = f"""
            <script type="text/javascript">
                let fuera = false;
                document.getElementById('startButton').onclick = function() {{
                    fuera = true;
                    introJs().setOptions({{'doneLabel': 'Crea tu primer contrato', 'showBullets': false}}).start().oncomplete(function() {{
                        window.location.href = "{nuevo_contrato_url}";
                    }});
                }};
                $("#tutorialModal").modal();
                $('#tutorialModal').on('hidden.bs.modal', function (e) {{
                    if(!fuera){{document.getElementById('startButton').click();}}
                }});
                $("#omitir").on("click", function(){{
                    let POST_token = $("#user_form").serialize();
                    $.ajax({{
                        type: 'POST',
                        url: '{url_remove_is_new}',
                        data: POST_token,
                        success: function(result){{
                            window.location.reload();
                        }}
                    }});
                }});
            </script>
        """
        self.assertContains(response, text, html=True, msg_prefix=response.content.decode().strip('\n'))

    def test_proyects_dashboard_correct_html_if_not_new_and_director(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        contrato = factories.ContratoFactory(cliente__company=company_test, monto=150000)
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.user.nivel_acceso = self.director_permission
        self.user.is_new = False
        self.user.save()
        contrato_url = reverse('proyectos:contrato_detail', kwargs={'pk': contrato.pk})
        text = f"""
        <div class="col-md-6"><p><strong>Contratos Vigentes</strong></p>
        <table class="table_sample table_left"><tr><th>Nombre</th><th>Avance General</th></tr><tr><td>
        <a href="{contrato_url}">{contrato.folio}. {contrato.contrato_shortName}</a><br>
        Cliente: {contrato.cliente.cliente_name}</td><td style="text-align:center;">0.00 %</td></tr>
        <tr><td>Total Contratos Vigentes</td><td>150,000.00</td></tr></table></div>
        """
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        error_message = response.content.decode().strip('\n') + '\n\n\n-------\n'
        self.assertContains(response, text, html=True, msg_prefix=error_message)

    def test_proyects_dashboard_correct_html_if_not_new_and_auxiliar(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        contrato = factories.ContratoFactory(cliente__company=company_test, monto=150000)
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.user.is_new = False
        self.user.save()
        contrato_url = reverse('proyectos:contrato_detail', kwargs={'pk': contrato.pk})
        text = f"""
        <div class="col-md-6"><p><strong>Contratos Vigentes</strong></p>
        <table class="table_sample table_left"><tr><th>Nombre</th><th>Avance General</th></tr><tr><td>
        <a href="{contrato_url}">{contrato.folio}. {contrato.contrato_shortName}</a><br>
        Cliente: {contrato.cliente.cliente_name}</td><td style="text-align:center;">0.00 %</td></tr>
        <tr><td>Total Contratos Vigentes</td><td>150,000.00</td></tr></table></div>
        """
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        error_message = response.content.decode().strip('\n') + '\n\n\n-------\n'
        self.assertNotContains(response, text, html=True, msg_prefix=error_message)

    @skipIf(os.environ.get('TRAVIS_ENVIRON', False), 'Do not run over Travis')
    def test_proyects_dashboard_uses_correct_template_if_is_new_and_not_coordinador(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.is_new = True
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        self.client.login(username=self.user.username, password='password')
        url_remove_is_new = reverse('users:remove_is_new', kwargs={'pk': self.user.pk})
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        remove_is_new = reverse('users:remove_is_new', kwargs={'pk': self.user.pk})
        text = f"""
            <script type="text/javascript">
                let fuera = false;
                document.getElementById('startButton').onclick = function() {{
                    fuera = true;
                    introJs().setOptions({{'doneLabel': '¡Terminar!', 'showBullets': false}}).start().oncomplete(function() {{
                        let POST_token = $("#user_form").serialize();
                        $.ajax({{
                            type: 'POST',
                            url: '{remove_is_new}',
                            data: POST_token,
                            success: function(result){{
                                window.location.reload();
                            }}
                        }});
                    }});
                }};
                $("#tutorialModal").modal();
                $('#tutorialModal').on('hidden.bs.modal', function (e) {{
                    if(!fuera){{document.getElementById('startButton').click();}}
                }});
                $("#omitir").on("click", function(){{
                    let POST_token = $("#user_form").serialize();
                    $.ajax({{
                        type: 'POST',
                        url: '{url_remove_is_new}',
                        data: POST_token,
                        success: function(result){{
                            window.location.reload();
                        }}
                    }});
                }});
            </script>
        """
        self.assertContains(response, text, html=True)

    def test_proyects_dashboard_has_correct_html_if_is_new(self):
        company_test = factories.CompanyFactory(customer=self.user.customer)
        self.user.is_new = True
        self.user.company.add(company_test)
        self.user.currently_at = company_test
        text = """
            Este es el espacio de trabajo de Construbot, en este tutorial aprenderás 
            lo básico del uso de la aplicación, además de asignarte un nombre de 
            usuario y generar tu primer compañía.
        """
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        self.assertTemplateUsed(response, 'proyectos/index.html')
        self.assertContains(response, text, html=True)

    def test_proyects_dashboard_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:proyect_dashboard'))
        self.assertEqual(response.status_code, 200)


class ContratoListTemplates(TestBaseTemplates):

    def test_contrato_list_uses_correct_template(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_contratos'))
        self.assertTemplateUsed(response, 'proyectos/contrato_list.html')

    def test_contrato_list_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_contratos'))
        self.assertEqual(response.status_code, 200)


class ClienteListTemplate(TestBaseTemplates):

    def test_clientes_list_uses_correct_template(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        for i in range(0, 11):
            cliente = factories.ClienteFactory(company=self.user.currently_at)
            contrato = factories.ContratoFactory(cliente=cliente)
            self.user.contrato_set.add(contrato)
        response = self.client.get('/proyectos/listado/clientes/?page=2')
        self.assertTemplateUsed(response, 'proyectos/cliente_list.html')

    def test_clientes_list_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_clientes'))
        self.assertEqual(response.status_code, 200)


class SitiosListTemplate(TestBaseTemplates):

    def test_sitios_list_uses_correct_template(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_sitios'))
        self.assertTemplateUsed(response, 'proyectos/sitio_list.html')

    def test_sitios_list_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_sitios'))
        self.assertEqual(response.status_code, 200)


class DestinatariosListTemplate(TestBaseTemplates):

    def test_destinatarios_list_uses_correct_template(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_destinatarios'))
        self.assertTemplateUsed(response, 'proyectos/destinatario_list.html')

    def test_destinatarios_list_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:listado_de_destinatarios'))
        self.assertEqual(response.status_code, 200)


class CatalogoConceptosInlineTemplate(TestBaseTemplates):

    def test_catalogo_edit_uses_correct_template(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/catalogo-conceptos-inline.html')

    def test_catalogo_edit_has_correct_status_code(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:catalogo_conceptos', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)


class ContratoDetailTemplate(TestBaseTemplates):

    def test_contrato_detail_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        contrato_factory.users.add(self.user)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:contrato_detail', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/contrato_detail.html')

    def test_contrato_detail_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        contrato_factory.users.add(self.user)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:contrato_detail', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)


class ClienteDetailTemplate(TestBaseTemplates):

    def test_cliente_detail_uses_correct_template(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:cliente_detail', kwargs={'pk': cliente.pk}))
        self.assertTemplateUsed(response, 'proyectos/cliente_detail.html')

    def test_cliente_detail_has_correct_status_code(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:cliente_detail', kwargs={'pk': cliente.pk}))
        self.assertEqual(response.status_code, 200)


class TitioDetailTemplate(TestBaseTemplates):

    def test_sitio_detail_uses_correct_template(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        sitio = factories.SitioFactory(cliente__company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:sitio_detail', kwargs={'pk': sitio.pk}))
        self.assertTemplateUsed(response, 'proyectos/sitio_detail.html')

    def test_sitio_detail_has_correct_status_code(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=contrato_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:sitio_detail', kwargs={'pk': sitio.pk}))
        self.assertEqual(response.status_code, 200)


class DestinatarioDetailTemplate(TestBaseTemplates):

    def test_destinatario_detail_uses_correct_template(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        destinatario = factories.DestinatarioFactory(cliente__company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:destinatario_detail', kwargs={'pk': destinatario.pk}))
        self.assertTemplateUsed(response, 'proyectos/destinatario_detail.html')

    def test_destinatario_detail_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:destinatario_detail', kwargs={'pk': destinatario.pk}))
        self.assertEqual(response.status_code, 200)


class EstimateDetailTemplate(TestBaseTemplates):

    def test_estimate_detail_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        destinatario = factories.DestinatarioFactory(cliente=contrato_cliente)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        concepto = factories.ConceptoFactory(
            project=contrato_factory
        )
        factories.EstimateConceptFactory(
            estimate=estimate,
            concept=concepto
        )
        estimate2 = Estimate.objects.create(
            project=contrato_factory,
            consecutive=2,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-20',
            finish_date='1999-08-20',
        )
        estimate2.auth_by.add(destinatario.id)
        estimate2.auth_by_gen.add(destinatario.id)
        factories.ConceptoFactory(
            project=contrato_factory
        )
        factories.EstimateConceptFactory(
            estimate=estimate,
            concept=concepto
        )
        estimate.save()
        estimate2.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:estimate_detail', kwargs={'pk': estimate2.pk}))
        self.assertTemplateUsed(response, 'proyectos/estimate_detail.html')
        self.assertTemplateUsed(response, 'proyectos/concept_estimate.html')
        self.assertTemplateUsed(response, 'proyectos/concept_generator.html')

    def test_estimate_detail_has_correct_status_code(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
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


class CreationFormTemplate(TestBaseTemplates):

    def test_nuevo_contrato_uses_correct_template(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_contrato_uses_correct_template_when_user_is_new(self):
        self.user.is_new = False
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_contrato_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_contrato'))
        self.assertEqual(response.status_code, 200)

    def test_editar_contrato_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato_factory.users.add(self.user)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_contrato', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_contrato_has_correct_status_code(self):
        self.user.nivel_acceso = self.coordinador_permission
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        contrato_factory.users.add(self.user)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_contrato', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_cliente_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_cliente'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_cliente_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_cliente'))
        self.assertEqual(response.status_code, 200)

    def test_editar_cliente_uses_correct_template(self):
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_cliente', kwargs={'pk': cliente.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_cliente_has_correct_status_code(self):
        cliente = factories.ClienteFactory(company=self.user.company.first())
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_cliente', kwargs={'pk': cliente.pk}))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_sitio_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_sitio'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_sitio_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_sitio'))
        self.assertEqual(response.status_code, 200)

    def test_editar_sitio_uses_correct_template(self):
        sitio_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_sitio', kwargs={'pk': sitio.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_sitio_has_correct_status_code(self):
        sitio_cliente = factories.ClienteFactory(company=self.user.company.first())
        sitio = factories.SitioFactory(cliente=sitio_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_sitio', kwargs={'pk': sitio.pk}))
        self.assertEqual(response.status_code, 200)

    def test_nuevo_destinatario_uses_correct_template(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_destinatario'))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_nuevo_destinatario_has_correct_status_code(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nuevo_destinatario'))
        self.assertEqual(response.status_code, 200)

    def test_editar_destinatario_uses_correct_template(self):
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_destinatario', kwargs={'pk': destinatario.pk}))
        self.assertTemplateUsed(response, 'proyectos/creation_form.html')

    def test_editar_destinatario_has_correct_status_code(self):
        destinatario_cliente = factories.ClienteFactory(company=self.user.company.first())
        destinatario = factories.DestinatarioFactory(cliente=destinatario_cliente)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:editar_destinatario', kwargs={'pk': destinatario.pk}))
        self.assertEqual(response.status_code, 200)


class DeleteModelTemplateTest(TestBaseTemplates):

    def test_delete_models_uses_correct_template(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        contrato_factory.users.add(self.user)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(
            reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_factory.pk})
        )
        self.assertTemplateUsed(response, 'core/delete.html')

    def test_delete_models_has_correct_status_code(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        contrato_factory.users.add(self.user)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(
            reverse('proyectos:eliminar', kwargs={'model': 'Contrato', 'pk': contrato_factory.pk})
        )
        self.assertEqual(response.status_code, 200)


class EstimateFormTemplate(TestBaseTemplates):

    def test_nueva_estimacion_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato_factory.pk}))
        self.assertTemplateUsed(response, 'proyectos/estimate_form.html')

    def test_nueva_estimacion_has_correct_status_code(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('proyectos:nueva_estimacion', kwargs={'pk': contrato_factory.pk}))
        self.assertEqual(response.status_code, 200)

    def test_editar_estimacion_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
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

    def test_editar_estimacion_has_correct_status_code(self):
        self.user.nivel_acceso = self.director_permission
        self.user.save()
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


class ConceptGeneratorTemplateTest(TestBaseTemplates):

    def test_generator_pdf_print_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        destinatario = factories.DestinatarioFactory(cliente=contrato_cliente)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        concepto = factories.ConceptoFactory(
            project=contrato_factory
        )
        factories.EstimateConceptFactory(
            estimate=estimate,
            concept=concepto
        )
        estimate2 = Estimate.objects.create(
            project=contrato_factory,
            consecutive=2,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-20',
            finish_date='1999-08-20',
        )
        estimate2.auth_by.add(destinatario.id)
        estimate2.auth_by_gen.add(destinatario.id)
        factories.ConceptoFactory(
            project=contrato_factory
        )
        factories.EstimateConceptFactory(
            estimate=estimate,
            concept=concepto
        )
        estimate.save()
        estimate2.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(
            reverse('proyectos:generator_detailpdf', kwargs={'pk': estimate2.pk}),
            {'as': 'html'}
        )
        self.assertTemplateNotUsed(response, 'proyectos/estimate_detail.html')
        self.assertTemplateNotUsed(response, 'proyectos/concept_estimate.html')
        self.assertTemplateUsed(response, 'proyectos/concept_generator.html')
        self.assertContains(response, '<!DOCTYPE html>', html=True)


class ConceptEstimateTemplateTest(TestBaseTemplates):

    def test_estimate_pdf_print_uses_correct_template(self):
        contrato_cliente = factories.ClienteFactory(company=self.user.company.first())
        contrato_sitio = factories.SitioFactory(cliente=contrato_cliente)
        contrato_factory = factories.ContratoFactory(cliente=contrato_cliente, sitio=contrato_sitio, monto=90.00)
        self.user.nivel_acceso = self.director_permission
        self.user.save()
        destinatario = factories.DestinatarioFactory(cliente=contrato_cliente)
        estimate = Estimate.objects.create(
            project=contrato_factory,
            consecutive=1,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-15',
            finish_date='1999-08-15'
        )
        concepto = factories.ConceptoFactory(
            project=contrato_factory
        )
        factories.EstimateConceptFactory(
            estimate=estimate,
            concept=concepto
        )
        estimate2 = Estimate.objects.create(
            project=contrato_factory,
            consecutive=2,
            draft_by=self.user,
            supervised_by=self.user,
            start_date='1999-08-20',
            finish_date='1999-08-20',
        )
        estimate2.auth_by.add(destinatario.id)
        estimate2.auth_by_gen.add(destinatario.id)
        factories.ConceptoFactory(
            project=contrato_factory
        )
        factories.EstimateConceptFactory(
            estimate=estimate,
            concept=concepto
        )
        estimate.save()
        estimate2.save()
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(
            reverse('proyectos:estimate_detailpdf', kwargs={'pk': estimate2.pk}),
            {'as': 'html'}
        )
        self.assertTemplateNotUsed(response, 'proyectos/estimate_detail.html')
        self.assertTemplateUsed(response, 'proyectos/concept_estimate.html')
        self.assertTemplateNotUsed(response, 'proyectos/concept_generator.html')
        self.assertContains(response, '<!DOCTYPE html>', html=True)
