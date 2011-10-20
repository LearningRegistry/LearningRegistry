from lr.tests import *
import json
import urllib
import logging
from lr.lib.harvest import harvest
import lr.lib.helpers as h
from webtest import AppError
import time
from pylons import config
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
        self.server = h.server
        result = app.post('/publish', params=json.dumps(data), headers=headers)                
        result = json.loads(result.body)
        self.ids = []
        self.ids.extend(map(lambda doc: doc['doc_ID'],result['document_results']))
        result = app.post('/publish', params=json.dumps(data), headers=headers)                
        result = json.loads(result.body)
        self.ids.extend(map(lambda doc: doc['doc_ID'],result['document_results']))
        self.resourceLocators = map(lambda doc: doc['resource_locator'],data['documents'])
        done = False
        distributableIds = map(lambda id: id+'-distributable',self.ids)
        while not done:      
            view = self.db.view('_all_docs',keys=distributableIds)                
            done = len(distributableIds) == len(view.rows)
            time.sleep(0.5)
        len(self.db.view('_design/learningregistry-resources/_view/docs'))
        len(self.db.view('_design/learningregistry-resource-location/_view/docs'))
    @classmethod
    def tearDownClass(self):
        for doc in self.ids:
            try:
                self.db.delete(self.db[doc])
            except:
                pass
            try:
                self.db.delete(self.db[doc+'-distributable'])
            except:
                pass
        self.db.commit()
                
    def _getInitialPostData(self):
        data = {
            "by_doc_ID":False,
            "by_resource_ID":True,
            "ids_only":False
        }
        return data
    def _validateResponse(self,resp,requestData,testids):
        data = json.loads(resp.body)
        requestData = json.loads(requestData)
        assert(data['documents'])
        assert(len(data['documents'])>0) 
        for d in data['documents']:
            assert d['doc_ID'] in testids
        return data
    def _validateError(self,error):
        data = json.loads(error)
        assert(data["OK"] == False)
    def test_create(self):        
        params = self._getInitialPostData()
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,map(lambda doc: doc['key'],self.db.view('_design/learningregistry-resource-location/_view/docs').rows))
        # Test response...
    def test_create_ids_only(self):
        params = self._getInitialPostData()
        params['ids_only'] = True
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,map(lambda doc: doc['key'],self.db.view('_design/learningregistry-resource-location/_view/docs').rows))

    def test_flow_control_enabled(self):
        nodeDb = self.server[config["couchdb.db.node"]]
        serviceDoc = nodeDb[config["lr.obtain.docid"]]
        flowControlCurrent = serviceDoc['service_data']['flow_control']
        serviceDoc['service_data']['flow_control'] = True
        idLimit = None
        if serviceDoc['service_data'].has_key('id_limit'):
            idLimit = serviceDoc['service_data']['id_limit']
        serviceDoc['service_data']['id_limit'] = 100
        nodeDb[config["lr.obtain.docid"]] = serviceDoc
        params = self._getInitialPostData()        
        params['ids_only'] = True
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        result = json.loads(response.body)
        serviceDoc['service_data']['flow_control'] = flowControlCurrent
        if idLimit is None:
            del serviceDoc['service_data']['id_limit']
        else:
            serviceDoc['service_data']['id_limit'] = idLimit
        nodeDb[config["lr.obtain.docid"]] = serviceDoc
        assert result.has_key('resumption_token')
        assert len(result['documents']) == 100
    def test_flow_control_disabled(self):
        nodeDb = self.server[config["couchdb.db.node"]]
        serviceDoc = nodeDb[config["lr.obtain.docid"]]
        flowControlCurrent = serviceDoc['service_data']['flow_control']
        serviceDoc['service_data']['flow_control'] = False
        serviceDoc['service_data']['id_limit'] = 100
        nodeDb[config["lr.obtain.docid"]] = serviceDoc
        params = self._getInitialPostData()        
        params['ids_only'] = True
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        result = json.loads(response.body)
        serviceDoc['service_data']['flow_control'] = flowControlCurrent
        nodeDb[config["lr.obtain.docid"]] = serviceDoc
        assert not result.has_key('resumption_token')
    def test_create_by_doc_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,self.db)
    def test_create_by_resource_id(self):
        params = self._getInitialPostData()
        del params['by_doc_ID']
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,map(lambda doc: doc['key'],self.db.view('_design/learningregistry-resource-location/_view/docs').rows))
    def test_create_by_doc_id_and_by_resource_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params['request_IDs'] = self.ids
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,self.db)
    def test_create_by_doc_id_and_by_resource_id_fail(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = True
        params['request_IDs'] = self.resourceLocators
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,self.resourceLocators)
    def test_create_by_doc_id_subset_of_ids(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params['ids_only'] = True
        params['request_IDs'] = self.ids[0:2]
        print params
        params = json.dumps(params)        
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,self.ids[0:2])
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