from lr.lib.harvest import harvest
from lr.lib.schema_helper import TombstoneValidator, ResourceDataModelValidator
from lr.tests import *
from lr.util.decorators import ForceCouchDBIndexing, PublishTestDocs, SetFlowControl, ModifiedServiceDoc, update_authz, make_gpg_keys
from lr.util.testdata import getTestDataForReplacement, getTestDataForMultipleResourceLocator
from pylons import config
from webtest import AppError
import couchdb
import json
import logging
import lr.lib.helpers as h
import time
import urllib
log = logging.getLogger(__name__)
headers={'Content-Type': 'application/json'}

def checkTombstone(doc):
    TombstoneValidator.validate_model(doc)

def checkResourceData(doc):
    ResourceDataModelValidator.validate_model(doc)

class TestObtainControllerWithMultipleResourceLocator(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.db =  self.server[config['couchdb.db.resourcedata']] 

    def _getInitialPostData(self):
        data = {
            "by_doc_ID":False,
            "ids_only":False
        }
        return data

    def _validateResponse(self,resp,requestData,testids,special=None):
        data = json.loads(resp.body)
        requestData = json.loads(requestData)
        assert 'documents' in data
        assert len(data['documents'])>0, json.dumps(data['documents'])
        byDocId = requestData.has_key('by_doc_ID') and requestData['by_doc_ID']
        # import pdb; pdb.set_trace()
        for d in data['documents']:
            if byDocId:
                assert d['doc_ID'] in testids
            else:
                testids = [urllib.unquote_plus(x) for x in testids]
                assert urllib.unquote_plus(d['doc_ID']) in testids
            if not requestData.has_key('ids_only') or (requestData.has_key('ids_only') and not requestData['ids_only']):
                for doc in d['document']:
                    if requestData.has_key('by_doc_ID') and requestData['by_doc_ID']:
                        assert doc['doc_ID'] == d['doc_ID']
                    elif isinstance(doc['resource_locator'], basestring):
                        assert urllib.unquote_plus(doc['resource_locator']) == urllib.unquote_plus(d['doc_ID'])

                    if special is not None:
                        special(doc)

    @make_gpg_keys(1)
    @PublishTestDocs(getTestDataForMultipleResourceLocator(3), "OB-Delete")
    def test_multiple_locators(self, *args, **kwargs):
        '''test_multiple_locators: 1 doc is published with multiple resource_locator's, check that we can harvest by each locator.'''

        data = kwargs["test_data_sorted"]
        test_ids = kwargs["test_data_ids"]
        assert len(data) == len(test_ids) and len(data) == 1, "Not all envelopes got published!"

        test_rd3 = data[0]
        assert len(test_rd3["resource_locator"]) == 3, "Not enough resource_locator's"

        def checkDocID(doc):
            assert doc['doc_ID'] == test_rd3['doc_ID'], "unexpected doc_ID: {0} expected: {1}".format(doc['doc_ID'], test_rd3['doc_ID'])

            checkResourceData(doc)


        for uri in test_rd3["resource_locator"]:
            #check if first doc exists as a tombstone.
            params = self._getInitialPostData()
            params['request_id'] = uri
            response = self.app.get(url(controller='obtain', **params))
            self._validateResponse(response, json.dumps(params), test_rd3["resource_locator"], checkDocID)




class TestObtainControllerWithReplacments(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.db =  self.server[config['couchdb.db.resourcedata']] 

    def _getInitialPostData(self):
        data = {
            "by_doc_ID":True,
            "ids_only":False
        }
        return data

    def _validateResponse(self,resp,requestData,testids,special=None):
        data = json.loads(resp.body)
        requestData = json.loads(requestData)
        assert 'documents' in data
        assert len(data['documents'])>0, json.dumps(data['documents'])
        byDocId = requestData.has_key('by_doc_ID') and requestData['by_doc_ID']
        for d in data['documents']:
            if byDocId:
                assert d['doc_ID'] in testids
            else:
                testids = [urllib.unquote_plus(x) for x in testids]
                assert urllib.unquote_plus(d['doc_ID']) in testids
            if not requestData.has_key('ids_only') or (requestData.has_key('ids_only') and not requestData['ids_only']):
                for doc in d['document']:
                    if requestData.has_key('by_doc_ID') and requestData['by_doc_ID']:
                        assert doc['doc_ID'] == d['doc_ID']
                    else:
                        assert urllib.unquote_plus(doc['resource_locator']) == urllib.unquote_plus(d['doc_ID'])
                    if special is not None:
                        special(doc)

    @make_gpg_keys(1)
    @PublishTestDocs(getTestDataForReplacement(2, True), "OB-Delete")
    def test_obtain_delete(self, *args, **kwargs):
        '''test_obtain_delete: checks to see that replaced document's tombstone is retrievable and the
        replacement resource_data signaling a delete is also obtainable by api'''

        data = kwargs["test_data_sorted"]
        test_ids = kwargs["test_data_ids"]
        assert len(data) == len(test_ids) and len(data) == 2, "Not all envelopes got published!"


        #check if first doc exists as a tombstone.
        params = self._getInitialPostData()
        params['request_id'] = test_ids[0]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response, json.dumps(params), test_ids, checkTombstone)

        #check for deleted document.
        params = self._getInitialPostData()
        params['request_id'] = test_ids[1]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response, json.dumps(params), test_ids, checkResourceData)



    @make_gpg_keys(1)
    @PublishTestDocs(getTestDataForReplacement(2, False), "OB-Replacement")
    def test_obtain_replacement(self, *args, **kwargs):
        '''test_obtain_replacement: checks to see that replaced document's tombstone is retrievable and the
        replacement resource_data is obtainable by api'''
        
        data = kwargs["test_data_sorted"]
        test_ids = kwargs["test_data_ids"]
        assert len(data) == len(test_ids) and len(data) == 2, "Not all envelopes got published!"


        #check if first doc exists as a tombstone.
        params = self._getInitialPostData()
        params['request_id'] = test_ids[0]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response, json.dumps(params), test_ids, checkTombstone)

        #check for replacement document.
        params = self._getInitialPostData()
        params['request_id'] = test_ids[1]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response, json.dumps(params), test_ids, checkResourceData)



