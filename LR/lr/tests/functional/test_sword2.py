from lr.tests import *

class TestSword2Controller(TestController):

    def test_index(self):
        response = self.app.get(url(controller='sword2', action='index'))
        # Test response...
