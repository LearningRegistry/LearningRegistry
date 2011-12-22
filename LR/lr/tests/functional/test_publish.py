from lr.tests import *

class TestPublisherController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "publish"    
    def test_index(self):
        res = self.app.options(url(controller=self.controllerName),headers={'origin':'http://foo.bar'})
        assert res.headers['Access-Control-Allow-Origin'] == 'http://foo.bar'
        assert res.headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
        assert res.headers['Access-Control-Max-Age'] == '1728000'
        assert res.headers['Access-Control-Allow-Headers'] == 'Content-Type,Origin,Accept'
        with open("lr/tests/data/nsdl_dc/data-000000000.json",'r') as f:
        	res = self.app.publich(url(controller=self.controllerName),params=json.dump(f),headers={'origin':'http://foo.bar','Content-Type': 'application/json'})
        publishResult = json.loads(res.body)
        assert publishResult['OK']
        for result in publishResult['document_results']:
        	assert result['OK']
        
