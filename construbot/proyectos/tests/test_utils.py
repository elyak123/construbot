from unittest import mock
from django.test import tag
from test_plus.test import CBVTestCase
from construbot.proyectos import utils


class EstimacionesPendientesdePago(CBVTestCase):

    @mock.patch('construbot.proyectos.utils.Estimate.objects.select_related')
    @mock.patch('construbot.proyectos.utils.Estimate.objects.filter')
    def test_estimaciones_pendients_pago_returns_qs_on_perms(self, mock_filter, mock_select_related):
        mock_qs = mock.Mock()
        mock_qs.filter = mock_filter
        mock_select_related.return_value = mock_qs
        mock_company = mock.Mock()
        mock_user = mock.Mock()
        utils.estimacionespendientes_pago(mock_company, True, mock_user)
        mock_filter.assert_called_once_with(
            project__contraparte__company=mock_company, invoiced=True, paid=False, project__depth=1
        )


class EstimacionesPendientesFacturacion(CBVTestCase):
    @tag('current')
    @mock.patch('construbot.proyectos.utils.Estimate.objects.select_related')
    @mock.patch('construbot.proyectos.utils.Estimate.objects.filter')
    def test_estimaciones_pendients_facturacion_returns_qs_on_perms(self, mock_filter, mock_select_related):
        mock_qs = mock.Mock()
        mock_qs.filter = mock_filter
        mock_select_related.return_value = mock_qs
        mock_company = mock.Mock()
        mock_user = mock.Mock()
        utils.estimacionespendientes_facturacion(mock_company, True, mock_user)
        mock_filter.assert_called_once_with(
            project__contraparte__company=mock_company, invoiced=False, project__depth=1
        )
