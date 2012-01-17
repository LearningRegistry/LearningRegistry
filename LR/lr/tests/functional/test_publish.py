from lr.tests import *
import json

headers={'Content-Type': 'application/json'}

class TestPublisherController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "publish"
        
    def test_required_empty_filed(self):
        #The following test doc has an empty required resource_locator fiedl that
        #should not get published.
        data = {"documents":[{"doc_type": "resource_data",
                    "resource_locator": "",
                     "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n                 xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n                 xmlns:dct=\"http://purl.org/dc/terms/\"\n                 xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n                 xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n                 schemaVersion=\"1.02.020\"\n                 xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n   <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n   <dc:title>Posters to Go</dc:title>\n   <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n   <dc:creator/>\n   <dc:language>en-US</dc:language>\n   <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n   <dc:format>text/html</dc:format>\n   <dc:date>2010-07-26</dc:date>\n   <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                     "update_timestamp": "2011-11-07T14:51:07.137671Z",
                     "TOS": {"submission_attribution": "Smithsonian Education",
                     "submission_TOS": "http://si.edu/Termsofuse"},
                     "_rev": "1-d7289942bb98ab5c3657b1cc1832ae50",
                     "resource_data_type": "metadata",
                     "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                     "payload_placement": "inline",
                     "payload_schema": ["NSDL DC 1.02.020"],
                     "node_timestamp": "2011-12-21T04:57:18.343124Z",
                     "digital_signature": {"key_location": ["http://pgp.mit.edu:11371/pks/lookup?op=get&search=0xE006035FD5EFEA67"],
                     "signing_method": "LR-PGP.1.0",
                     "signature": "-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA256\n\n316c7e1e9436cc45f5c2f0a1ba8d560adefb22e2ca4abf72fa5279267c88ac6e-----BEGIN PGP SIGNATURE-----\nVersion: BCPG v1.46\n\niQFdBAEBCABHBQJOt+/6QBxTbWl0aHNvbmlhbiBFZHVjYXRpb24gKFNtaXRoc29u\naWFuIEVkdWNhdGlvbikgPGxlYXJuaW5nQHNpLmVkdT4ACgkQ4AYDX9Xv6merCAf+\nPJQ6TX7jTo79a9XKhaSmFbYTgRz+D/uN9ksWJjsmvvoprqjMnsZBivD+3YDE/nTK\nttexx5Gy173Sj0wsojY4UPVezPmwbBjA2+2CG9btTKIsg3WwQpqzPeA/6LT46Ski\n2v3UbbGAMAU00ereuOjmdsqRZkXD/ABtZ/LYVMQCIqVMdR3aeQorHzuLlxTuzt/A\nMFxJb4A+a2jVw5nUM2Ry/x31Cb0pQ9uNO+jIWr8Xl3fjqiD5dUtySmVYvOEjEYcN\nh1twKySLmRWx0OfLN/Fnr1+N+sXT/s7lPCopKV3leEC2FOKDTjHhFM3mKUJvV4E+\ncXWLz6hBgEtIJlRuIj/o"},
                     "create_timestamp": "2011-11-07T14:51:07.137671Z",
                     "doc_version": "0.23.0",
                     "active": True,
                     "publishing_node": "cad60ef7493246868f6394fa764397c3",
                     "_id": "02d0f16e30184dccb64efd4ee63c7a45",
                     "doc_ID": "02d0f16e30184dccb64efd4ee63c7a45",
                     "identity": {"signer": "Smithsonian Education <learning@si.edu>",
                     "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                     "submitter_type": "agent",
                     "curator": "Smithsonian Education",
                     "owner": "Smithsonian American Art Museum"}}]}

        result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)
        assert(result['OK']), " Publish was not successfully"
        assert(result['document_results'][0]['OK'] == False), "Publish should have failed to on empty value for required field"
        assert('error' in result['document_results'][0] and
                  "Required value for 'resource_locator' cannot be an empty string" in result['document_results'][0]['error'])
        