class TestObtainController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "obtain"   

    @classmethod
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def setupClass(cls):
        cls.setup = True

        with open("lr/tests/data/nsdl_dc/data-000000000.json",'r') as f:
            data = json.load(f)
        if hasattr(cls, "attr"):
            app = cls.app
        else:
            controller =  TestObtainController(methodName="test_empty")
            app = controller.app  
                    
        cls.server = couchdb.Server(config['couchdb.url.dbadmin'])
        cls.db =  cls.server[config['couchdb.db.resourcedata']] 

        view = cls.db.view("_all_docs")
        for row in view.rows:
            if not row.id.startswith("_design/"):
                del cls.db[row.id]

        result = app.post('/publish', params=json.dumps(data), headers=headers)                
        result = json.loads(result.body)
        cls.ids = []
        cls.ids.extend(map(lambda doc: doc['doc_ID'],result['document_results']))
        result = app.post('/publish', params=json.dumps(data), headers=headers)                
        result = json.loads(result.body)
        cls.ids.extend(map(lambda doc: doc['doc_ID'],result['document_results']))
        cls.resourceLocators = map(lambda doc: doc['resource_locator'],data['documents'])
        done = False
        distributableIds = map(lambda id: id+'-distributable',cls.ids)
        while not done:      
            view = cls.db.view('_all_docs',keys=distributableIds)                
            done = len(distributableIds) == len(view.rows)
            time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        for doc in cls.ids:
            try:
                cls.db.delete(cls.db[doc])
            except:
                pass
            try:
                cls.db.delete(cls.db[doc+'-distributable'])
            except:
                pass
        cls.db.commit()
                
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
        assert 'documents' in data
        assert len(data['documents'])>0, json.dumps(data['documents'])
        byDocId = requestData.has_key('by_doc_ID') and requestData['by_doc_ID']
        for d in data['documents']:
            if byDocId:
                assert d['doc_ID'] in testids
            else:
                testids = [urllib.unquote_plus(x) for x in testids]
                assert urllib.unquote_plus(d['doc_ID']) in testids
            if not requestData.has_key('ids_only') or (requestData.has_key('ids_only') and not requestData['ids_only']):
                for doc in d['document']:
                    if requestData.has_key('by_doc_ID') and requestData['by_doc_ID']:
                        assert doc['doc_ID'] == d['doc_ID']
                    else:
                        assert urllib.unquote_plus(doc['resource_locator']) == urllib.unquote_plus(d['doc_ID'])
        return data
    def _validateError(self,error):
        data = json.loads(error)
        assert(data["OK"] == False)
    @ForceCouchDBIndexing()        
    def test_create(self):        
        params = self._getInitialPostData()
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,map(lambda doc: doc['key'],TestObtainController.db.view('_design/learningregistry-resource-location/_view/docs').rows))
        # Test response...
    @ForceCouchDBIndexing()        
    def test_create_ids_only(self):
        params = self._getInitialPostData()
        params['ids_only'] = True
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,map(lambda doc: doc['key'],TestObtainController.db.view('_design/learningregistry-resource-location/_view/docs').rows))
    @SetFlowControl(True,config["lr.obtain.docid"])
    @ForceCouchDBIndexing()                
    def test_flow_control_enabled(self):
        params = self._getInitialPostData()        
        params['ids_only'] = True
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        result = json.loads(response.body)
        assert result.has_key('resumption_token')
        assert len(result['documents']) == 100    
    @SetFlowControl(False,config["lr.obtain.docid"])    
    @ForceCouchDBIndexing()    
    def test_flow_control_disabled(self):
        params = self._getInitialPostData()        
        params['ids_only'] = True
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        result = json.loads(response.body)
        assert not result.has_key('resumption_token')
    @ForceCouchDBIndexing()        
    def test_create_by_doc_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,TestObtainController.db)
    @ForceCouchDBIndexing()        
    def test_create_by_resource_id(self):
        params = self._getInitialPostData()
        del params['by_doc_ID']
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,map(lambda doc: doc['key'],TestObtainController.db.view('_design/learningregistry-resource-location/_view/docs').rows))
    @ForceCouchDBIndexing()        
    def test_create_by_doc_id_and_by_resource_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params['request_IDs'] = self.ids
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,TestObtainController.db)
    @ForceCouchDBIndexing()        
    def test_create_by_doc_id_and_by_resource_id_fail(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = True
        params['request_IDs'] = self.resourceLocators
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,TestObtainController.resourceLocators)
    @ForceCouchDBIndexing()        
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
    @ForceCouchDBIndexing()        
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

    @ForceCouchDBIndexing()            
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
    @ForceCouchDBIndexing()
    def test_create_by_doc_id_and_by_resource_id_empty(self):
        params = self._getInitialPostData()
        del params['by_doc_ID']
        del params['by_resource_ID']
        params['request_IDs'] = TestObtainController.resourceLocators
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response,params,TestObtainController.resourceLocators)        
    @ForceCouchDBIndexing()        
    def test_request_id_with_uri_escaped_characters(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = True
        testId = urllib.quote_plus(TestObtainController.resourceLocators[0])
        params['request_ID'] = testId
        response = self.app.get(url(controller='obtain',**params))
        self._validateResponse(response,json.dumps(params),[testId])        
    @ForceCouchDBIndexing()
    def test_request_ID_doc_get(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        del params['by_resource_ID']
        params['request_ID'] = TestObtainController.ids[0]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response,json.dumps(params),[TestObtainController.ids[0]])
    @ForceCouchDBIndexing()
    def test_request_id_doc_get(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        del params['by_resource_ID']
        params['request_id'] = TestObtainController.ids[0]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response,json.dumps(params),[TestObtainController.ids[0]])
    @ForceCouchDBIndexing()        
    def test_request_ID_resource_get(self):
        params = self._getInitialPostData()
        params['request_ID'] = TestObtainController.resourceLocators[0]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response,json.dumps(params),[TestObtainController.resourceLocators[0]])
    @ForceCouchDBIndexing()
    def test_request_ID_resource_get(self):
        params = self._getInitialPostData()
        params['request_id'] = TestObtainController.resourceLocators[0]
        response = self.app.get(url(controller='obtain', **params))
        self._validateResponse(response,json.dumps(params),[TestObtainController.resourceLocators[0]])
    @SetFlowControl(True, config["lr.obtain.docid"])
    @ForceCouchDBIndexing()
    def test_request_ID_resource_and_token_get(self):
        params = self._getInitialPostData()
        params['request_id'] = TestObtainController.resourceLocators[0]
        firstResponse = json.loads(self.app.get(url(controller='obtain', **params)).body)
        params['resumption_token'] = firstResponse['resumption_token']
        response = json.loads(self.app.get(url(controller='obtain',**params), status=500).body)
        assert response["OK"] == False    
    @SetFlowControl(True, config["lr.obtain.docid"])
    @ForceCouchDBIndexing()     
    def test_request_ID_resource_and_token_get_complete(self):
        params = self._getInitialPostData()
        testKey = TestObtainController.resourceLocators[0]
        params['request_id'] = testKey        
        while True:
            path = url(controller='obtain', **params)
            response = self.app.get(path)
            data = json.loads(response.body)        
            self._validateResponse(response,json.dumps(params),[testKey])
            if "resumption_token" not in data or data['resumption_token'] is None:
                break
            params = {'resumption_token':data['resumption_token']} 
    @SetFlowControl(True, config["lr.obtain.docid"],doc_limit=37,id_limit=37)
    @ForceCouchDBIndexing()
    def test_request_ID_resource_and_token_get_complete_no_key(self):
        params = self._getInitialPostData()   
        while True:
            path = url(controller='obtain', **params)
            response = self.app.get(path)
            data = json.loads(response.body)        
            self._validateResponse(response,json.dumps(params),TestObtainController.resourceLocators)
            if "resumption_token" not in data or data['resumption_token'] is None:
                break
            params = {'resumption_token':data['resumption_token']}             
    @ForceCouchDBIndexing()        
    def test_get_fail_both_false(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = False
        params['request_ID'] = TestObtainController.resourceLocators[0:1]
        try:
            response = self.app.get(url(controller='obtain',**params),headers=headers)
        except AppError as ex:
            self._validateError(ex.message[ex.message.rfind('{'):])      
    @ForceCouchDBIndexing()        
    def test_obtain_empty_resource_locator(self):
        import uuid
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = True
        for id in TestObtainController.ids:
            doc = TestObtainController.db[id]
            del doc['_id'] 
            del doc['_rev'] 
            doc['resource_locator'] = ""
            doc['doc_ID'] = uuid.uuid1().hex   
            TestObtainController.db.save(doc)
        results = TestObtainController.db.view('_design/learningregistry-resource-location/_view/docs')                    
        response = self.app.get(url(controller='obtain',**params),headers=headers)             
        resourceLocators = [row.key for row in results]
        self._validateResponse(response,json.dumps(params),resourceLocators)
        items_to_delete = (r for r in results if r.key == "")
        for i in items_to_delete:
            del self.db[i.id]
    @ForceCouchDBIndexing()
    def test_get_fail_both_true(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = True
        params['request_ID'] = TestObtainController.resourceLocators[0:1]
        try:
            response = self.app.get(url(controller='obtain',**params),headers=headers)
        except AppError as ex:
            self._validateError(ex.message[ex.message.rfind('{'):])                    
    @ForceCouchDBIndexing()
    def test_bad_doc_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params['request_ID'] = 'xxxx'
        response = self.app.get(url(controller='obtain',**params),headers=headers)
    def test_empty(self):
            pass