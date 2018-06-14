from unittest import mock
from django.test import RequestFactory, tag
from construbot.users.tests import utils
from .context import ContextManager
from .utils import BasicAutocomplete
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
            self.assertEqual(menu.index(menu_specific_obj[0]), 2)


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
    def test_(self, mock_kw):
        mock_kw.return_value = {'mock_kw': 'bla'}
        instance = BasicAutocomplete()
        instance.request = mock.Mock()
        instance.q = 'string'
        instance.ordering = 'mock_ordering'
        instance.model = mock.Mock()
        instance.model.objects = mock.Mock()
        queryset_mock = mock.Mock()
        queryset_mock.order_by = mock.Mock()
        filter_mock = mock.Mock()
        filter_mock.return_value = queryset_mock
        instance.model.objects.filter = filter_mock
        instance.model.objects.order_by = mock.Mock()
        qs = instance.get_queryset()
        instance.model.objects.filter.assert_called_with(**mock_kw())
        queryset_mock.order_by.assert_called_with('mock_ordering')

