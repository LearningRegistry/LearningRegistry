from lr.tests import *

class TestRegisterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='register', action='index'))
        # Test response...
