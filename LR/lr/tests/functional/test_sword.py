from lr.tests import *
import logging, json
log = logging.getLogger(__name__)
file_path = '../data/oai_dc/data-0.json'
class TestSwordController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='sword', action='index'),headers={'content-type': 'application/json', 'user-agent':'python','X-On-Behalf-Of':'wegrata','X-Verbose':'False' })
        # Test response...
    def test_create(self):
        with open(file_path,'r') as f:
            data = json.loads(f.read()) 
        for doc in data['resource_data']:
            pub_data = json.dumps(doc)
            response = self.app.post(url(controller='sword', action='create'), params=pub_data, headers={'content-type': 'application/json', 'user-agent':'python','X-On-Behalf-Of':'wegrata','X-Verbose':'False' })    
