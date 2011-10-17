from lr.tests import *
import logging,json
import time
from datetime import datetime
from lr.lib.harvest import harvest
log = logging.getLogger(__name__)
headers={'content-type': 'application/json'}
db = None
def updateViews():
    len(db.view('_design/learningregistry-resources/_view/docs'))
    len(db.view('_design/learningregistry-resource-location/_view/docs'))
    len(db.view('_design/learningregistry-by-date/_view/docs'))        
class TestHarvestController(TestController):
    @classmethod
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
        global db
        db = self.db
        result = app.post('/publish', params=json.dumps(data), headers=headers)        
        result = json.loads(result.body)
        self.ids = map(lambda doc: doc['doc_ID'],result['document_results'])
        self.resourceLocators = map(lambda doc: doc['resource_locator'],data['documents'])
        done = False
        distributableIds = map(lambda id: id+'-distributable',self.ids)
        while not done:      
            view = self.db.view('_all_docs',keys=distributableIds)                
            done = len(distributableIds) == len(view.rows)
            time.sleep(0.5)        
        updateViews()
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
        updateViews()
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
          assert doc['resource_data']['_id'] == targetId

    def validate_getrecord_response_resource_id(self, response, resourceLocator):
        data = self.validate_getrecord_response_base(response)
        for doc in data['getrecord']['record']:
          assert doc.has_key('resource_data')
          assert doc['resource_data']['resource_locator'] == resourceLocator

    def test_getrecord_get_by_doc_id(self):
        response = self.app.get(url('harvest', id='getrecord',request_ID=self.ids[0], by_doc_ID=True))
        self.validate_getrecord_response(response,self.ids[0])

    def test_getrecord_get_by_resource_id(self):
        response = self.app.get(url('harvest', id='getrecord',request_ID=self.resourceLocators[0], by_doc_ID=False,by_resource_id=True))
        self.validate_getrecord_response_resource_id(response,self.resourceLocators[0])

    def test_getrecord_post(self):
        data = json.dumps({'request_ID':self.ids[0],'by_doc_ID':True})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_response(response,self.ids[0])

    def _validate_error_message(self,response):
        data = json.loads(response.body)
        assert (not data['OK'])
    def validate_listrecords_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']
        assert data.has_key('listrecords')
        assert len(data['listrecords']) > 0
        for doc in data['listrecords']:
          assert doc.has_key('record')
          record = doc['record']          
          assert record.has_key('resource_data')            
          resource = record['resource_data']
          nodeTimestamp = resource['node_timestamp']
          print nodeTimestamp
          print self.until_date
          assert nodeTimestamp >= self.from_date
          assert nodeTimestamp <= self.until_date

    def test_listrecords_get(self):
        response = self.app.get(url('harvest', id='listrecords'),params={'from':self.from_date,'until':self.until_date})
        self.validate_listrecords_response(response)

    def test_listrecords_post(self):
        data = json.dumps({'from':self.from_date,'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self.validate_listrecords_response(response)

    def test_listrecords_post_bad_from(self):
        data = json.dumps({'from':"aaa",'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self._validate_error_message(response)

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

    def test_listidentifiers_get(self):
        response = self.app.get(url('harvest', id='listidentifiers'),params={'from':self.from_date,'until':self.until_date})
        self.validate_listidentifiers_response(response)

    def test_listidentifiers_post(self):
        data = json.dumps({'from':self.from_date,'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self.validate_listidentifiers_response(response)

    def test_listidentifiers_post_bad_from(self):
        data = json.dumps({'from':'self.from_date','until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self._validate_error_message(response)

    def test_listidentifiers_post_bad_until(self):
        data = json.dumps({'from':self.from_date,'until':'self.until_date'})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self._validate_error_message(response)


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
        
    def test_identify_get(self):
        response = self.app.get(url(controller='harvest', action='identify'))
        self.validate_identify_response(response)

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

    def test_listmetadataformats_get(self):
        response = self.app.get(url('harvest', id='listmetadataformats'))
        self.validate_listmetadataformats_response(response)

    def test_listmetadataformats_post(self):
        response = self.app.post(url(controller='harvest',action='listmetadataformats'), params={} ,headers=headers)
        self.validate_listmetadataformats_response(response)


    def validate_listsets_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and not data['OK']

    def test_listsets_get(self):
        response = self.app.get(url('harvest', id='listsets'))
        self.validate_listsets_response(response)

    def test_listsets_post(self):
        response = self.app.post(url(controller='harvest',action='listsets'), params={} ,headers=headers)
        self.validate_listsets_response(response)
