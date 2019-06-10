<<<<<<< HEAD
from django.core.urlresolvers import reverse
=======
from django.urls import reverse
>>>>>>> 432b8adc6f2247b6794c8149615a4b25fef180f5
from construbot.users.tests import utils


class TestProyectsURLs(utils.BaseTestCase):
    """Test URL patterns for users app."""

    def test_proyects_dashboard_reverse(self):
        self.assertEqual(reverse('proyectos:proyect_dashboard'), '/proyectos/')

    def test_contrato_list_reverse(self):
        self.assertEqual(reverse('proyectos:listado_de_contratos'), '/proyectos/listado/contratos/')

    def test_clientes_list_reverse(self):
        self.assertEqual(reverse('proyectos:listado_de_clientes'), '/proyectos/listado/clientes/')

    def test_sitios_list_reverse(self):
        self.assertEqual(reverse('proyectos:listado_de_sitios'), '/proyectos/listado/sitios/')

    def test_destinatarios_list_reverse(self):
        self.assertEqual(reverse('proyectos:listado_de_destinatarios'), '/proyectos/listado/destinatarios/')

    def test_catalogo_edit_reverse(self):
        self.assertEqual(reverse('proyectos:catalogo_conceptos', kwargs={'pk': 1}), '/proyectos/contrato/catalogo-edit/1/')

    def test_catalogo_list_reverse(self):
        self.assertEqual(reverse('proyectos:catalogo_conceptos_listado', kwargs={'pk': 1}), '/proyectos/contrato/catalogo-conceptos/1/')

    def test_contrato_detail_reverse(self):
        self.assertEqual(reverse('proyectos:contrato_detail', kwargs={'pk': 1}), '/proyectos/contrato/detalle/1/')

    def test_cliente_detail_reverse(self):
        self.assertEqual(reverse('proyectos:cliente_detail', kwargs={'pk': 1}), '/proyectos/cliente/detalle/1/')

    def test_sitio_detail_reverse(self):
        self.assertEqual(reverse('proyectos:sitio_detail', kwargs={'pk': 1}), '/proyectos/sitio/detalle/1/')

    def test_destinatario_detail_reverse(self):
        self.assertEqual(reverse('proyectos:destinatario_detail', kwargs={'pk': 1}), '/proyectos/destinatario/detalle/1/')

    def test_estimate_detail_reverse(self):
        self.assertEqual(reverse('proyectos:estimate_detail', kwargs={'pk': 1}), '/proyectos/estimacion/detalle/1/')

    def test_nuevo_contrato_reverse(self):
        self.assertEqual(reverse('proyectos:nuevo_contrato'), '/proyectos/contrato/nuevo/')

    def test_nuevo_cliente_reverse(self):
        self.assertEqual(reverse('proyectos:nuevo_cliente'), '/proyectos/cliente/nuevo/')

    def test_nuevo_sitio_reverse(self):
        self.assertEqual(reverse('proyectos:nuevo_sitio'), '/proyectos/sitio/nuevo/')

    def test_nuevo_destinatario_reverse(self):
        self.assertEqual(reverse('proyectos:nuevo_destinatario'), '/proyectos/destinatario/nuevo/')

    def test_nueva_estimacion_reverse(self):
        self.assertEqual(reverse('proyectos:nueva_estimacion', kwargs={'pk': 1}), '/proyectos/estimacion/nuevo/1/')

    def test_editar_contrato_reverse(self):
        self.assertEqual(reverse('proyectos:editar_contrato',
                                  kwargs={'pk': 1}),
                                  '/proyectos/editar/contrato/1/')

    def test_editar_cliente_reverse(self):
        self.assertEqual(reverse('proyectos:editar_cliente',
                                 kwargs={'pk': 1}),
                                 '/proyectos/editar/cliente/1/')

    def test_editar_sitio_reverse(self):
        self.assertEqual(
            reverse('proyectos:editar_sitio', kwargs={'pk': 1}),
            '/proyectos/editar/sitio/1/'
        )

    def test_editar_destinatario_reverse(self):
        self.assertEqual(reverse('proyectos:editar_destinatario',
                                 kwargs={'pk': 1}),
                                 '/proyectos/editar/destinatario/1/')

    def test_editar_estimacion_reverse(self):
        self.assertEqual(reverse('proyectos:editar_estimacion',
                                 kwargs={'pk': 1}),
                                 '/proyectos/editar/estimacion/1/')

    def test_delete_models_reverse(self):
        self.assertEqual(reverse('proyectos:eliminar', kwargs={'model': 'contrato', 'pk': 1}),
                         '/proyectos/eliminar/contrato/1/')

    def test_cliente_autocomplete_reverse(self):
        self.assertEqual(reverse('proyectos:cliente-autocomplete'), '/proyectos/cliente-autocomplete/')

    def test_sitio_autocomplete_reverse(self):
        self.assertEqual(reverse('proyectos:sitio-autocomplete'), '/proyectos/sitio-autocomplete/')

    def test_destinatario_autocomplete_reverse(self):
        self.assertEqual(reverse('proyectos:destinatario-autocomplete'), '/proyectos/destinatario-autocomplete/')

    def test_unit_autocomplete_reverse(self):
        self.assertEqual(reverse('proyectos:unit-autocomplete'), '/proyectos/unit-autocomplete/')
