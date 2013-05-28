from functools import wraps
from lr.lib import helpers as helpers
from lr.tests import *
from lr.util.decorators import SetFlowControl, ModifiedServiceDoc, update_authz
from pylons.configuration import config
from urllib2 import urlopen, quote
import couchdb
import json
import logging
log = logging.getLogger(__name__)
json_headers = {'content-type': 'application/json'}

END_DATE = 'until'
START_DATE = 'from'
ANY_TAGS = "any_tags"
IDENTITY = "identity"
RESUMPTION = 'resumption_token'
IDS_ONLY = 'ids_only'


#Set the data multiplier value to control the volume of test data written. Typical tests write 3-9
#test documents, multiplied by the data multiplier.
DATA_MULTIPLIER = 3


def DataCleaner(testName, type="Basic"):

    #write a document for each combination of test key and test identity (currently 3X3), multiplied
    #by the data multiplier. Returns the response from posting this array of docs to the publish
    #service. Also attempts to force a reindex (by calling the slice view directly) before returning.
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def writeTestData(obj):
        test_data = {"documents": []}

        for x in xrange(0, DATA_MULTIPLIER):
            for testKey in obj.testKeys:
                for testIdentity in obj.identities:
                    obj.setupCount = obj.setupCount + 1
                    setupCountFlag = testName + "setupCount" + str(obj.setupCount)
                    testDoc = buildTestDoc(testIdentity + testName,
                                        [setupCountFlag, obj.testDataKey, testKey + testName, obj.otherKeys[0], obj.otherKeys[1]],
                                        "metadata",
                                        [obj.testSchema + testName])
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
        urlopen(obj.couch_url + "/resource_data/_design/learningregistry-slicelite/_view/by-date?limit=1&reduce=false&descending=true&limit=1").read()
        #print "indexed, elapsed time: " + str(time.clock() - pub_time) + ", output is: " + str(url_result.read())
        #info = urlopen(obj.couch_url+"/resource_data/_design/learningregistry-slice/_info")
        #print "info, post-index: " + str(info.read())

        return response

    #for each identity in test indentities, writes a doc with all 3 test keys
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def writeMultiKeyTestData(obj):
        test_data = {"documents": []}
        for testIdentity in obj.identities:
            obj.setupCount = obj.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(obj.setupCount)
            testDoc = buildTestDoc(testIdentity + testName,
                                   [setupCountFlag, obj.testDataKey, obj.testKeys[0] + testName, obj.testKeys[1] + testName, obj.testKeys[2] + testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", [obj.testSchema + testName])
            test_data["documents"].append(testDoc)

        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers=json_headers)
        urlopen(obj.couch_url + "/resource_data/_design/learningregistry-slicelite/_view/by-date?limit=1").read()
        return response

    #writes 150 docs for the purpose of resumption testing
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def writeResumptionTestData(obj):
        num_docs = 150
        #i=0
        test_data = {"documents": []}
        #while i<num_docs:
        for x in xrange(0, num_docs):
            obj.setupCount = obj.setupCount + 1
            setupCountFlag = testName + "setupCount" + str(obj.setupCount)
            testDoc = buildTestDoc(obj.identities[1] + testName, [setupCountFlag, obj.testDataKey, obj.testKeys[0] + testName, obj.testKeys[1] + testName, obj.testKeys[2] + testName, obj.otherKeys[0], obj.otherKeys[1]], "metadata", [obj.testSchema + testName])
            test_data["documents"].append(testDoc)
            #i = i+1
        docs_json = json.dumps(test_data)
        response = obj.app.post('/publish', params=docs_json, headers=json_headers)
        urlopen(obj.couch_url + "/resource_data/_design/learningregistry-slicelite/_view/by-date?limit=1")
        return response

    #simple template for writing test docs
    def buildTestDoc(submitter, keys, type, schemas):
        testDoc = {
                   "resource_data": "data",
                   "keys": keys, \
                   "TOS": {
                        "submission_attribution": "My Attribution",
                        "submission_TOS": "My TOS"
                    },
                   "payload_placement": "inline",
                   "active": True,
                   "resource_locator": "http://my.resource.locator",
                   "doc_type": "resource_data",
                   "resource_data_type": type,
                   "payload_schema_locator": "http://my.scehma.locator",
                   "payload_schema": schemas,
                   "doc_version": "0.23.0",
                   "identity": {
                               "submitter": submitter,
                               "submitter_type": "agent"
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
        while True:
            deleteFail = 0
            deleteDistributableFail = 0
            #del_key = quote("{\"tag\": \"metadata\"}")
            url = obj.couch_url + "/resource_data/_design/learningregistry-slicelite/_view/any-tags-by-date?reduce=false"
            #url = url % obj.testDataKey
            #fragment = &startkey=[\"%s\", 0]
            response = urlopen(url)
            data = json.loads(response.read())
            rows = data["rows"]
            for row in rows:
                doc_id = row["id"]
                try:
                    del obj.db[doc_id]
                except Exception:
                    #print "error deleting doc_id: " + doc_id + ". Message: " + e.message
                    deleteFail = deleteFail + 1

            deleteAttempts = deleteAttempts + 1
            if (deleteFail == 0 and deleteDistributableFail == 0) or deleteAttempts > 10:
                break
            else:
                pass  # print "deleteFail: " + str(deleteFail) + ", deleteDistributableFail: " + str(deleteDistributableFail)

    #a decorator to wrap each test case in that writes test data before the test is run and removes is after
    def test_decorator(fn):
        @wraps(fn)
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                if(type == "Basic"):
                    self.test_data_response = writeTestData(self)
                elif(type == "Multi"):
                    self.test_data_response = writeMultiKeyTestData(self)
                elif(type == "Resumption"):
                    self.test_data_response = writeResumptionTestData(self)
                return fn(self, *args, **kw)
            except:
                raise
            finally:
                #removeTestData(self)
                removeTestData(self)
                self.test_data_response = None
                #print "Wrapper After...."

        return test_decorated
    return test_decorator


#the main suite of tests
class TestSlicesController(TestController):

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)
        self.controllerName = "slice"
    testKeys = ['alphaTestKey', 'betaTestKey', 'gammaTestKey']
    otherKeys = ['deltaTestKey', 'epsilonTestKey', 'zetaTestKey']
    testSchema = 'NSDL'
    testDataKey = 'lr-test-data-slice-jbrecht'
    identities = ['FederalMuseumTestIdentity', 'FederalArchivesTestIdentity', 'UniversityXTestIdentity']
    test_time_string = "T00:00:00.000000Z"
    test_pre_date_string = "2110-01-01"
    test_start_date_string = "1970-01-01"
    test_mid_date_string = "2111-03-01"
    test_end_date_string = "2111-05-01"
    test_post_date_string = "2112-01-01"

    #start_date = datetime.strptime(test_start_date_string,"%Y-%m-%d")
    #end_date = datetime.strptime("2011-01-01","%Y-%m-%d")

    couch_url = config['couchdb.url']
    couch_dba_url = config['couchdb.url.dbadmin']
    database = 'resource_data'
    server = couchdb.Server(couch_dba_url)
    db = server[database]

    setupCount = 0

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
        for result in docs['document_results']:
            doc_id = result["doc_ID"]
            doc = self.db[doc_id]
            doc["node_timestamp"] = self.test_start_date_string + self.test_time_string
            self.db[doc.id] = doc
        urlopen(self.couch_url + "/resource_data/_design/learningregistry-slicelite/_view/by-date?limit=1")

    #take an array of docs and apply a number of test dates to their node timestamps
    def updateTestDataWithMultipleTestDates(self, docs, testName):
        for result in docs['document_results']:
            doc_id = result["doc_ID"]
            doc = self.db[doc_id]
            identity = doc["identity"]
            submitter = identity["submitter"]
            if(submitter == self.identities[0] + testName):
                doc["node_timestamp"] = self.test_start_date_string + self.test_time_string
            elif(submitter == self.identities[1] + testName):
                doc["node_timestamp"] = self.test_mid_date_string + self.test_time_string
            else:
                doc["node_timestamp"] = self.test_end_date_string + self.test_time_string

            self.db[doc.id] = doc
        urlopen(self.couch_url + "/resource_data/_design/learningregistry-slicelite/_view/by-date?limit=1")

    #returns true if one of the doc's indentities matches the argument
    def _checkIdentity(self, doc, identity):

        if doc[IDENTITY].has_key('submitter'):
            if doc[IDENTITY]['submitter'].lower() == identity.lower(): return True
        if doc[IDENTITY].has_key('author'):
            if doc[IDENTITY]['author'].lower() == identity.lower(): return True
        if doc[IDENTITY].has_key('owner'):
            if doc[IDENTITY]['owner'].lower() == identity.lower(): return True
        if doc[IDENTITY].has_key('signer'):
            if doc[IDENTITY]['signer'].lower() == identity.lower(): return True

        return False

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
    def _slice(self, parameters):
        print(parameters)
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
            response = self._slice({RESUMPTION: resumption_token})
            data = json.loads(response.body)
            for doc in data['documents']:
                docs.add(doc)
        return docs

    def _validate_page(self, parameters, response, test, max_pages):
        data = json.loads(response.body)
        pages = set()
        while "resumption_token" in data and max_pages > 0:
            page = set()
            for doc in data['documents']:
                #make sure no duplicated is current page of results
                assert doc['doc_ID'] not in page
                page.add(doc['doc_ID'])
            page = frozenset(page)
            #empty pages give a false positive
            if len(page) > 0:
                #make sure no page is duplicated
                assert page not in pages, (page, pages)
                pages.add(page)
            max_pages -= 1
            test(data['documents'])
            resumption_token = data["resumption_token"]
            response = self._slice({RESUMPTION: resumption_token})
            data = json.loads(response.body)

    @DataCleaner('test_by_date')
    def test_by_date(self):
        data = json.loads(self.test_data_response.body)
        self.updateTestDataWithTestDates(data)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        date_int = helpers.convertDateTime(self.test_start_date_string)
        docs = json.loads(response.body)
        docs = docs['documents']
        assert len(docs) > 0
        assert len([x for x in docs if helpers.convertDateTime(x['resource_data_description']["node_timestamp"]) >= date_int]) == len(docs)

    @DataCleaner("test_by_date_range")
    def test_by_date_range(self):
        data = json.loads(self.test_data_response.body)
        self.updateTestDataWithMultipleTestDates(data, "test_by_date_range")
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[END_DATE] = self.test_end_date_string
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = json.loads(response.body)
        docs = docs['documents']
        start_int = helpers.convertDateTime(self.test_start_date_string)
        end_int = helpers.convertDateTime(self.test_end_date_string)
        assert len(docs) > 0
        assert len([x for x in docs if start_int <= helpers.convertDateTime(x['resource_data_description']["node_timestamp"]) <= end_int]) == len(docs)

    # # #test that there are 3 documents with identity = identities[0]
    @DataCleaner("test_by_identity")
    def test_by_identity(self):
        parameters = {}
        parameters[IDENTITY] = self.identities[1] + 'test_by_identity'
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = json.loads(response.body)
        docs = docs['documents']
        assert len(docs) > 0
        for doc in docs:
            assert self._checkIdentity(doc['resource_data_description'], self.identities[1] + 'test_by_identity')

    # #test that there are 3 documents with key = testKeys[0]
    @DataCleaner("test_by_single_key")
    def test_by_single_key(self):
        parameters = {}
        parameters[ANY_TAGS] = self.testKeys[0] + "test_by_single_key"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = json.loads(response.body)
        docs = docs['documents']
        assert len(docs) > 0
        assert len([x for x in docs if self.testKeys[0] + "test_by_single_key" in x['resource_data_description']['keys']]) == len(docs)

    @DataCleaner("test_by_date_range_and_identity")
    def test_by_date_range_and_identity(self):
        data = json.loads(self.test_data_response.body)
        self.updateTestDataWithMultipleTestDates(data, "test_by_date_range")
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[END_DATE] = self.test_end_date_string
        parameters[IDENTITY] = self.identities[1] + "test_by_date_range_and_identity"
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = json.loads(response.body)
        docs = docs['documents']
        start_int = helpers.convertDateTime(self.test_start_date_string)
        end_int = helpers.convertDateTime(self.test_end_date_string)
        assert len(docs) > 0
        assert len([x for x in docs if start_int <= helpers.convertDateTime(x['resource_data_description']["node_timestamp"]) <= end_int]) == len(docs)
        for doc in docs:
            assert self._checkIdentity(doc['resource_data_description'], self.identities[1] + "test_by_date_range_and_identity")

    @DataCleaner('test_by_date_range_and_key')
    def test_by_date_range_and_key(self):
        data = json.loads(self.test_data_response.body)
        self.updateTestDataWithMultipleTestDates(data, "test_by_date_range")
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[END_DATE] = self.test_end_date_string
        parameters[ANY_TAGS] = self.testKeys[0] + 'test_by_date_range_and_key'
        parameters[IDS_ONLY] = False
        response = self._slice(parameters)
        docs = json.loads(response.body)
        docs = docs['documents']
        start_int = helpers.convertDateTime(self.test_start_date_string)
        end_int = helpers.convertDateTime(self.test_end_date_string)
        assert len(docs) > 0
        assert len([x for x in docs if start_int <= helpers.convertDateTime(x['resource_data_description']["node_timestamp"]) <= end_int]) == len(docs)
        assert len([x for x in docs if self.testKeys[0] + 'test_by_date_range_and_key' in x['resource_data_description']['keys']]) == len(docs)

    # # # #test that there are 100 docs in the first result and 50 in the result after 1 resumption
    # # # #grab the service document for slice: http://127.0.0.1:5984/node/access%3Aslice
    @SetFlowControl(True, config["lr.slice.docid"])
    @DataCleaner("test_resumption", "Resumption")
    def test_resumption(self):
        slice_doc = helpers.getServiceDocument(config["lr.slice.docid"])
        page_size = slice_doc["service_data"]["doc_limit"]

       ##add test to assert that flow control is enabled, check that flow_control in service_data is true
        date_int = helpers.convertDateTime(self.test_start_date_string)
        parameters = {}
        parameters[START_DATE] = self.test_start_date_string
        parameters[IDS_ONLY] = False
        parameters[ANY_TAGS] = self.testKeys[0] + 'test_resumption'
        response = self._slice(parameters)
        result = json.loads(response.body)
        assert "resumption_token" in result
        test_key = self.testKeys[0] + 'test_resumption'

        def validate_page(docs):
            assert len(docs) <= page_size, "resumption assert will fail. doc count is: " + str(len(docs))
            assert len([x for x in docs if helpers.convertDateTime(x['resource_data_description']["node_timestamp"]) >= date_int]) == len(docs)
            assert all(test_key in doc['resource_data_description']["keys"] for doc in docs)
        self._validate_page(parameters, response, validate_page, 10)
