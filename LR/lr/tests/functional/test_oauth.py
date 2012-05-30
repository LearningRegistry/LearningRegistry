from lr.tests import *

class TestOauthController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='oauth', action='index'))
        # Test response...
