from lr.tests import *
from lr.util import decorators
from pylons import config
import codecs
import logging, json

log = logging.getLogger(__name__)
file_path = 'lr/tests/data/paradata-0.json'

class TestSwordController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "swordservice"    
        
    def test_index(self):
        response = self.app.get(url(controller='swordservice', action='index'),headers={'content-type': 'application/json', 'user-agent':'python','X-On-Behalf-Of':'wegrata','X-Verbose':'False' })
        # Test response...

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.sword.docid'], decorators.update_authz())
    def test_create(self):
        with codecs.open(file_path,'r','utf-8-sig') as f:
            pub_data = json.load(f)
        response = self.app.post(url(controller='swordservice', action='create'), params=json.dumps(pub_data), headers={'Content-Type': 'application/json', 'user-agent':'python','X-On-Behalf-Of':'wegrata','X-Verbose':'False' })    
