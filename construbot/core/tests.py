from django.test import RequestFactory
from construbot.users.tests import utils, factories
# Create your tests here.

class ContextTests(utils.BaseTestCase):
    def setUp(self):
        self.user_factory = factories.UserFactory
        self.user = self.make_user()
        self.factory = RequestFactory()