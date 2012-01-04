from lr.tests import *

class TestSetupController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='setup', action='index'))
        # Test response...
