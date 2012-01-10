from pylons import *
from lr.tests import *
import logging
log = logging.getLogger(__name__)

class TestStatusController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
	self.controllerName = "status"
    def test_index(self):
        response = self.app.get('/status')
        #log.info(str(response))
        assert 'node_id' in response
        assert 'node_name' in response
        assert 'active' in response
        assert 'timestamp' in response
