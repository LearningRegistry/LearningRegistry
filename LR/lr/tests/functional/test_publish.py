from lr.tests import *
from lr.model import ResourceDataModel
from lr.util import decorators
from time import sleep
from pylons import config
import couchdb, json, re


headers={'Content-Type': 'application/json'}

def _cmp_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

class TestPublisherController(TestController):

    _PUBLISH_UNSUCCESSFUL_MSG = "Publish was not successful"

    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "publish"
        
        self.oauth_info = {
                "name": "tester@example.com",
                "full_name": "Joe Tester"
        }

        self.oauth_user = {
           "_id": "org.couchdb.user:{0}".format(self.oauth_info["name"]),
           "type": "user",
           "name": self.oauth_info["name"],
           "roles": [
               "browserid"
           ],
           "browserid": True,
           "oauth": {
               "consumer_keys": {
                   self.oauth_info["name"] : "ABC_consumer_key_123"
               },
               "tokens": {
                   "node_sign_token": "QWERTY_token_ASDFGH",
               }
           },
           "lrsignature": {
               "full_name": self.oauth_info["full_name"]
           }
        }


    def test_index(self):
        pass

    @decorators.OAuthRequest(path="/publish", http_method="POST")
    def test_oauth_sign_publish(self):
        data = {
            "documents": 
                    [
                       {"doc_type": "resource_data",
                        "resource_locator": "http://example.com",
                         "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                         "update_timestamp": "2011-11-07T14:51:07.137671Z",
                         "TOS": {"submission_attribution": "Smithsonian Education",
                         "submission_TOS": "http://si.edu/Termsofuse"},
                         "resource_data_type": "metadata",
                         "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                         "payload_placement": "inline",
                         "payload_schema": ["NSDL DC 1.02.020"],
                         "doc_version": "0.23.0",
                         "active": True,
                         "identity": {
                                "signer": "Smithsonian Education <learning@si.edu>",
                                "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                                "submitter_type": "agent",
                                "curator": "Smithsonian Education",
                                "owner": "Smithsonian American Art Museum"
                                }
                         },
                         
                        {"doc_type": "resource_data",
                        "resource_locator": "http://example.com/1",
                         "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                         "TOS": {"submission_attribution": "Smithsonian Education",
                         "submission_TOS": "http://si.edu/Termsofuse"},
                         "resource_data_type": "metadata",
                         "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                         "payload_placement": "inline",
                         "payload_schema": ["NSDL DC 1.02.020"],
                         "create_timestamp": "2011-11-07T14:51:07.137671Z",
                         "doc_version": "0.21.0",
                         "active": True,
                         "identity": {
                                "signer": "Smithsonian Education <learning@si.edu>",
                                "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                                "submitter_type": "agent",
                                "curator": "Smithsonian Education",
                                "owner": "Smithsonian American Art Museum"
                                }
                        },
                        
                        {
                        "doc_type": "resource_data",
                        "resource_locator": "http://example.com/2",
                         "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                         "TOS": {"submission_attribution": "Smithsonian Education",
                         "submission_TOS": "http://si.edu/Termsofuse"},
                         "resource_data_type": "metadata",
                         "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                         "payload_placement": "inline",
                         "payload_schema": ["NSDL DC 1.02.020"],
                         "create_timestamp": "2011-11-07T14:51:07.137671Z",
                         "doc_version": "0.11.0",
                         "active": True,
                         "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                         "submitter_type": "agent",
                         }
                     ]
                }

        h={}
        h.update(headers)
        h.update(self.oauth.header)

        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        
 
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])

            doc = ResourceDataModel._defaultDB[docResults['doc_ID']]
            assert "doc_version" in doc and doc["doc_version"] is not None, "Missing doc_version"

            if _cmp_version(doc["doc_version"], "0.21.0") >= 0:
                    assert doc["identity"]["submitter"] == "{full_name} <{name}>".format(**self.oauth_info), "identity.submitter is not correct for #{0}, got: {1}".format(index, doc["identity"]["submitter"])
                    assert doc["identity"]["submitter_type"] == "user", "identity.submitter_type is not correct for #{0}, got: {1}".format(index, doc["identity"]["submitter_type"])
                    assert doc["identity"]["signer"] == config["app_conf"]["lr.publish.signing.signer"], "identity.signer is not correct for #{0}, got: {1}".format(index, doc["identity"]["signer"])
            else:
                    assert doc["submitter"] == "{full_name} <{name}>".format(**self.oauth_info), "doc.submitter is not correct for #{0}, got: {1}".format(index, doc["submitter"])
                    assert doc["submitter_type"] == "user", "doc.submitter_type is not correct for #{0}, got: {1}".format(index, doc["submitter_type"])

            if _cmp_version(doc["doc_version"], "0.20.0") >= 0:
                assert "digital_signature" in doc, "Digital Signature missing when it was expected."
            else:
                assert "digital_signature" not in doc, "Digital Signature exists in document version earlier than expected."


        ##delete the published  testdocuments.
        #Wait for documents to be processed
        sleep(5)
        for  doc in result['document_results']:
            try:
                del ResourceDataModel._defaultDB[doc['doc_ID']]
            except:
                pass


    def test_invalid_doc_version(self):
        data = { 
                "documents": 
                     [
                        { # Invalid doc_version value
                        "active" : True,
                        "doc_type" : "resource_data",
                        "doc_version": "zzzz",
                        "payload_schema": ["none"],
                        "resource_data_type": "metadata",
                        "resource_locator" : "http://example.com",
                        "identity": { "submitter" : "anonymous", "submitter_type" : "anonymous"},
                        "payload_placement": "inline",
                        "resource_data" : "something",
                        "TOS" : { "submission_TOS" : "http://google.com" },
                        "weight" : 0,
                        "resource_TTL" : 0
                        },
                        { # Invalid doc_version type
                        "active" : True,
                        "doc_type" : "resource_data",
                        "doc_version": 0.23,
                        "payload_schema": ["none"],
                        "resource_data_type": "metadata",
                        "resource_locator" : "http://example.com",
                        "identity": { "submitter" : "anonymous", "submitter_type" : "anonymous"},
                        "payload_placement": "inline",
                        "resource_data" : "something",
                        "TOS" : { "submission_TOS" : "http://google.com" },
                        "weight" : 0,
                        "resource_TTL" : 0
                        },
                        { # Missing doc_version
                        "active" : True,
                        "doc_type" : "resource_data",
                        "payload_schema": ["none"],
                        "resource_data_type": "metadata",
                        "resource_locator" : "http://example.com",
                        "identity": { "submitter" : "anonymous", "submitter_type" : "anonymous"},
                        "payload_placement": "inline",
                        "resource_data" : "something",
                        "TOS" : { "submission_TOS" : "http://google.com" },
                        "weight" : 0,
                        "resource_TTL" : 0
                        } 
                     ]
                }
        result = json.loads(self.app.post('/publish',params=json.dumps(data), headers=headers).body)
        assert(result['OK'] == True), self._PUBLISH_UNSUCCESSFUL_MSG
        for doc in result['document_results']:
                assert(doc['OK'] == False), "Should catch missing/invalid doc version"

    def test_invalid_array_value(self):
        data = { 
                "documents": 
                     [
                        { # 'keys' contains integers instead of strings
                        "active" : True,
                        "doc_type" : "resource_data",
                        "doc_version": "0.23.0",
                        "payload_schema": ["none"],
                        "resource_data_type": "metadata",
                        "resource_locator" : "http://example.com",
                        "identity": { "submitter" : "anonymous", "submitter_type" : "anonymous"},
                        "payload_placement": "inline",
                        "resource_data" : "something",
                        "TOS" : { "submission_TOS" : "http://google.com" },
                        "weight" : 0,
                        "resource_TTL" : 0,
                        "keys" : [1, 2, 3]
                        }
                     ]
                }
        result = json.loads(self.app.post('/publish',params=json.dumps(data), headers=headers).body)
        assert(result['OK'] == True), self._PUBLISH_UNSUCCESSFUL_MSG
        assert(result['document_results'][0]['OK'] == False), "Should catch document with invalid array values"

    def test_empty_document_array(self):
        data = { "documents": [] }
        result = json.loads(self.app.post('/publish',params=json.dumps(data), headers=headers).body)
        assert(result['OK'] == False), "Should catch empty documents array on publish, no error returned"
        assert(result['error'] == "List of documents is empty"), "Incorrect error message returned"

    # Handles case where documents field is missing
    # Example here is trying to publish a document without the wrapper
    def test_missing_document_body(self):
        data = { 
                    "active" : True,
                    "doc_type" : "resource_data",
                    "doc_version": "0.23.0",
                    "payload_schema": ["none"],
                    "resource_data_type": "metadata",
                    "resource_locator" : "http://example.com",
                    "identity": { "submitter" : "anonymous", "submitter_type" : "anonymous"},
                    "payload_placement": "inline",
                    "resource_data" : "something",
                    "TOS" : { "submission_TOS" : "http://google.com" },
                    "weight" : 0,
                    "resource_TTL" : 0,
                }
        result = json.loads(self.app.post('/publish',params=json.dumps(data), headers=headers).body)
        assert(result['OK'] == False), "Accepted invalid json object on publish"
        assert(result['error'] == "Missing field 'documents' in post body"), "Incorrect error message returned"

    def test_multiple_version(self):
        data = {
            "documents": 
                    [
                       {"doc_type": "resource_data",
                        "resource_locator": "http://example.com",
                         "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                         "update_timestamp": "2011-11-07T14:51:07.137671Z",
                         "TOS": {"submission_attribution": "Smithsonian Education",
                         "submission_TOS": "http://si.edu/Termsofuse"},
                         "resource_data_type": "metadata",
                         "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                         "payload_placement": "inline",
                         "payload_schema": ["NSDL DC 1.02.020"],
                         "node_timestamp": "2011-12-21T04:57:18.343124Z",
                         "digital_signature": {"key_location": ["http://pgp.mit.edu:11371/pks/lookup?op=get&search=0xE006035FD5EFEA67"],
                         "signing_method": "LR-PGP.1.0",
                         "signature": "-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA256\n\n316c7e1e9436cc45f5c2f0a1ba8d560adefb22e2ca4abf72fa5279267c88ac6e-----BEGIN PGP SIGNATURE-----\nVersion: BCPG v1.46\n\niQFdBAEBCABHBQJOt+/6QBxTbWl0aHNvbmlhbiBFZHVjYXRpb24gKFNtaXRoc29u\naWFuIEVkdWNhdGlvbikgPGxlYXJuaW5nQHNpLmVkdT4ACgkQ4AYDX9Xv6merCAf+\nPJQ6TX7jTo79a9XKhaSmFbYTgRz+D/uN9ksWJjsmvvoprqjMnsZBivD+3YDE/nTK\nttexx5Gy173Sj0wsojY4UPVezPmwbBjA2+2CG9btTKIsg3WwQpqzPeA/6LT46Ski\n2v3UbbGAMAU00ereuOjmdsqRZkXD/ABtZ/LYVMQCIqVMdR3aeQorHzuLlxTuzt/A\nMFxJb4A+a2jVw5nUM2Ry/x31Cb0pQ9uNO+jIWr8Xl3fjqiD5dUtySmVYvOEjEYcN\nh1twKySLmRWx0OfLN/Fnr1+N+sXT/s7lPCopKV3leEC2FOKDTjHhFM3mKUJvV4E+\ncXWLz6hBgEtIJlRuIj/o"},
                         "doc_version": "0.23.0",
                         "active": True,
                         "identity": {"signer": "Smithsonian Education <learning@si.edu>",
                         "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                         "submitter_type": "agent",
                         "curator": "Smithsonian Education",
                         "owner": "Smithsonian American Art Museum"}
                         },
                         
                        {"doc_type": "resource_data",
                        "resource_locator": "http://example.com/1",
                         "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                         "TOS": {"submission_attribution": "Smithsonian Education",
                         "submission_TOS": "http://si.edu/Termsofuse"},
                         "resource_data_type": "metadata",
                         "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                         "payload_placement": "inline",
                         "payload_schema": ["NSDL DC 1.02.020"],
                         "node_timestamp": "2011-12-21T04:57:18.343124Z",
                         "digital_signature": {"key_location": ["http://pgp.mit.edu:11371/pks/lookup?op=get&search=0xE006035FD5EFEA67"],
                         "signing_method": "LR-PGP.1.0",
                         "signature": "-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA256\n\n316c7e1e9436cc45f5c2f0a1ba8d560adefb22e2ca4abf72fa5279267c88ac6e-----BEGIN PGP SIGNATURE-----\nVersion: BCPG v1.46\n\niQFdBAEBCABHBQJOt+/6QBxTbWl0aHNvbmlhbiBFZHVjYXRpb24gKFNtaXRoc29u\naWFuIEVkdWNhdGlvbikgPGxlYXJuaW5nQHNpLmVkdT4ACgkQ4AYDX9Xv6merCAf+\nPJQ6TX7jTo79a9XKhaSmFbYTgRz+D/uN9ksWJjsmvvoprqjMnsZBivD+3YDE/nTK\nttexx5Gy173Sj0wsojY4UPVezPmwbBjA2+2CG9btTKIsg3WwQpqzPeA/6LT46Ski\n2v3UbbGAMAU00ereuOjmdsqRZkXD/ABtZ/LYVMQCIqVMdR3aeQorHzuLlxTuzt/A\nMFxJb4A+a2jVw5nUM2Ry/x31Cb0pQ9uNO+jIWr8Xl3fjqiD5dUtySmVYvOEjEYcN\nh1twKySLmRWx0OfLN/Fnr1+N+sXT/s7lPCopKV3leEC2FOKDTjHhFM3mKUJvV4E+\ncXWLz6hBgEtIJlRuIj/o"},
                         "create_timestamp": "2011-11-07T14:51:07.137671Z",
                         "doc_version": "0.21.0",
                         "active": True,
                         "identity": {"signer": "Smithsonian Education <learning@si.edu>",
                         "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                         "submitter_type": "agent",
                         "curator": "Smithsonian Education",
                         "owner": "Smithsonian American Art Museum"}
                        },
                        
                        {
                        "doc_type": "resource_data",
                        "resource_locator": "http://example.com/2",
                         "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                         "TOS": {"submission_attribution": "Smithsonian Education",
                         "submission_TOS": "http://si.edu/Termsofuse"},
                         "resource_data_type": "metadata",
                         "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                         "payload_placement": "inline",
                         "payload_schema": ["NSDL DC 1.02.020"],
                         "create_timestamp": "2011-11-07T14:51:07.137671Z",
                         "doc_version": "0.11.0",
                         "active": True,
                         "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                         "submitter_type": "agent",
                         }
                     ]
                }

        result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        
        index = 0
        for docResults in result['document_results']:
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])
            index = index +1
        
        ##delete the published  testdocuments.
        #Wait for documents to be processed
        sleep(5)
        for  doc in result['document_results']:
            try:
                del ResourceDataModel._defaultDB[doc['doc_ID']]
            except:
                pass
            try:
                del ResourceDataModel._defaultDB[doc['doc_ID']+'-distributable']
            except:
                pass
