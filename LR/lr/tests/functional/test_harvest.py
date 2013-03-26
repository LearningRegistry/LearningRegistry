from datetime import datetime
from lr.lib.harvest import harvest
from lr.tests import *
from lr.util.decorators import ForceCouchDBIndexing, ModifiedServiceDoc, update_authz
from pylons import config
from urllib import unquote_plus,quote_plus
import logging,json
import threading
import time
import time
log = logging.getLogger(__name__)
headers={'content-type': 'application/json'}
db = None
class TestHarvestController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "obtain"
    @classmethod
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def setupClass(self):
        self.setup = True
        with open("lr/tests/data/nsdl_dc/data-000000000.json",'r') as f:
            data = json.load(f)
        if hasattr(self, "attr"):
            app = self.app
        else:
            controller =  TestHarvestController(methodName="test_empty")
            app = controller.app  
        h = harvest()
        self.db = h.db                      
        self.server = h.server
        global db
        db = self.db
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
    def test_empty(self):
        pass
    @classmethod
    def tearDownClass(self):
        for id in self.ids:
            try:
                del self.db[id]
            except:
                pass
            try:
                del self.db[id+'-distributable']
            except:
                pass
    def validate_getrecord_response_base(self, response):
        data = json.loads(response.body)   
        assert data.has_key('OK') and data['OK']
        assert data.has_key('request')
        assert data['request'].has_key('verb') and data['request']['verb'] == 'getrecord'
        assert data.has_key('getrecord')
        return data

    def validate_getrecord_response(self, response, targetId):
        data = self.validate_getrecord_response_base(response)         
        for doc in data['getrecord']['record']:
          assert doc.has_key('resource_data')
          assert doc['resource_data']['doc_ID'] == targetId

    def validate_getrecord_response_resource_id(self, response, resourceLocator):
        data = self.validate_getrecord_response_base(response)
        for doc in data['getrecord']['record']:
          assert doc.has_key('resource_data')
          assert unquote_plus(doc['resource_data']['resource_locator']) == unquote_plus(resourceLocator)

    def validate_getrecord_id_doesnot_exist(self,resp):
        doc = json.loads(resp.body)
        assert doc.has_key("OK") and not doc["OK"]
        assert doc.has_key("error") and doc['error'] == "idDoesNotExist"

    @ForceCouchDBIndexing()
    def test_getrecord_get_by_doc_id(self):
        response = self.app.get(url('harvest', id='getrecord',request_ID=self.ids[0], by_doc_ID=True))
        self.validate_getrecord_response(response,self.ids[0])
    @ForceCouchDBIndexing()
    def test_getrecord_get_by_resource_id(self):
        response = self.app.get(url('harvest', id='getrecord',request_ID=self.resourceLocators[0], by_doc_ID=False,by_resource_id=True))
        self.validate_getrecord_response_resource_id(response,self.resourceLocators[0])
    @ForceCouchDBIndexing()
    def test_getrecord_get_by_resource_id_url_quoted(self):
        testID = quote_plus(self.resourceLocators[0])
        response = self.app.get(url('harvest', id='getrecord',request_ID=testID, by_doc_ID=False,by_resource_id=True))
        self.validate_getrecord_response_resource_id(response,testID)
    @ForceCouchDBIndexing()
    def test_getrecord_post_by_resource_id(self):
        data = json.dumps({'request_ID':self.resourceLocators[0],'by_resource_ID':True,'by_doc_ID':False})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_response_resource_id(response,self.resourceLocators[0])
    @ForceCouchDBIndexing()
    def test_getrecord_post_by_doc_id(self):
        data = json.dumps({'request_ID':self.ids[0],'by_doc_ID':True})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_response(response,self.ids[0])
    @ForceCouchDBIndexing()
    def test_getrecord_get_by_doc_id_fail(self):
        response = self.app.get(url('harvest', id='getrecord',request_ID="blah", by_doc_ID=True))
        self.validate_getrecord_id_doesnot_exist(response)
    @ForceCouchDBIndexing()
    def test_getrecord_get_by_resource_id_fail(self):
        response = self.app.get(url('harvest', id='getrecord',request_ID="blah", by_doc_ID=False,by_resource_id=True))
        self.validate_getrecord_id_doesnot_exist(response)
    @ForceCouchDBIndexing()
    def test_getrecord_post_by_doc_id_fail(self):
        data = json.dumps({'request_ID':"blah",'by_resource_ID':True,'by_doc_ID':False})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_id_doesnot_exist(response)
    @ForceCouchDBIndexing()
    def test_getrecord_post_by_resource_id_fail(self):
        data = json.dumps({'request_ID':"blah",'by_doc_ID':True})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_id_doesnot_exist(response)

    def _validate_error_message(self,response):
        data = json.loads(response.body)
        assert (not data['OK'])
    def validate_listrecords_response(self, response):
        data = json.loads(response.body)
        if not data['OK']:
            print data
        assert data.has_key('OK') and data['OK']
        assert data.has_key('listrecords')
        assert len(data['listrecords']) > 0
        for doc in data['listrecords']:
          assert doc.has_key('record')
          record = doc['record']          
          assert record.has_key('resource_data')            
          resource = record['resource_data']
          nodeTimestamp = resource['node_timestamp']
          assert nodeTimestamp[:nodeTimestamp.rfind('.')] >= self.from_date[:self.from_date.rfind('.')]
          assert nodeTimestamp[:nodeTimestamp.rfind('.')] <= self.until_date[:self.until_date.rfind('.')]
    @ForceCouchDBIndexing()          
    def test_listrecords_get(self):
        self.until_date = datetime.utcnow().isoformat()+"Z"
        response = self.app.get(url('harvest', id='listrecords'),params={'from':self.from_date,'until':self.until_date})
        self.validate_listrecords_response(response)
    @ForceCouchDBIndexing()
    def test_listrecords_post(self):
        self.until_date = datetime.utcnow().isoformat()+"Z"
        data = json.dumps({'from':self.from_date,'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self.validate_listrecords_response(response)
    @ForceCouchDBIndexing()
    def test_listrecords_post_bad_from(self):
        self.until_date = datetime.utcnow().isoformat()+"Z"
        data = json.dumps({'from':"aaa",'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self._validate_error_message(response)
    @ForceCouchDBIndexing()
    def test_listrecords_post_bad_until(self):
        data = json.dumps({'from':self.from_date,'until':'self.until_date'})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self._validate_error_message(response)
        
    def validate_listidentifiers_response(self, response):
        data = json.loads(response.body)
        if not data['OK']:
            print data
        assert data.has_key('OK') and data['OK']
        assert data.has_key('listidentifiers')
        assert len(data['listidentifiers']) > 0
        for doc in data['listidentifiers']:
          assert doc.has_key('header')
          record = doc['header']          
          assert record.has_key('identifier')
    @ForceCouchDBIndexing()
    def test_listidentifiers_get(self):
        self.until_date = datetime.utcnow().isoformat()+"Z"
        response = self.app.get(url('harvest', id='listidentifiers'),params={'from':self.from_date,'until':self.until_date})
        self.validate_listidentifiers_response(response)
    @ForceCouchDBIndexing()
    def test_listidentifiers_post(self):
        self.until_date = datetime.utcnow().isoformat()+"Z"
        data = json.dumps({'from':self.from_date,'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self.validate_listidentifiers_response(response)
    @ForceCouchDBIndexing()
    def test_listidentifiers_post_bad_from(self):
        self.until_date = datetime.utcnow().isoformat()+"Z"
        data = json.dumps({'from':'self.from_date','until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self._validate_error_message(response)
    @ForceCouchDBIndexing()
    def test_listidentifiers_post_bad_until(self):
        data = json.dumps({'from':self.from_date,'until':'self.until_date'})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self._validate_error_message(response)
    @ForceCouchDBIndexing()
    def test_listidentifiers_flow_control_enabled(self):
        nodeDb = self.server[config["couchdb.db.node"]]
        serviceDoc = nodeDb[config["lr.harvest.docid"]]
        flowControlCurrent = serviceDoc['service_data']['flow_control']
        serviceDoc['service_data']['flow_control'] = True
        idLimit = None
        if serviceDoc['service_data'].has_key('id_limit'):
            idLimit = serviceDoc['service_data']['id_limit']
        serviceDoc['service_data']['id_limit'] = 100
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        response = self.app.get(url('harvest', id='listidentifiers'))
        result = json.loads(response.body)
        serviceDoc['service_data']['flow_control'] = flowControlCurrent
        if idLimit is None:
            del serviceDoc['service_data']['id_limit']
        else:
            serviceDoc['service_data']['id_limit'] = idLimit
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        assert result.has_key('resumption_token')
        assert len(result['documents']) == 100
    @ForceCouchDBIndexing()        
    def test_listidentifiers_flow_control_enabled(self):
        nodeDb = self.server[config["couchdb.db.node"]]
        serviceDoc = nodeDb[config["lr.harvest.docid"]]
        flowControlCurrent = serviceDoc['service_data']['flow_control']
        serviceDoc['service_data']['flow_control'] = False
        serviceDoc['service_data']['id_limit'] = 100
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        response = self.app.get(url('harvest', id='listidentifiers'))
        result = json.loads(response.body)
        serviceDoc['service_data']['flow_control'] = flowControlCurrent
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        assert not result.has_key('resumption_token')
    @ForceCouchDBIndexing()
    def test_listrecords_flow_control_enabled(self):
        nodeDb = self.server[config["couchdb.db.node"]]
        serviceDoc = nodeDb[config["lr.harvest.docid"]]
        flowControlCurrent = serviceDoc['service_data']['flow_control']
        serviceDoc['service_data']['flow_control'] = True
        idLimit = None
        if serviceDoc['service_data'].has_key('id_limit'):
            idLimit = serviceDoc['service_data']['id_limit']
        serviceDoc['service_data']['id_limit'] = 100
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        response = self.app.get(url('harvest', id='listrecords'))
        result = json.loads(response.body)
        serviceDoc['service_data']['flow_control'] = flowControlCurrent
        if idLimit is None:
            del serviceDoc['service_data']['id_limit']
        else:
            serviceDoc['service_data']['id_limit'] = idLimit
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        assert result.has_key('resumption_token')
        assert len(result['documents']) == 100
    @ForceCouchDBIndexing()        
    def test_listrecords_flow_control_enabled(self):
        nodeDb = self.server[config["couchdb.db.node"]]
        serviceDoc = nodeDb[config["lr.harvest.docid"]]
        flowControlCurrent = serviceDoc['service_data']['flow_control']
        serviceDoc['service_data']['flow_control'] = False
        serviceDoc['service_data']['id_limit'] = 100
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        response = self.app.get(url('harvest', id='listrecords'))
        result = json.loads(response.body)
        serviceDoc['service_data']['flow_control'] = flowControlCurrent
        nodeDb[config["lr.harvest.docid"]] = serviceDoc
        assert not result.has_key('resumption_token')

    def validate_identify_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']
        assert data.has_key('identify')
        assert data['identify'].has_key('node_id')
        assert data['identify'].has_key('repositoryName')
        assert data['identify'].has_key('baseURL')
        assert data['identify'].has_key('protocolVersion')
        assert data['identify'].has_key('service_version')
        assert data['identify'].has_key('earliestDatestamp')
        assert data['identify'].has_key('deletedRecord')
        assert data['identify'].has_key('granularity')
        assert data['identify'].has_key('adminEmail')
    @ForceCouchDBIndexing()        
    def test_identify_get(self):
        response = self.app.get(url(controller='harvest', action='identify'))
        self.validate_identify_response(response)
    @ForceCouchDBIndexing()
    def test_identify_post(self):
        response = self.app.post(url(controller='harvest',action='identify'), params={} ,headers=headers)
        self.validate_identify_response(response)


    def validate_listmetadataformats_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']
        assert data.has_key('listmetadataformats')
        metadata_formats = data['listmetadataformats']
        assert len(metadata_formats) >= 0
        for format in metadata_formats: 
          assert format.has_key('metadataformat')
          assert format['metadataformat'].has_key('metadataPrefix')
    @ForceCouchDBIndexing()
    def test_listmetadataformats_get(self):
        response = self.app.get(url('harvest', id='listmetadataformats'))
        self.validate_listmetadataformats_response(response)
    @ForceCouchDBIndexing()
    def test_listmetadataformats_post(self):
        response = self.app.post(url(controller='harvest',action='listmetadataformats'), params={} ,headers=headers)
        self.validate_listmetadataformats_response(response)


    def validate_listsets_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and not data['OK']
    @ForceCouchDBIndexing()
    def test_listsets_get(self):
        response = self.app.get(url('harvest', id='listsets'))
        self.validate_listsets_response(response)
    @ForceCouchDBIndexing()
    def test_listsets_post(self):
        response = self.app.post(url(controller='harvest',action='listsets'), params={} ,headers=headers)
        self.validate_listsets_response(response)
