from lr.tests import *
from datetime import datetime, timedelta
import urllib2
import couchdb
import time
    
import json
from pylons.configuration import config
from urllib2 import urlopen

#json_headers={'Content-Type':'application/json; charset=utf-8'}
json_headers={'content-type': 'application/json'}

END_DATE = 'until'
START_DATE = 'from'
IDENTITY = 'identity'
RESUMPTION = 'resumption_token'
ANY_TAGS = 'any_tags'
IDS_ONLY = 'ids_only'

DATA_MULTIPLIER = 5

def DataCleaner(testName, type="Basic"):
    
    def writeTestData(obj):
        test_data = { "documents" : [] }
        
        for x in xrange(0,DATA_MULTIPLIER):
            for testKey in obj.testKeys :
                for testIdentity in obj.identities :
                    obj.setupCount = obj.setupCount + 1
                    setupCountFlag = testName + "setupCount" + str(obj.setupCount)
                    testDoc = buildTestDoc(testIdentity+testName, [setupCountFlag, obj.testDataKey, testKey+testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", ["nsdl_dc"])
                    test_data["documents"].append(testDoc)
                
        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers={"Content-type": "application/json"})
        urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
        return response
    
    
    def writeMultiKeyTestData(obj):
        test_data = { "documents" : [] }
        for testIdentity in obj.identities :
            obj.setupCount = obj.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(obj.setupCount)
            testDoc = buildTestDoc(testIdentity+testName, [setupCountFlag, obj.testDataKey, obj.testKeys[0]+testName, obj.testKeys[1]+testName, obj.testKeys[2]+testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", ["nsdl_dc"])
            test_data["documents"].append(testDoc)
                
        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers=json_headers)
        urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
        return response
    
    def writeResumptionTestData(obj):
        num_docs = 150
        #i=0
        test_data = { "documents" : [] }
        #while i<num_docs:
        for x in xrange(0,num_docs):
            obj.setupCount = obj.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(obj.setupCount)
            testDoc = buildTestDoc(obj.identities[1]+testName, [setupCountFlag, obj.testDataKey, obj.testKeys[0]+testName, obj.testKeys[1]+testName, obj.testKeys[2]+testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", ["nsdl_dc"])
            test_data["documents"].append(testDoc)
            #i = i+1
                
        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers=json_headers)
        urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
        return response

    def buildTestDoc(submitter, keys, type, schemas):
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
                   "payload_schema_locator":"http://my.scehma.locator",
                   "payload_schema": schemas,
                   "doc_version":"0.23.0",
                   "identity":{
                               "submitter":submitter,
                               "submitter_type":"agent"
                               }
                   }
        return testDoc
    
    
    def removeTestData(obj):
        response = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?reduce=false&key=\""+obj.testDataKey+"\"")
        body = response.read()
        data = json.loads(body) 
        rows = data["rows"]
        
        for row in rows :
            doc_id = row["id"]
            try:
                del obj.db[doc_id]
            except Exception as e:
                print e.message
            try:
                del obj.db[doc_id+"-distributable"]
            except Exception as e:
                print e.message
        
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                if(type=="Basic"):
                    self.test_data_response = writeTestData(self)
                elif(type=="Multi"):
                    self.test_data_response = writeMultiKeyTestData(self)
                elif(type=="Resumption"):
                    self.test_data_response = writeResumptionTestData(self)
                fn(self, *args, **kw)
            except :
                raise
            finally:
                removeTestData(self)
                self.test_data_response = None
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator

class TestSlicesController(TestController):

    testKeys = ['alphaTestKey', 'betaTestKey', 'gammaTestKey']
    otherKeys = ['deltaTestKey', 'epsilonTestKey', 'zetaTestKey']
    testDataKey = 'lr-test-data-slice-jbrecht'
    identities = ['FederalMuseumTestIdentity', 'FederalArchivesTestIdentity', 'UniversityXTestIdentity']    
    test_time_string = "T00:00:00.000000Z"
    test_pre_date_string = "2110-01-01"
    test_start_date_string  = "2111-01-01"
    test_mid_date_string  = "2111-03-01"
    test_end_date_string  = "2111-05-01"
    test_post_date_string = "2112-01-01"
    
    #start_date = datetime.strptime(test_start_date_string,"%Y-%m-%d")
    #end_date = datetime.strptime("2011-01-01","%Y-%m-%d")
    
    couch_url = config['couchdb.url']
    database='resource_data'
    server = couchdb.Server(couch_url)
    db = server[database]
    
    setupCount=0
    
    def _sliceForAllTestDocs(self):
        parameters = {}
        parameters["any_tags"] = [self.testDataKey]
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        return docs
    
    def updateTestDataWithTestDates(self, docs):
        for result in docs['document_results'] :
            doc_id = result["doc_ID"]
            doc = self.db[doc_id]
            doc["node_timestamp"] = self.test_start_date_string + self.test_time_string
            self.db[doc.id] = doc
        urlopen(self.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
            
    def updateTestDataWithMultipleTestDates(self, docs, testName):
        for result in docs['document_results'] :
            doc_id = result["doc_ID"]
            doc = self.db[doc_id]
            identity = doc["identity"]
            submitter = identity["submitter"]
            if(submitter==self.identities[0]+testName): 
                doc["node_timestamp"] = self.test_start_date_string + self.test_time_string
            elif(submitter==self.identities[1]+testName): 
                doc["node_timestamp"] = self.test_mid_date_string + self.test_time_string
            else: 
                doc["node_timestamp"] = self.test_end_date_string + self.test_time_string
            
            self.db[doc.id] = doc
        urlopen(self.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
        
    def _checkIdentity(self, doc, identity) :
        
        if doc[IDENTITY].has_key('submitter') :
            if doc[IDENTITY]['submitter'].lower() == identity.lower() : return True
        if doc[IDENTITY].has_key('author') :
            if doc[IDENTITY]['author'].lower() == identity.lower() : return True
        if doc[IDENTITY].has_key('owner') :
            if doc[IDENTITY]['owner'].lower() == identity.lower() : return True
        if doc[IDENTITY].has_key('signer') :
            if doc[IDENTITY]['signer'].lower() == identity.lower() : return True
            
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
    
    
    @DataCleaner("test_by_date")   
    def test_by_date(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs) != 9*DATA_MULTIPLIER :
            print "assert will fail in test_by_date. len(docs): " + str(len(docs))
            print "data: " + str(data)
            all_docs = self._sliceForAllTestDocs()
            print "all docs: " + str(all_docs)
        assert len(docs)==9*DATA_MULTIPLIER
        if len(docs)== 9*DATA_MULTIPLIER :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string+self.test_time_string)
    
    @DataCleaner("test_by_date_range")   
    def test_by_date_range(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithMultipleTestDates(data, "test_by_date_range")
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[END_DATE] = self.test_end_date_string
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        self.assertEqual(len(docs), 6*DATA_MULTIPLIER)
        if len(docs)== 6*DATA_MULTIPLIER :
            for doc in docs:
                assert (self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string+self.test_time_string) or
                        self._checkTimestamp(doc['resource_data_description'], self.test_mid_date_string+self.test_time_string) )
    
    #test that there are 3 documents with identity = identities[0]
    @DataCleaner("test_by_identity")
    def test_by_identity(self):
        parameters = {}
        parameters[IDENTITY] = self.identities[1]+"test_by_identity"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)==3*DATA_MULTIPLIER :
            assert self._checkIdentity(docs[0]['resource_data_description'], self.identities[1]+"test_by_identity")
            assert self._checkIdentity(docs[1]['resource_data_description'], self.identities[1]+"test_by_identity")
            assert self._checkIdentity(docs[2]['resource_data_description'], self.identities[1]+"test_by_identity")
            
    #test that there are 100 docs in the first result and 50 in the result after 1 resumption
    @DataCleaner("test_resumption", "Resumption")
    def test_resumption(self):
        parameters = {}
        parameters[IDENTITY] = self.identities[1]+"test_resumption"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=100 :
            print "resumption assert will fail. doc count is: " + str(len(docs))
        assert len(docs)==100
        for doc in docs:
            assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_resumption")
        resumption_token = data["resumption_token"]
        parameters[RESUMPTION] = resumption_token
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        assert len(docs)==50
        for doc in docs:
            assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_resumption")

       
    #test that there are 3 documents with key = testKeys[0]
    @DataCleaner("test_by_single_key")
    def test_by_single_key(self):
        parameters = {}
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_single_key"]
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=3*DATA_MULTIPLIER :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)==3*DATA_MULTIPLIER :
            assert self._checkTag(docs[0]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
            assert self._checkTag(docs[1]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
            assert self._checkTag(docs[2]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
    
        
    @DataCleaner("test_by_multiple_keys", "Multi")  
    def test_by_multiple_keys(self):
        parameters = {}
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_multiple_keys", self.testKeys[1]+"test_by_multiple_keys", self.testKeys[2]+"test_by_multiple_keys"]
        parameters[IDS_ONLY] = False
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
        
        
   
    @DataCleaner("test_by_date_and_key")     
    def test_by_date_and_key(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_date_and_key"]
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=3*DATA_MULTIPLIER :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
            print "data is: "
            print str(data)
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)== 3*DATA_MULTIPLIER :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string+self.test_time_string)
                assert self._checkTag(doc['resource_data_description'], self.testKeys[0]+"test_by_date_and_key")

            
    @DataCleaner("test_by_identity_and_key") 
    def test_by_identity_and_key(self):
        parameters = {}
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_identity_and_key"]
        parameters[IDENTITY] = self.identities[1]+"test_by_identity_and_key"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        if len(docs)!=1*DATA_MULTIPLIER :
            print "assert will fail. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==1*DATA_MULTIPLIER
        if len(docs)==1*DATA_MULTIPLIER :
            for doc in docs :
                assert self._checkTag(doc['resource_data_description'], self.testKeys[0]+"test_by_identity_and_key")
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_identity_and_key")
        
        
    @DataCleaner("test_by_date_and_identity") 
    def test_by_date_and_identity(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDENTITY] = self.identities[1]+"test_by_date_and_identity"
        parameters[IDS_ONLY] = False
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
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)== 3*DATA_MULTIPLIER :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string+self.test_time_string)
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_date_and_identity")

    @DataCleaner("test_by_all", "Multi") 
    def test_by_all(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDENTITY] = self.identities[1]+"test_by_all"
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_all", self.testKeys[1]+"test_by_all", self.testKeys[2]+"test_by_all"]
        parameters[IDS_ONLY] = False
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
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string+self.test_time_string)
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_all")
                for testKey in self.testKeys :
                    assert self._checkTag(doc['resource_data_description'], testKey+"test_by_all")
