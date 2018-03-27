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
            ContextManager.user_groups = [
                'home', 'documentos', 'pendientes', 'proyectos'
            ]
            view = ContextManager()
            menu = view.get_menu()
            for obj in menu:
                self.assertTrue(
                    obj['title'].lower() in ContextManager.user_groups,
                    '%s is not in user_groups' % obj['title']
                )
