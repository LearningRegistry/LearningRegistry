from lr.tests import *
import logging,json
from datetime import datetime
import unittest
time_format = '%Y-%m-%d %H:%M:%S.%f'
log = logging.getLogger(__name__)
headers={'content-type': 'application/json'}
test_id ='fda7ed3436d849fdbff6b106eb5f8cba'
class TestHarvestController(TestController):

    def validate_getrecord_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']
        assert data.has_key('getrecord')

    def test_getrecord_get(self):
        response = self.app.get(url('harvest', id='getrecord',request_id=test_id, by_doc_ID=True))
        self.validate_getrecord_response(response)

    def test_getrecord_post(self):
        data = json.dumps({'request_id':test_id,'by_doc_ID':True})
        response = self.app.post(url(controller='harvest',action='getrecord'), params=data ,headers=headers)
        self.validate_getrecord_response(response)


    def validate_listrecords_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']

    def test_listrecords_get(self):
        from_date = datetime(1900,1,1).strftime(time_format)
        until = datetime.today().strftime(time_format)
        response = self.app.get(url('harvest', id='listrecords'),params={'from':from_date,'until':until})
        self.validate_listrecords_response(response)

    def test_listrecords_post(self):
        data = json.dumps({'from':datetime(1900,1,1).strftime(time_format),'until':datetime.today().strftime(time_format)})
        response = self.app.post(url(controller='harvest',action='listrecords'), params=data ,headers=headers)
        self.validate_listrecords_response(response)


    def validate_listidentifiers_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']

    def test_listidentifiers_get(self):
        from_date = datetime(1900,1,1).strftime(time_format)
        until = datetime.today().strftime(time_format)
        response = self.app.get(url('harvest', id='listidentifiers'),params={'from':from_date,'until':until})
        self.validate_listidentifiers_response(response)

    def test_listidentifiers_post(self):
        data = json.dumps({'from':datetime(1900,1,1).strftime(time_format),'until':datetime.today().strftime(time_format)})
        response = self.app.post(url(controller='harvest',action='listidentifiers'), params=data ,headers={'content-type': 'application/json'})
        self.validate_listidentifiers_response(response)


    def validate_identify_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']

    def test_identify_get(self):
        response = self.app.get(url('harvest', id='identify'))
        self.validate_identify_response(response)

    def test_identify_post(self):
        response = self.app.post(url(controller='harvest',action='identify'), params={} ,headers={'content-type': 'application/json'})
        self.validate_identify_response(response)


    def validate_listmetadataformats_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and data['OK']

    def test_listmetadataformats_get(self):
        response = self.app.get(url('harvest', id='listmetadataformats'))
        self.validate_listmetadataformats_response(response)

    def test_listmetadataformats_post(self):
        response = self.app.post(url(controller='harvest',action='listmetadataformats'), params={} ,headers={'content-type': 'application/json'})
        self.validate_listmetadataformats_response(response)


    def validate_listsets_response(self, response):
        data = json.loads(response.body)
        assert data.has_key('OK') and not data['OK']

    def test_listmetadataformats_get(self):
        response = self.app.get(url('harvest', id='listsets'))
        self.validate_listsets_response(response)

    def test_listmetadataformats_post(self):
        response = self.app.post(url(controller='harvest',action='listsets'), params={} ,headers={'content-type': 'application/json'})
        self.validate_listsets_response(response)
