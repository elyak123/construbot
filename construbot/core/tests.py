from unittest import mock
from django.test import RequestFactory
from construbot.users.tests import utils
from .context import ContextManager
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
