from unittest import mock
from django.test import RequestFactory, tag
from construbot.users.tests import utils
from .context import ContextManager
from .utils import BasicAutocomplete, get_directory_path
# Create your tests here.


class ContextTests(utils.BaseTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_context_includes_user_groups(self):
        with mock.patch('django.urls.reverse') as reverse_mock:
            reverse_mock.return_value = '/fake/url/'
            reverse_mock.side_effect = 'fake/url/'
            view = ContextManager()
            view.user_groups = [
                'home', 'documentos', 'pendientes', 'proyectos'
            ]
            menu = view.get_menu()
            for obj in menu:
                self.assertTrue(
                    obj['title'].lower() in view.user_groups,
                    '%s is not in user_groups' % obj['title']
                )

    def test_context_includes_menu_specific_right_place(self):
        with mock.patch('django.urls.reverse') as reverse_mock:
            reverse_mock.return_value = '/fake/url/'
            reverse_mock.side_effect = 'fake/url/'
            view = ContextManager()
            view.user_groups = [
                'users', 'documentos', 'pendientes', 'proyectos'
            ]
            menu_specific_obj = [{'title': 'fake'}, {'title': 'foo'}]
            view.menu_specific = menu_specific_obj
            view.app_label_name = 'Documentos'
            menu = view.get_menu()
            self.assertIn(menu_specific_obj[0], menu)
            self.assertEqual(menu.index(menu_specific_obj[0]), 3)


class BaseAutoCompleteTest(utils.BaseTestCase):

    def test_basic_autcomplete_returns_true_on_permissions(self):
        request = mock.Mock()
        instance = BasicAutocomplete()
        self.assertTrue(instance.has_add_permission(request))

    def test_get_key_words_returns_empty_obj(self):
        instance = BasicAutocomplete()
        with self.assertRaises(NotImplementedError):
            instance.get_key_words()

    @mock.patch.object(BasicAutocomplete, 'get_key_words')
    def test_autocomplete_get_queryset(self, mock_kw):
        mock_kw.return_value = {'mock_kw': 'bla'}
        instance = BasicAutocomplete()
        instance.request = mock.Mock()
        instance.q = 'string'
        instance.ordering = 'mock_ordering'
        instance.model = mock.Mock()
        instance.model.objects = mock.Mock()
        queryset_mock = mock.Mock()
        queryset_mock.order_by = mock.Mock()
        queryset_mock_instance = mock.Mock()
        queryset_mock.order_by.return_value = queryset_mock_instance
        filter_mock = mock.Mock()
        filter_mock.return_value = queryset_mock
        instance.model.objects.filter = filter_mock
        instance.model.objects.order_by = mock.Mock()
        qs = instance.get_queryset()
        instance.model.objects.filter.assert_called_with(**mock_kw())
        queryset_mock.order_by.assert_called_with('mock_ordering')
        self.assertEqual(qs, queryset_mock_instance)

    def test_autocomplete_on_post_returns_default_manager(self):
        instance = BasicAutocomplete()
        instance.request = mock.MagicMock()
        instance.model = mock.MagicMock()
        manager = mock.MagicMock()
        instance.model.objects = manager
        instance.q = None
        self.assertEqual(instance.get_queryset(), manager)

    def test_get_post_key_words(self):
        instance = BasicAutocomplete()
        self.assertDictEqual(instance.get_post_key_words(), {})

    @mock.patch.object(BasicAutocomplete, 'get_post_key_words')
    @mock.patch.object(BasicAutocomplete, 'get_queryset')
    def test_autocomplete_create_object(self, mock_queryset, post_kw_mock):
        instance = BasicAutocomplete()
        instance.create_field = 'hola'
        post_kw_mock.return_value = {'key': 'value'}
        manager = mock.MagicMock()
        mock_queryset.return_value = manager
        mock_create_method = mock.MagicMock()
        manager.create = mock_create_method
        instance.create_object('foo')
        self.assertEqual(instance.post_key_words, {'hola': 'foo', 'key': 'value'})
        self.assertTrue(post_kw_mock.called)
        manager.create.assert_called_with(**{'hola': 'foo', 'key': 'value'})


class DirectoyPathTest(utils.BaseTestCase):

    @mock.patch('construbot.core.utils.strftime')
    def test_get_directory_path_returns_correct_string(self, mock_strftime):
        mock_strftime.return_value = '2018-06-15-17-28-49'
        mock_instance = mock.MagicMock()
        mock_instance._meta.verbose_name_plural = 'models'
        mock_instance.cliente.company.customer.customer_name = 'customer'
        mock_instance.cliente.company.customer.id = '12'
        mock_instance.cliente.company.company_name = 'company'
        path = get_directory_path(mock_instance, 'file.txt')
        self.assertEqual(path, '12-customer/company/models/2018-06-15-17-28-49-file.txt')
