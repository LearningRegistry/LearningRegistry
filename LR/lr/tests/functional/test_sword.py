from lr.tests import *
import logging, json
log = logging.getLogger(__name__)
class TestSwordController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='sword', action='index'),headers={'content-type': 'application/json', 'user-agent':'python','X-On-Behalf-Of':'wegrata','X-Verbose':'False' })
        # Test response...
    def test_create(self):
        with open('/home/wegrata/LearningRegistry/LR/lr/tests/2011-02-28Metadata1.json','r') as f:
            data = f.read() 
        response = self.app.post(url(controller='sword', action='create'), params=data, headers={'content-type': 'application/json', 'user-agent':'python','X-On-Behalf-Of':'wegrata','X-Verbose':'False' })        
