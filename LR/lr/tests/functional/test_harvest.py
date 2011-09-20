from lr.tests import *
import logging,json
log = logging.getLogger(__name__)
headers={'content-type': 'application/json'}
test_location = 'http://www.scholaris.pl/cms/index.php/resources/8640.html'
test_id ='f4821dde0f154c439468d18f0ff845b9'
class TestHarvestController(TestController):

    def validate_getrecord_response_base(self, response):
        data = json.loads(response.body)   
        assert data.has_key('OK') and data['OK']
        assert data.has_key('request')
        assert data['request'].has_key('verb') and data['request']['verb'] == 'getrecord'
        assert data.has_key('getrecord')
        return data

    def validate_getrecord_response(self, response):
        data = self.validate_getrecord_response_base(response)         
        for doc in data['getrecord']['record']:
          assert doc.has_key('resource_data')
          assert doc['resource_data']['_id'] == test_id

    def validate_getrecord_response_resource_id(self, response):
        data = self.validate_getrecord_response_base(response)
        for doc in data['getrecord']['record']:
          assert doc.has_key('resource_data')
          assert doc['resource_data']['resource_locator'] == test_location

    def test_getrecord_get_by_doc_id(self):
        response = self.app.get(url('harvest', id='getrecord',request_id=test_id, by_doc_ID=True))
        self.validate_getrecord_response(response)

    def test_getrecord_get_by_resource_id(self):
        response = self.app.get(url('harvest', id='getrecord',request_id=test_location, by_doc_ID=False,by_resource_id=True))
        self.validate_getrecord_response_resource_id(response)

    def test_getrecord_post(self):
        data = json.dumps({'request_id':test_id,'by_doc_ID':True})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_response(response)


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
          assert resource['node_timestamp'] >= self.from_date
          assert resource['node_timestamp'] <= self.until_date

    def test_listrecords_get(self):
        response = self.app.get(url('harvest', id='listrecords'),params={'from':self.from_date,'until':self.until_date})
        self.validate_listrecords_response(response)

    def test_listrecords_post(self):
        data = json.dumps({'from':self.from_date,'until':self.until_date})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self.validate_listrecords_response(response)


    def validate_listidentifiers_response(self, response):
        data = json.loads(response.body)
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
