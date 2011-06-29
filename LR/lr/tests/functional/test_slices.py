from lr.tests import *
from datetime import datetime, timedelta
import urllib2
import couchdb
    
import json
    
#json_headers={'Content-Type':'application/json; charset=utf-8'}
json_headers={'content-type': 'application/json'}

class TestSlicesController(TestController):

    testKeys = ['alphaTestKey', 'betaTestKey', 'gammaTestKey']
    otherKeys = ['deltaTestKey', 'epsilonTestKey', 'zetaTestKey']
    testDataKey = 'LR-test-data-slice-jbrecht'
    identities = ['FederalMuseumTestIdentity', 'FederalArchivesTestIdentity', 'UniversityXTestIdentity']    
    #T16:18:21.186899Z
    test_start_date_string  = "2111-01-01"
    
    start_date = datetime.strptime(test_start_date_string,"%Y-%m-%d")
    #end_date = datetime.strptime("2011-01-01","%Y-%m-%d")
    
    database='resource_data'
    server = couchdb.Server()
    db = server[database]
    
    setupCount=0
    
    def writeTestData(self, testName):
        self.removeTestData()
        test_data = { "documents" : [] }
        for testKey in self.testKeys :
            for testIdentity in self.identities :
                self.setupCount = self.setupCount + 1
                setupCountFlag = testName + "setupCount" + str(self.setupCount)
                testDoc = self._buildTestDoc(testIdentity+testName, [setupCountFlag, self.testDataKey, testKey+testName, self.otherKeys[0], self.otherKeys[1]], "metadata", ["nsdl_dc"])
                test_data["documents"].append(testDoc)
                
        docs_json = json.dumps(test_data)
        response = self.app.post('/publish', params=docs_json, headers=json_headers)
        return response
        
    def writeMultiKeyTestData(self, testName):
        self.removeTestData()
        test_data = { "documents" : [] }
        for testIdentity in self.identities :
            self.setupCount = self.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(self.setupCount)
            testDoc = self._buildTestDoc(testIdentity+testName, [setupCountFlag, self.testDataKey, self.testKeys[0]+testName, self.testKeys[1]+testName, self.testKeys[2]+testName, self.otherKeys[0], self.otherKeys[1]], "metadata", ["nsdl_dc"])
            test_data["documents"].append(testDoc)
                
        docs_json = json.dumps(test_data)
        response = self.app.post('/publish', params=docs_json, headers=json_headers)
        return response

    def _buildTestDoc(self, submitter, keys, type, schemas):
        testDoc = {
                   "resource_data":"data",
                   "keys": keys, \
                   "TOS":{
                        "submission_attribution":"My Attribution",
                        "submission_TOS":"My TOS"
                    },
                   "payload_placement":"inline",
                   "active": True,
                   "resource_locator":"http://my.resource.locator",
                   "doc_type":"resource_data",
                   "resource_data_type": type,
                   "payload_schema_locator":"http://my.sceham.locator",
                   "payload_schema": schemas,
                   "doc_version":"0.21.0",
                   "identity":{
                               "submitter":submitter,
                               "submitter_type":"agent"
                               }
                   }
        return testDoc
    
    def updateTestDataWithTestDates(self, docs):
        for result in docs['document_results'] :
            doc_id = result["doc_ID"]
            doc = self.db[doc_id]
            doc["node_timestamp"] = self.test_start_date_string
            self.db[doc.id] = doc
        
    def tearDown(self):
        #self.removeTestData()
        a=1

    def removeTestData(self):
        parameters = {}
        parameters['any_tags'] = [self.testDataKey]
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        
        for doc in docs :
            doc_id = doc["doc_ID"]
            couchdoc = self.db[doc_id]
            self.db.delete(couchdoc)
        
    def _checkIdentity(self, doc, identity) :
        
        if doc['identity'].has_key('submitter') :
            if doc['identity']['submitter'].lower() == identity.lower() : return True
        if doc['identity'].has_key('author') :
            if doc['identity']['author'].lower() == identity.lower() : return True
        if doc['identity'].has_key('owner') :
            if doc['identity']['owner'].lower() == identity.lower() : return True
        if doc['identity'].has_key('signer') :
            if doc['identity']['signer'].lower() == identity.lower() : return True
            
        return False;
    
    def _checkTimestamp(self, doc, timestamp) :
        
        if doc.has_key('node_timestamp') :
            if doc['node_timestamp'].lower() == timestamp.lower() : return True
            
        return False;
    
    def _checkTag(self, doc, tag) :
        for key in doc['keys'] :
            if key.lower() == tag.lower() : return True
        
        for schema in doc['payload_schema'] :
            if schema.lower() == tag.lower() : return True
    
        if doc.resource_data_type.lower() == tag.lower() : return True
        
        return False
    
    #paramKeys = ['start_date', 'identity', 'any_tags', 'full_docs']
    
    def _slice(self, parameters) :
        print "sliceparameters: " + str(parameters)
        response = self.app.get('/slice', params=parameters, headers=json_headers)
        print "sliceresponse: " + str(response)
        return response
    
    def test_by_date(self):
        response = self.writeTestData("test_by_date")
        data = json.loads(response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters['start_date'] = self.test_start_date_string
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        assert len(docs)==9
        if len(docs)== 9 :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string)
            
        self.removeTestData()
    
    #test that there are 3 documents with identity = identities[0]
    def test_by_identity(self):
        self.writeTestData("test_by_identity")
        parameters = {}
        parameters['identity'] = self.identities[1]+"test_by_identity"
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        assert len(docs)==3
        if len(docs)==3 :
            assert self._checkIdentity(docs[0]['resource_data_description'], self.identities[1]+"test_by_identity")
            assert self._checkIdentity(docs[1]['resource_data_description'], self.identities[1]+"test_by_identity")
            assert self._checkIdentity(docs[2]['resource_data_description'], self.identities[1]+"test_by_identity")
        self.removeTestData()
        
        
    #test that there are 3 documents with key = testKeys[0]
    def test_by_single_key(self):
        self.writeTestData("test_by_single_key")
        parameters = {}
        parameters['any_tags'] = [self.testKeys[0]+"test_by_single_key"]
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=3 :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==3
        if len(docs)==3 :
            assert self._checkTag(docs[0]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
            assert self._checkTag(docs[1]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
            assert self._checkTag(docs[2]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
        
        self.removeTestData()
        
    def test_by_multiple_keys(self):
        self.writeMultiKeyTestData("test_by_multiple_keys")
        parameters = {}
        parameters['any_tags'] = [self.testKeys[0]+"test_by_multiple_keys", self.testKeys[1]+"test_by_multiple_keys", self.testKeys[2]+"test_by_multiple_keys"]
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=3 :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==3
        if len(docs)==3 :
            for testKey in self.testKeys :
                for doc in docs :
                    assert self._checkTag(doc['resource_data_description'], testKey+"test_by_multiple_keys")
        
        self.removeTestData()
        
        
    def test_by_date_and_key(self):
        response = self.writeTestData("test_by_date_and_key")
        data = json.loads(response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters['start_date'] = self.test_start_date_string
        parameters['any_tags'] = [self.testKeys[0]+"test_by_date_and_key"]
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=3 :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
            print "data is: "
            print str(data)
        assert len(docs)==3
        if len(docs)== 3 :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string)
                assert self._checkTag(doc['resource_data_description'], self.testKeys[0]+"test_by_date_and_key")
            
        self.removeTestData()

            
    def test_by_identity_and_key(self):
        self.writeTestData("test_by_identity_and_key")
        parameters = {}
        parameters['any_tags'] = [self.testKeys[0]+"test_by_identity_and_key"]
        parameters['identity'] = self.identities[1]+"test_by_identity_and_key"
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=1 :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==1
        if len(docs)==1 :
            for doc in docs :
                assert self._checkTag(doc['resource_data_description'], self.testKeys[0]+"test_by_identity_and_key")
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_identity_and_key")
        
        
    def test_by_date_and_identity(self):
        response = self.writeTestData("test_by_date_and_identity")
        data = json.loads(response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters['start_date'] = self.test_start_date_string
        parameters['identity'] = self.identities[1]+"test_by_date_and_identity"
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=3 :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
            print "data is: "
            print str(data)
        assert len(docs)==3
        if len(docs)== 3 :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string)
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_date_and_identity")

        
        
    def test_by_all(self):
        response = self.writeMultiKeyTestData("test_by_all")
        data = json.loads(response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters['start_date'] = self.test_start_date_string
        parameters['identity'] = self.identities[1]+"test_by_all"
        parameters['any_tags'] = [self.testKeys[0]+"test_by_all", self.testKeys[1]+"test_by_all", self.testKeys[2]+"test_by_all"]
        parameters['full_docs'] = True
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=1 :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
            print "data is: "
            print str(data)
        assert len(docs)==1
        if len(docs)== 1 :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string)
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_all")
                for testKey in self.testKeys :
                    assert self._checkTag(doc['resource_data_description'], testKey+"test_by_all")

