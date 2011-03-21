from lr.tests import *
import logging
log = logging.getLogger(__name__)
class TestSword2Controller(TestController):

    def test_index(self):
        response = self.app.get(url(controller='sword', action='index'))
        # Test response...
    def test_create(self):
        response = self.app.post(url(controller='sword', action='create'),headers={'content-type': 'application/json', 'user-agent':'python' })        
