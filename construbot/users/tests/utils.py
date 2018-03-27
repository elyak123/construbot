from test_plus.test import CBVTestCase


class BaseTestCase(CBVTestCase):
    def get_request(self, user, url='bla/bla'):
        request = self.factory.get(url)
        request.user = user
        return request
