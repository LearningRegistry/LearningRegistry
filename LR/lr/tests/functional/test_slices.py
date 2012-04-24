from lr.tests import *
from datetime import datetime, timedelta
import urllib2
import couchdb
import time
import urllib    
import json
from pylons.configuration import config
from urllib2 import urlopen, quote
from lr.lib import helpers as helpers
import logging
log = logging.getLogger(__name__)
json_headers={'content-type': 'application/json'}

END_DATE = 'until'
START_DATE = 'from'
IDENTITY = 'identity'
RESUMPTION = 'resumption_token'
ANY_TAGS = 'any_tags'
IDS_ONLY = 'ids_only'


#Set the data multiplier value to control the volume of test data written. Typical tests write 3-9 
#test documents, multiplied by the data multiplier. 
DATA_MULTIPLIER = 3

def DataCleaner(testName, type="Basic"):
    
    
    #write a document for each combination of test key and test identity (currently 3X3), multiplied
    #by the data multiplier. Returns the response from posting this array of docs to the publish 
    #service. Also attempts to force a reindex (by calling the slice view directly) before returning.
    def writeTestData(obj):
        test_data = { "documents" : [] }
        
        for x in xrange(0,DATA_MULTIPLIER):
            for testKey in obj.testKeys :
                for testIdentity in obj.identities :
                    obj.setupCount = obj.setupCount + 1
                    setupCountFlag = testName + "setupCount" + str(obj.setupCount)
                    testDoc = buildTestDoc(testIdentity+testName, [setupCountFlag, obj.testDataKey, testKey+testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", [obj.testSchema+testName])
                    test_data["documents"].append(testDoc)
                
        docs_json = json.dumps(test_data)
        
        
        #all the commented out code below is for debugging, principally to measure time to 
        #publish and time to reindex, but also to determine whether the re-index call is 
        #actually working
        
        #info = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_info")
        #print "info, pre-publish: " + str(info.read())
        
        #start = time.clock()
        #print "about to publish " + str(len(test_data["documents"])) + " documents."
        response = obj.app.post('/publish', params=docs_json, headers={"Content-type": "application/json"})
        #pub_time = time.clock()
        #print "published, elapsed time: " + str(pub_time - start) + ". about to wait for index..."
        #info = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_info")
        #print "info, post-publish: " + str(info.read())
        #This call is here to attempt to force a re-index. Not clear if it is working properly
        url_result = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1&reduce=false&descending=true")
        #print "indexed, elapsed time: " + str(time.clock() - pub_time) + ", output is: " + str(url_result.read())
        
        #info = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_info")
        #print "info, post-index: " + str(info.read())
        
        return response
    
    
    #for each identity in test indentities, writes a doc with all 3 test keys
    def writeMultiKeyTestData(obj):
        test_data = { "documents" : [] }
        for testIdentity in obj.identities :
            obj.setupCount = obj.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(obj.setupCount)
            testDoc = buildTestDoc(testIdentity+testName, [setupCountFlag, obj.testDataKey, obj.testKeys[0]+testName, obj.testKeys[1]+testName, obj.testKeys[2]+testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", [obj.testSchema+testName])
            test_data["documents"].append(testDoc)
                
        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers=json_headers)
        urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
        return response
    
    #writes 150 docs for the purpose of resumption testing
    def writeResumptionTestData(obj):
        num_docs = 150
        #i=0
        test_data = { "documents" : [] }
        #while i<num_docs:
        for x in xrange(0,num_docs):
            obj.setupCount = obj.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(obj.setupCount)
            testDoc = buildTestDoc(obj.identities[1]+testName, [setupCountFlag, obj.testDataKey, obj.testKeys[0]+testName, obj.testKeys[1]+testName, obj.testKeys[2]+testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", [obj.testSchema+testName])
            test_data["documents"].append(testDoc)
            #i = i+1
                
        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers=json_headers)
        urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
        return response

    #simple template for writing test docs
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
    

    #attempt to delete all test data. get a list of doc ids to be deleted by slicing for the signature test
    #data key. then attempt to delete a doc having each id and each id+"-distributable". A single pass at
    #this can fail to delete many docs, but the exception message thrown is empty so it is not yet known
    #why. making multiple passes at this can improve the number of documents successfully deleted, so
    #we iterate until all docs are successfully deleted or that we've made 10 attempts.
    def removeTestData(obj):
        deleteFail = 0
        deleteDistributableFail = 0
        deleteAttempts = 0
        while True :
            deleteFail = 0
            deleteDistributableFail = 0
            print "delete attempt: " + str(deleteAttempts)
            del_key = quote("{\"tag\": \""+obj.testDataKey+"\"}")
            #del_key = quote("{\"tag\": \"metadata\"}")
            print("del_key: " + del_key)
            print("del response call: " + obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?reduce=false&key="+del_key)
            response = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?reduce=false&key="+del_key)
            data = json.loads(response.read()) 
            rows = data["rows"]
            print "rows of data to delete: " + str(len(rows))
            
            for row in rows :
                doc_id = row["id"]
                try:
                    del obj.db[doc_id]
                except Exception as e:
                    #print "error deleting doc_id: " + doc_id + ". Message: " + e.message
                    deleteFail = deleteFail + 1
                try:
                    del obj.db[doc_id+"-distributable"]
                except Exception as e:
                    #print "error deleting doc_id: " + doc_id+"-distributable" + ". Message: " + e.message
                    deleteDistributableFail = deleteDistributableFail + 1
                    
            deleteAttempts = deleteAttempts + 1
            if (deleteFail==0 and deleteDistributableFail==0) or deleteAttempts>10:
                break
            else:
                print "deleteFail: " + str(deleteFail) + ", deleteDistributableFail: " + str(deleteDistributableFail)
                
                
        print "failed to delete: " + str(deleteFail)
        
    #a decorator to wrap each test case in that writes test data before the test is run and removes is after
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
                #removeTestData(self)
                removeTestData(self)
                self.test_data_response = None
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator

#a test controller that performs one empty test, mainly for testing the test_decorator
class TestSlicesSmallController(TestController):

    testKeys = ['alphaTestKey', 'betaTestKey', 'gammaTestKey']
    otherKeys = ['deltaTestKey', 'epsilonTestKey', 'zetaTestKey']
    testSchema = 'NSDL'
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
    
    @DataCleaner("stuff")
    def test_stuff(self):
        pass

#the main suite of tests
class TestSlicesController(TestController):

    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "slice"
    testKeys = ['alphaTestKey', 'betaTestKey', 'gammaTestKey']
    otherKeys = ['deltaTestKey', 'epsilonTestKey', 'zetaTestKey']
    testSchema = 'NSDL'
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
    
    #slice for test docs containing the signature test key
    def _sliceForAllTestDocs(self):
        parameters = {}
        parameters["any_tags"] = [self.testDataKey]
        response = self._slice(parameters)
        data = json.loads(response.body) 
        docs = data["documents"]
        return docs
    
    #take an array of docs and apply the test start date as all their node timestamps
    def updateTestDataWithTestDates(self, docs):
        for result in docs['document_results'] :
            doc_id = result["doc_ID"]
            doc = self.db[doc_id]
            doc["node_timestamp"] = self.test_start_date_string + self.test_time_string
            self.db[doc.id] = doc
        urlopen(self.couch_url+"/resource_data/_design/learningregistry-slice/_view/docs?limit=1")
            
    #take an array of docs and apply a number of test dates to their node timestamps
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
        
    #returns true if one of the doc's indentities matches the argument
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
    
    #tests that the doc's node_timestamp matches the argument
    def _checkTimestamp(self, doc, timestamp) :
        
        if doc.has_key('node_timestamp') :
            if doc['node_timestamp'].lower() == timestamp.lower() : return True
            
        return False;
    
    #check that the doc has the argument tag
    def _checkTag(self, doc, tag) :
        for key in doc['keys'] :
            if key.lower() == tag.lower() : return True
        
        for schema in doc['payload_schema'] :
            if schema.lower() == tag.lower() : return True
    
        if doc.resource_data_type.lower() == tag.lower() : return True
        
        return False
    
    def _checkSchema(self, doc, testSchema) :
        for schema in doc['payload_schema'] :
            if schema.lower() == testSchema.lower() : return True
            
        return False
   
    
    #paramKeys = ['start_date', 'identity', 'any_tags', 'full_docs']
    
    #call slice with the supplied parameters
    def _slice(self, parameters) :
        print "sliceparameters: " + str(parameters)
        response = self.app.get('/slice', params=parameters, headers=json_headers)
        #print "sliceresponse: " + str(response)
        return response
    
    #iteratively load all the docs for a given slice call, adding any resumption docs to the initial set
    def _loadAllDocs(self, parameters, response):
        data = json.loads(response.body) 
        docs = data["documents"]
        while("resumption_token" in data):
            resumption_token = data["resumption_token"]
            parameters[RESUMPTION] = resumption_token
            response = self._slice(parameters)
            data = json.loads(response.body) 
            docs.extend(data["documents"])
        return docs
        
    
    
    @DataCleaner("test_by_date")   
    def test_by_date(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = self._loadAllDocs(parameters, response)
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
        docs = self._loadAllDocs(parameters, response)
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
        docs = self._loadAllDocs(parameters, response)
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)==3*DATA_MULTIPLIER :
            assert self._checkIdentity(docs[0]['resource_data_description'], self.identities[1]+"test_by_identity")
            assert self._checkIdentity(docs[1]['resource_data_description'], self.identities[1]+"test_by_identity")
            assert self._checkIdentity(docs[2]['resource_data_description'], self.identities[1]+"test_by_identity")
            
#    #test that there are 100 docs in the first result and 50 in the result after 1 resumption
#    #grab the service document for slice: http://127.0.0.1:5984/node/access%3Aslice
#    @DataCleaner("test_resumption", "Resumption")
#    def test_resumption(self):
#
#        slice_doc = helpers.getServiceDocument("access:slice")
#        page_size = slice_doc["service_data"]["doc_limit"]
#        
#        ##add test to assert that flow control is enabled, check that flow_control in service_data is true
#        
#        parameters = {}
#        parameters[IDENTITY] = self.identities[1]+"test_resumption"
#        parameters[IDS_ONLY] = False
#        response = self._slice(parameters)
#        data = json.loads(response.body) 
#        docs = data["documents"]
#        if len(docs)!=100 :
#            print "resumption assert will fail. doc count is: " + str(len(docs))
#        assert len(docs)==100
#        for doc in docs:
#            assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_resumption")
#        resumption_token = data["resumption_token"]
#        parameters[RESUMPTION] = resumption_token
#        response = self._slice(parameters)
#        data = json.loads(response.body) 
#        docs = data["documents"]
#        assert len(docs)==50
#        for doc in docs:
#            assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_resumption")

       
    #test that there are 3 documents with key = testKeys[0]
    @DataCleaner("test_by_single_key")
    def test_by_single_key(self):
        parameters = {}
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_single_key"]
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = self._loadAllDocs(parameters, response)
        if len(docs)!=3*DATA_MULTIPLIER :
            print "assert will fail in test_by_single_key. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)==3*DATA_MULTIPLIER :
            assert self._checkTag(docs[0]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
            assert self._checkTag(docs[1]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
            assert self._checkTag(docs[2]['resource_data_description'], self.testKeys[0]+"test_by_single_key")
    
    #test that there are 9*DATA_MULTIPLIER documents with key = "NSDL DC 1.02.020"
    @DataCleaner("test_by_paradata_schema")
    def test_by_paradata_schema(self):
        parameters = {}
        parameters[ANY_TAGS] = [self.testSchema+"test_by_paradata_schema"]
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = self._loadAllDocs(parameters, response)
        print "docs length in schema test is: " + str(len(docs))
        if len(docs)!=9*DATA_MULTIPLIER :
            print "assert will fail in test_by_paradata_schema. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==9*DATA_MULTIPLIER
        if len(docs)==9*DATA_MULTIPLIER :
            assert self._checkSchema(docs[0]['resource_data_description'], self.testSchema+"test_by_paradata_schema")
            assert self._checkSchema(docs[1]['resource_data_description'], self.testSchema+"test_by_paradata_schema")
            assert self._checkSchema(docs[2]['resource_data_description'], self.testSchema+"test_by_paradata_schema")
        
    @DataCleaner("test_by_multiple_keys", "Multi")  
    def test_by_multiple_keys(self):
        parameters = {}
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_multiple_keys", self.testKeys[1]+"test_by_multiple_keys", self.testKeys[2]+"test_by_multiple_keys"]
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = self._loadAllDocs(parameters, response)
        if len(docs)!=3 :
            print "assert will fail in test_by_multiple_keys. docs are:"
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
        docs = self._loadAllDocs(parameters, response)
        if len(docs)!=3*DATA_MULTIPLIER :
            print "assert will fail in test_by_date_and_key. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
            print "response is: "
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
        docs = self._loadAllDocs(parameters, response)
        if len(docs)!=1*DATA_MULTIPLIER :
            print "assert will fail in test_by_identity_and_key. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
        assert len(docs)==1*DATA_MULTIPLIER
        if len(docs)==1*DATA_MULTIPLIER :
            for doc in docs :
                assert self._checkTag(doc['resource_data_description'], self.testKeys[0]+"test_by_identity_and_key")
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_identity_and_key")

    @DataCleaner("test_by_identity_and_key_check_resultCount") 
    def test_by_identity_and_key_check_resultCount(self):
        print 'test_by_identity_and_key_check_resultCount'
        parameters = {}
        parameters[ANY_TAGS] = [self.testKeys[0]+"test_by_identity_and_key_check_resultCount"]
        parameters[IDENTITY] = self.identities[1]+"test_by_identity_and_key_check_resultCount"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        data = json.loads(response.body)
        docsCount = len(self._loadAllDocs(parameters, response))
        assert data['resultCount'] == docsCount
        
    @DataCleaner("test_by_date_and_identity") 
    def test_by_date_and_identity(self):
        data = json.loads(self.test_data_response.body) 
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDENTITY] = self.identities[1]+"test_by_date_and_identity"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = self._loadAllDocs(parameters, response)
        if len(docs)!=3*DATA_MULTIPLIER :
            print "assert will fail in test_by_date_and_identity. docs are:"
            for doc in docs :
                doc_id = doc["doc_ID"]
                couchdoc = self.db[doc_id]
                print json.dumps(couchdoc)
            print "full response is: "
            print str(response.body)
        assert len(docs)==3*DATA_MULTIPLIER
        if len(docs)== 3*DATA_MULTIPLIER :
            for doc in docs:
                assert self._checkTimestamp(doc['resource_data_description'], self.test_start_date_string+self.test_time_string)
                assert self._checkIdentity(doc['resource_data_description'], self.identities[1]+"test_by_date_and_identity")
    def test_is_view_updated(self):        
        
        couch = {
            "url": config["couchdb.url"],
            "resource_data": config["couchdb.db.resourcedata"]
        }        
        index_opts={
            "limit":1
        }

        with open("lr/tests/data/nsdl_dc/data-000000000.json",'r') as f:
            data = json.load(f)    

        retry = 0
        while True:
            # get view info to determine if updater is running
            req = urllib2.Request("{url}/{resource_data}/{view}".format(view='_design/learningregistry-slice/_info', **couch), headers=json_headers)
            view_info = json.loads(urllib2.urlopen(req).read())
            if 'view_index' in view_info and view_info['view_index']['updater_running'] == False:
                break;
            elif retry < 10:
                retry += 1
                wait_time = 5*retry
                log.info("Waiting {0} seconds for view updater to stop.".format(wait_time))
                time.sleep(wait_time)

            else:
                assert view_info['updater_running'] == False, "View updater is still running, need to extend wait time probably so it stops before test can continue."

        result = self.app.post('/publish', params=json.dumps(data), headers=json_headers)                
        params = {ANY_TAGS:['lr-test-data']}
        result =  json.loads(self._slice(params).body)
        assert not result['viewUpToDate']

   

        retry = 0
        while True:
            # force index
            req = urllib2.Request("{url}/{resource_data}/{view}".format(view='_design/learningregistry-slice/_view/docs', opts=urllib.urlencode(index_opts), **couch), headers=json_headers)
            resp = urllib2.urlopen(req).read()

            # get last db sequence
            req = urllib2.Request("{url}/{resource_data}/{view}".format(view='', **couch), headers=json_headers)
            db_info = json.loads(urllib2.urlopen(req).read())
            log.debug("db_info: "+json.dumps(db_info))
            # get last view sequenc
            req = urllib2.Request("{url}/{resource_data}/{view}".format(view='_design/learningregistry-slice/_info', **couch), headers=json_headers)
            view_info = json.loads(urllib2.urlopen(req).read())
            log.debug("view_info: "+json.dumps(view_info))

            # if the index is up-to-date, then these should be equal
            if db_info['committed_update_seq'] == view_info['view_index']['update_seq']:
                break;
            # we'll allow a few retries to give couchdb more time (the silly change monitor might be causing some grief)
            elif retry < 10:
                retry += 1
                time.sleep(3)
            # by now, if it hasn't caught up... assert an error.
            else:
                assert db_info['committed_update_seq'] == view_info['view_index']['update_seq'], "CouchDB view index isn't updating!!!"

        result =  json.loads(self._slice(params).body)
        assert result['viewUpToDate']

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
        docs = self._loadAllDocs(parameters, response)
        if len(docs)!=1 :
            print "assert will fail in test_by_all. docs are:"
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
