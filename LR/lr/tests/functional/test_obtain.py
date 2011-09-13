from lr.tests import *
import json
import urllib
import logging
from webtest import AppError
log = logging.getLogger(__name__)
headers={'Content-Type': 'application/json'}
class TestObtainController(TestController):
    def _getInitialPostData(self):
        data = {
            "by_doc_ID":False,
            "by_resource_ID":True,
            "ids_only":False            
        }
        return data
    def _validateResponse(self,resp):
        data = json.loads(resp.body)
        assert(data['documents'])
        assert(len(data['documents'])>0)
        return data
    def _validateError(self,error):
        data = json.loads(error)
        assert(data["OK"] == False)
    def test_create(self):
        params = self._getInitialPostData()
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response)
        # Test response...
    def test_create_ids_only(self):
        params = self._getInitialPostData()
        params['ids_only'] = True
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response)
    def test_create_by_doc_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        del params['by_resource_ID']
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response)
    def test_create_by_resource_id(self):
        params = self._getInitialPostData()
        del params['by_doc_ID']
        params = json.dumps(params)
        response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        self._validateResponse(response)        
    def test_create_by_doc_id_and_by_resource_id(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = False
        params['request_IDs'] = ['fffc4ddde2574f578e8f19e1791075e9','33c3b509ad5b42eba5e3748599612954']
        response = self.app.post(url(controller='obtain'), params=json.dumps(params) ,headers=headers)
        data = self._validateResponse(response)
        for doc in data['documents']:
            assert(doc['doc_ID'] in params['request_IDs'])
    def test_create_by_doc_id_and_by_resource_id_fail(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = True
        params['request_IDs'] = ['http://dum.rvp.cz/materialy/stahnout.html?s=uvwcqfum','http://www3.ac-nancy-metz.fr/cddp57/cinema/']
        response = self.app.post(url(controller='obtain'), params=json.dumps(params) ,headers=headers)
        data = self._validateResponse(response)
        for doc in data['documents']:
            assert(doc['doc_ID'] in params['request_IDs'])
    def test_create_by_doc_id_and_by_resource_id_both_true(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = True
        params['by_resource_ID'] = True
        params['request_IDs'] = ['fffc4ddde2574f578e8f19e1791075e9']
        try:
            response = self.app.post(url(controller='obtain'), params=json.dumps(params) ,headers=headers)
        except AppError as ex:
            self._validateError(ex.message[ex.message.rfind('{'):])
            pass#expected error
    def test_create_by_doc_id_and_by_resource_id_fail_both_false(self):
        params = self._getInitialPostData()
        params['by_doc_ID'] = False
        params['by_resource_ID'] = False
        params['request_IDs'] = ['http://dum.rvp.cz/materialy/stahnout.html?s=uvwcqfum']
        params = json.dumps(params)
        try:
            response = self.app.post(url(controller='obtain'), params=params ,headers=headers)
        except AppError as ex:
            self._validateError(ex.message[ex.message.rfind('{'):])
            pass#expected error        
