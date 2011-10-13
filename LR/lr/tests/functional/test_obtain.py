from lr.tests import *
import json
import urllib
import logging
from lr.lib.harvest import harvest
from webtest import AppError
log = logging.getLogger(__name__)
headers={'Content-Type': 'application/json'}
class TestObtainController(TestController):
    @classmethod
    def setupClass(self):
        self.setup = True
        with open("lr/tests/data/nsdl_dc/data-000000000.json",'r') as f:
            data = json.load(f)
        if hasattr(self, "attr"):
            app = self.app
        else:
            controller =  TestObtainController(methodName="test_empty")
            app = controller.app  
        h = harvest()
        self.db = h.db              
        result = app.post('/publish', params=json.dumps(data), headers=headers)
        len(self.db.view('_design/learningregistry-resources/_view/docs'))
        len(self.db.view('_design/learningregistry-resource-location/_view/docs'))
        result = json.loads(result.body)
        self.ids = map(lambda doc: doc['doc_ID'],result['document_results'])
        self.resourceLocators = map(lambda doc: doc['resource_locator'],data['documents'])
    @classmethod
    def tearDownClass(self):
        for id in self.ids:
            del self.db[id]
            del self.db[id+'-distributable']
    def _getInitialPostData(self):
        data = {
            "by_doc_ID":False,
            "by_resource_ID":True,
            "ids_only":False
        }
        return data
    def _validateResponse(self,resp,requestData):
        data = json.loads(resp.body)
        requestData = json.loads(requestData)
        assert(data['documents'])
        assert(len(data['documents'])>0)
        if requestData.has_key('by_doc_ID') and requestData['by_doc_ID']:
            for d in self.ids:
                print d            
        for d in data['documents']:
            print "Target Doc %s" %d['doc_ID']
            if requestData.has_key('by_doc_ID') and requestData['by_doc_ID']:
                assert d['doc_ID'] in self.ids 
            else:
                assert d['doc_ID'] in self.resourceLocators
        return data
    def _validateError(self,error):
        data = json.loads(error)
        assert(data["OK"] == False)
    def test_create(self):        
        params = self._getInitialPostData()
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params)
        # Test response...
    def test_create_ids_only(self):
        params = self._getInitialPostData()
        params['ids_only'] = True
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params)
    def test_create_by_doc_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params)
    def test_create_by_resource_id(self):
        params = self._getInitialPostData()
        del params['by_doc_ID']
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params)        
    def test_create_by_doc_id_and_by_resource_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params['request_IDs'] = self.ids
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params)
    def test_create_by_doc_id_and_by_resource_id_fail(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = True
        params['request_IDs'] = self.resourceLocators
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params)
    def test_create_by_doc_id_and_by_resource_id_both_true(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = True
        params['request_IDs'] = self.ids[0:1]
        params = json.dumps(params)
        try:
            response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        except AppError as ex:
            self._validateError(ex.message[ex.message.rfind('{'):])
            pass#expected error
    def test_create_by_doc_id_and_by_resource_id_fail_both_false(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = False
        params['request_IDs'] = self.resourceLocators[0:1]
        params = json.dumps(params)
        try:
            response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        except AppError as ex:
            self._validateError(ex.message[ex.message.rfind('{'):])
            pass#expected error        
    def test_empty(self):
            pass