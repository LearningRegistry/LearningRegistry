from lr.tests import *
from lr.model import ResourceDataModel
from lr.util import decorators
from lr.util.decorators import make_gpg_keys
from lr.util.testdata import getTestDataForReplacement, getTestDataForMultipleResourceLocator
from lr.lib.schema_helper import TombstoneValidator, ResourceDataModelValidator
from lr.lib.signing import reloadGPGConfig
from time import sleep
from datetime import datetime
from pylons import config
import copy, couchdb, gnupg, json, re, uuid, socket
from LRSignature.sign.Sign  import Sign_0_21
from couchdb import Server
from functools import wraps
import tempfile, shutil

headers={'Content-Type': 'application/json'}

def _cmp_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

################################
## MOVED make_gpg_keys TO lr.util.decorators 
################################

# def backup(prop_list=[]):
#     backup = {}
#     for prop in prop_list:
#         backup[prop] = config["app_conf"][prop]
#     return backup

# def restore(backup={}):
#     config["app_conf"].update(backup)

# class make_gpg_keys(object):
#     '''decorator that makes at least 1 gpg key.  first key is set at the node key'''
#     def __init__(self, count=1):
#         self.count = count
#         self.gnupghome = tempfile.mkdtemp(prefix="gnupg_", dir=".")
#         self.gpgbin = "gpg"
#         self.gpg = gnupg.GPG(gnupghome=self.gnupghome, gpgbinary=self.gpgbin)
#         self.gpg.encoding = 'utf-8'
#         self.keys = []
        

#     def __call__(self, f):
#         @wraps(f)
#         def wrapped(*args, **kw):
#                 for i in range(self.count):
#                     cfg = {
#                         "key_type": "RSA",
#                         "key_length": 1024,
#                         "name_real": "Test Key #%d" % i,
#                         "name_comment": "Test key for %s" % f.__class__.__name__,
#                         "name_email": "test-%d@example.com" % i,
#                         "passphrase": "secret"
#                     }
#                     key = self.gpg.gen_key(self.gpg.gen_key_input(**cfg))
#                     assert key is not None, "GPG key not generated"
#                     assert key.fingerprint is not None, "Key missing fingerprint"

#                     cfg.update({
#                         "key": key,
#                         "fingerprint": key.fingerprint,
#                         "key_id": key.fingerprint[-16:],
#                         "locations": ["http://www.example.com/pubkey/%s" % key.fingerprint[-16:] ],
#                         "owner": "%s (%s)" % (cfg["name_real"], cfg["name_email"]) 
#                         })
#                     self.keys.append(cfg)

#                 kw["pgp_keys"] = self.keys
#                 kw["gnupghome"] = self.gnupghome
#                 kw["gpgbin"] = self.gpgbin
#                 kw["gpg"] = self.gpg

#                 backup_props = [
#                     "lr.publish.signing.privatekeyid",
#                     "lr.publish.signing.passphrase",
#                     "lr.publish.signing.gnupghome",
#                     "lr.publish.signing.gpgbin",
#                     "lr.publish.signing.publickeylocations",
#                     "lr.publish.signing.signer"
#                 ]
#                 backup_conf = backup(backup_props)

#                 config["app_conf"].update({
#                     "lr.publish.signing.privatekeyid": self.keys[0]["key_id"],
#                     "lr.publish.signing.passphrase": self.keys[0]["passphrase"],
#                     "lr.publish.signing.gnupghome": self.gnupghome,
#                     "lr.publish.signing.gpgbin": self.gpgbin,
#                     "lr.publish.signing.publickeylocations": '''["http://localhost/pubkey"]''',
#                     "lr.publish.signing.signer": self.keys[0]["owner"]
#                     })

#                 reloadGPGConfig(config["app_conf"])

#                 try:
#                     return f(*args, **kw)
#                 finally:
#                     shutil.rmtree(self.gnupghome)
#                     restore(backup_conf)
#                     reloadGPGConfig(config["app_conf"])

#         return wrapped



class TestMultiLocatorPublisherController(TestController):

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


        self.oauth_info2 = {
                "name": "tester2@example.com",
                "full_name": "Jane Tester"
        }

        self.oauth_user2 = {
           "_id": "org.couchdb.user:{0}".format(self.oauth_info2["name"]),
           "type": "user",
           "name": self.oauth_info2["name"],
           "roles": [
               "browserid"
           ],
           "browserid": True,
           "oauth": {
               "consumer_keys": {
                   self.oauth_info2["name"] : "XXX_ABC_consumer_key_123"
               },
               "tokens": {
                   "node_sign_token": "XXX_QWERTY_token_ASDFGH",
               }
           },
           "lrsignature": {
               "full_name": self.oauth_info2["full_name"]
           }
        }

        self.bauth_user = {
                "name": "mrbasicauth",
                "password": "ABC_123"
        }

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    @decorators.make_gpg_keys(1)
    def test_publish_multiple_resource_locator(self, *args, **kw):
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        docs = getTestDataForMultipleResourceLocator(3)

        assert len(docs) == 1, "Not enough test data."
        test_rd3 = docs[0]

        assert isinstance(test_rd3["resource_locator"], list) and len(test_rd3["resource_locator"]) > 0, "resource_locator isn't an array in the test data"

        key = kw["pgp_keys"][0]
        signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        signed_rd3 = signer.sign(test_rd3)
        data = { "documents": [signed_rd3] }
        result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
        for index, docResults in enumerate(result['document_results']):

            assert(docResults['OK'] == True), "Document did not publish for doc_ID: {0}".format(data['documents'][index]['doc_ID'])
            assert('doc_ID' in docResults), "Expected doc_ID: {0} in result.".format(data['documents'][index]['doc_ID'])  
            assert(docResults['doc_ID'] == signed_rd3["doc_ID"]), "Expected doc_id: {0}, got {1}".format(signed_rd3["doc_ID"], docResults['doc_ID'])          
            published_document = db[docResults['doc_ID']]
            assert published_document['digital_signature']['key_owner'] == signed_rd3['digital_signature']['key_owner'], "key_owner doesn't match"
            assert published_document['digital_signature']['signature'] == signed_rd3['digital_signature']['signature'], "signature doesn't match"
            assert published_document['resource_locator'] == signed_rd3['resource_locator'], "resource_locator's don't match."
            ResourceDataModelValidator.validate_model(published_document)


class TestReplacementDocsController(TestController):
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


        self.oauth_info2 = {
                "name": "tester2@example.com",
                "full_name": "Jane Tester"
        }

        self.oauth_user2 = {
           "_id": "org.couchdb.user:{0}".format(self.oauth_info2["name"]),
           "type": "user",
           "name": self.oauth_info2["name"],
           "roles": [
               "browserid"
           ],
           "browserid": True,
           "oauth": {
               "consumer_keys": {
                   self.oauth_info2["name"] : "XXX_ABC_consumer_key_123"
               },
               "tokens": {
                   "node_sign_token": "XXX_QWERTY_token_ASDFGH",
               }
           },
           "lrsignature": {
               "full_name": self.oauth_info2["full_name"]
           }
        }

        self.bauth_user = {
                "name": "mrbasicauth",
                "password": "ABC_123"
        }

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    @decorators.make_gpg_keys(1)
    def test_publish_replacement_with_delete(self, **kw):
        '''test_publish_replacement_with_delete: publishes 3 documents, doc 1 ordinary, doc 2 is a replacment, doc 3 is a delete replacment.'''
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        docs = getTestDataForReplacement(3, True)

        assert len(docs) == 3, "Not enough test data."

        key = kw["pgp_keys"][0]
        signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        replacements = []

        for rd3 in docs:

            signed_rd3 = signer.sign(rd3)
            replacements.append(signed_rd3)

            data = { "documents": [signed_rd3] }
            result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):

                assert(docResults['OK'] == True), "Document did not publish for doc_ID: {0}".format(data['documents'][index]['doc_ID'])
                assert('doc_ID' in docResults), "Expected doc_ID: {0} in result.".format(data['documents'][index]['doc_ID'])  
                assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                published_document = db[docResults['doc_ID']]
                assert published_document['digital_signature']['key_owner'] == replacements[-1]['digital_signature']['key_owner'], "key_owner doesn't match"
                assert published_document['digital_signature']['signature'] == replacements[-1]['digital_signature']['signature'], "signature doesn't match"

                if "replaces" in published_document:
                    for repl_doc_id in published_document["replaces"]:
                        repl_doc = db[repl_doc_id]

                        TombstoneValidator.validate_model(repl_doc)

                        assert repl_doc["replaced_by"]["doc_ID"] == published_document["doc_ID"], "Tombstone has wrong replacement doc_ID."


    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    @decorators.make_gpg_keys(1)
    def test_publish_replacement_docs(self, **kw):
        '''test_publish_replacement_docs: publishes 10 docs. each subsequent doc replaces the previous.
           the first document published is version 0.23.0'''
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        def gen_doc_id():
            base_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
            rev = 0
            while True:
                yield "%s-%d" % (base_doc_id, rev)
                rev += 1
        doc_id = gen_doc_id();
          
        base_rd3 = {
            'TOS': {
                      'submission_attribution': 'Example', 
                      'submission_TOS': 'http://example.com/terms'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'identity': {
                'submitter': 'Test Agent', 
                'submitter_type': 'agent'
            }, 
            'doc_type': 'resource_data', 
            'resource_data': {
                "testing":"data", 
                "version":0
            },
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://example.com/schema/locator', 
            'payload_schema': ['example'], 
            'doc_version': '0.23.0'
        }

        key = kw["pgp_keys"][0]

        signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        replacements = []
        for i in range(10):
            rd3 = copy.deepcopy(base_rd3)
            new_id = doc_id.next()
            rd3.update({
                    "doc_ID": new_id,
                    "resource_data": {
                        "testing": "data",
                        "version": i
                    }
                })
            if len(replacements) > 0:
                rd3["replaces"] = [ replacements[-1]["doc_ID"] ]
                rd3["doc_version"] = '0.49.0'

            signed_rd3 = signer.sign(rd3)

            replacements.append(signed_rd3)

            data = { "documents": [signed_rd3] }

            result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):
                assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
                assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
                assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                published_document = db[docResults['doc_ID']]
                assert published_document['digital_signature']['key_owner'] == replacements[-1]['digital_signature']['key_owner'], "key_owner doesn't match"
                assert published_document['digital_signature']['signature'] == replacements[-1]['digital_signature']['signature'], "signature doesn't match"

                if "replaces" in published_document:
                    for repl_doc_id in published_document["replaces"]:
                        repl_doc = db[repl_doc_id]

                        TombstoneValidator.validate_model(repl_doc)

                        assert repl_doc["replaced_by"]["doc_ID"] == published_document["doc_ID"], "Tombstone has wrong replacement doc_ID."
  
    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
    @decorators.make_gpg_keys(1)
    @decorators.OAuthRequest(path="/publish", http_method="POST")
    def test_publish_proxy_signed_replacement_docs(self, **kw):
        '''test_publish_proxy_signed_replacement_docs: publishes 10 documents by proxy signing. subsequent documents
           are published to replace the previous document.'''
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        def gen_doc_id():
            base_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
            rev = 0
            while True:
                yield "%s-%d" % (base_doc_id, rev)
                rev += 1
        doc_id = gen_doc_id();
          
        base_rd3 = {
            'TOS': {
                      'submission_attribution': 'Example', 
                      'submission_TOS': 'http://example.com/terms'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'doc_type': 'resource_data', 
            'resource_data': {
                "testing":"data", 
                "version":0
            },
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://example.com/schema/locator', 
            'payload_schema': ['example'], 
            'doc_version': '0.23.0'
        }

        key = kw["pgp_keys"][0]
        gpg = kw["gpg"]

        # signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        replacements = []
        for i in range(10):
            rd3 = copy.deepcopy(base_rd3)
            new_id = doc_id.next()
            rd3.update({
                    "doc_ID": new_id,
                    "resource_data": {
                        "testing": "data",
                        "version": i
                    }
                })
            if len(replacements) > 0:
                rd3["replaces"] = [ replacements[-1]["doc_ID"] ]
                rd3["doc_version"] = '0.49.0'

            # signed_rd3 = signer.sign(rd3)

            replacements.append(rd3)

            data = { "documents": [rd3] }

            h={}
            h.update(headers)
            h.update(self.oauth.header)

            result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)

            # result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):
                assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
                assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
                assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                published_document = db[docResults['doc_ID']]
                assert published_document['identity']['signer'] == key['owner'], "unexpected signer."
                
                v = gpg.verify(published_document['digital_signature']['signature'])
                assert v.fingerprint == key["fingerprint"], "signature does not use node key."

                if "replaces" in published_document:
                    for repl_doc_id in published_document["replaces"]:
                        repl_doc = db[repl_doc_id]

                        TombstoneValidator.validate_model(repl_doc)

                        assert repl_doc["replaced_by"]["doc_ID"] == published_document["doc_ID"], "Tombstone has wrong replacement doc_ID."

    
    @decorators.OAuthRequest(path="/publish", http_method="POST", oauth_user_attrib="oauth_user")
    def publish_user_1(self, data):
        h={}
        h.update(headers)
        h.update(self.oauth.header)

        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        return result

    @decorators.OAuthRequest(path="/publish", http_method="POST", oauth_user_attrib="oauth_user2")
    def publish_user_2(self, data):
        h={}
        h.update(headers)
        h.update(self.oauth.header)

        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        return result

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
    @decorators.make_gpg_keys(1)
    def test_multi_user_publish_proxy_signed_replacement_docs(self, **kw):
        '''test_multi_user_publish_proxy_signed_replacement_docs: publishes 2 documents by proxy signing with different users. second document
           published attempts to replace the previous document, however should fail in replacement AND in publishing.'''
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]


        def gen_doc_id():
            base_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
            rev = 0
            while True:
                yield "%s-%d" % (base_doc_id, rev)
                rev += 1
        doc_id = gen_doc_id();
          
        base_rd3 = {
            'TOS': {
                      'submission_attribution': 'Example', 
                      'submission_TOS': 'http://example.com/terms'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'doc_type': 'resource_data', 
            'resource_data': {
                "testing":"data", 
                "version":0
            },
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://example.com/schema/locator', 
            'payload_schema': ['example'], 
            'doc_version': '0.49.0'
        }

        key = kw["pgp_keys"][0]
        gpg = kw["gpg"]

        # signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        publish_it = [
            self.publish_user_1,
            self.publish_user_2
        ]

        replacements = []
        for i in range(2):
            rd3 = copy.deepcopy(base_rd3)
            new_id = doc_id.next()
            rd3.update({
                    "doc_ID": new_id,
                    "resource_data": {
                        "testing": "data",
                        "version": i
                    }
                })
            if len(replacements) > 0:
                rd3["replaces"] = [ replacements[-1]["doc_ID"] ]
                rd3["doc_version"] = '0.49.0'

            # signed_rd3 = signer.sign(rd3)

            replacements.append(rd3)

            data = { "documents": [rd3] }

            result = publish_it[i](data)

            # h={}
            # h.update(headers)
            # h.update(self.oauth.header)

            # result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)

            # result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):
                
                if "replaces" not in data['documents'][index]:
                    assert(docResults['OK'] == True), "Publish should succeed for doc_ID {0}".format(data['documents'][index]['doc_ID'])
                    assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
                    assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                    published_document = db[docResults['doc_ID']]
                    
                    ResourceDataModelValidator.validate_model(published_document)

                    assert published_document['identity']['signer'] == key['owner'], "unexpected signer."
                    
                    v = gpg.verify(published_document['digital_signature']['signature'])
                    assert v.fingerprint == key["fingerprint"], "signature does not use node key."

                elif "replaces" in data['documents'][index]:
                    assert(docResults['OK'] == False), "Publish should fail for doc_ID {0}".format(data['documents'][index]['doc_ID'])
                    for repl_doc_id in data['documents'][index]["replaces"]:
                        repl_doc = db[repl_doc_id]

                        ResourceDataModelValidator.validate_model(repl_doc)

                        # assert repl_doc["replaced_by"]["doc_ID"] == published_document["doc_ID"], "Tombstone has wrong replacement doc_ID."



    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    @decorators.make_gpg_keys(1)
    def test_publish_resource_over_tombstone(self, **kw):
        '''test_publish_resource_over_tombstone: This creates a resource, tombstones it with a replacement, then tries to publish a resource
           with the same doc_ID as the tombstoned resource, which is expected to fail.'''
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        def gen_doc_id():
            base_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
            rev = 0
            while True:
                yield "%s-%d" % (base_doc_id, rev)
                rev += 1
        doc_id = gen_doc_id();
          
        base_rd3 = {
            'TOS': {
                      'submission_attribution': 'Example', 
                      'submission_TOS': 'http://example.com/terms'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'identity': {
                'submitter': 'Test Agent', 
                'submitter_type': 'agent'
            }, 
            'doc_type': 'resource_data', 
            'resource_data': {
                "testing":"data", 
                "version":0
            },
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://example.com/schema/locator', 
            'payload_schema': ['example'], 
            'doc_version': '0.23.0'
        }

        key = kw["pgp_keys"][0]

        signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        replacements = []
        for i in range(2):
            rd3 = copy.deepcopy(base_rd3)
            new_id = doc_id.next()
            rd3.update({
                    "doc_ID": new_id,
                    "resource_data": {
                        "testing": "data",
                        "version": i
                    }
                })
            if len(replacements) > 0:
                rd3["replaces"] = [ replacements[-1]["doc_ID"] ]
                rd3["doc_version"] = '0.49.0'

            signed_rd3 = signer.sign(rd3)

            replacements.append(signed_rd3)

            data = { "documents": [signed_rd3] }


            result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):
                assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
                assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
                assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                published_document = db[docResults['doc_ID']]
                assert published_document['digital_signature']['key_owner'] == replacements[-1]['digital_signature']['key_owner'], "key_owner doesn't match"
                assert published_document['digital_signature']['signature'] == replacements[-1]['digital_signature']['signature'], "signature doesn't match"

                if "replaces" in published_document:
                    for repl_doc_id in published_document["replaces"]:
                        repl_doc = db[repl_doc_id]

                        TombstoneValidator.validate_model(repl_doc)

                        assert repl_doc["replaced_by"]["doc_ID"] == published_document["doc_ID"], "Tombstone has wrong replacement doc_ID."

        data = { "documents": replacements[0:1] }
        result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
        for index, docResults in enumerate(result['document_results']):
            # import pdb; pdb.set_trace()
            assert(docResults['OK'] == False), "Publish should not have succeeded for doc_ID: {0}.".format(data['documents'][index]['doc_ID'])      
            
            published_document = db[data['documents'][index]['doc_ID']]

            TombstoneValidator.validate_model(published_document)


    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    @decorators.make_gpg_keys(1)
    def test_publish_replacement_existing_tombstone(self, **kw):
        '''test_publish_replacement_existing_tombstone: publishes 1 resource, 2 updates.  1st update should successfully tombstone the first, and the second should
           try to tombstone both 1 and 2, however should fail on first, succeed on second'''

        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        def gen_doc_id():
            base_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
            rev = 0
            while True:
                yield "%s-%d" % (base_doc_id, rev)
                rev += 1
        doc_id = gen_doc_id();
          
        base_rd3 = {
            'TOS': {
                      'submission_attribution': 'Example', 
                      'submission_TOS': 'http://example.com/terms'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'identity': {
                'submitter': 'Test Agent', 
                'submitter_type': 'agent'
            }, 
            'doc_type': 'resource_data', 
            'resource_data': {
                "testing":"data", 
                "version":0
            },
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://example.com/schema/locator', 
            'payload_schema': ['example'], 
            'doc_version': '0.23.0'
        }

        key = kw["pgp_keys"][0]

        signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

        replacements = []
        tombstoned_by = { }
        for i in range(5):
            rd3 = copy.deepcopy(base_rd3)
            new_id = doc_id.next()
            rd3.update({
                    "doc_ID": new_id,
                    "resource_data": {
                        "testing": "data",
                        "version": i
                    }
                })

            # tombstone all previous docs
            if len(replacements) > 0:
                rd3["replaces"] = map(lambda x: x["doc_ID"], replacements)
                rd3["doc_version"] = '0.49.0'
                tombstoned_by[replacements[-1]["doc_ID"]] = rd3["doc_ID"]

            signed_rd3 = signer.sign(rd3)

            replacements.append(signed_rd3)

            data = { "documents": [signed_rd3] }

            result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):
                assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
                assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
                assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                published_document = db[docResults['doc_ID']]
                assert published_document['digital_signature']['key_owner'] == replacements[-1]['digital_signature']['key_owner'], "key_owner doesn't match"
                assert published_document['digital_signature']['signature'] == replacements[-1]['digital_signature']['signature'], "signature doesn't match"

                if "replaces" in published_document:
                    for pos, repl_doc_id in enumerate(published_document["replaces"]):
                        repl_doc = db[repl_doc_id]

                        TombstoneValidator.validate_model(repl_doc)

                        if pos < (len(published_document["replaces"])-1):
                            assert repl_doc["replaced_by"]["doc_ID"] != tombstoned_by[repl_doc["doc_ID"]], "Tombstone was expected to be set by some other doc_ID."
                        else:
                            assert repl_doc["replaced_by"]["doc_ID"] == tombstoned_by[repl_doc["doc_ID"]], "Tombstone was expected to have been set by the replacement."
                          

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    @decorators.make_gpg_keys(2)
    def test_publish_replacement_conflict(self, **kw):
        '''test_publish_replacement_conflict: Publish 2 documents each signed with different keys. The 
           second document tries to replace the first, which should fail, however the first document is
           permited to be published'''
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        def gen_doc_id():
            base_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
            rev = 0
            while True:
                yield "%s-%d" % (base_doc_id, rev)
                rev += 1
        doc_id = gen_doc_id();
          
        base_rd3 = {
            'TOS': {
                      'submission_attribution': 'Example', 
                      'submission_TOS': 'http://example.com/terms'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'identity': {
                'submitter': 'Test Agent', 
                'submitter_type': 'agent'
            }, 
            'doc_type': 'resource_data', 
            'resource_data': {
                "testing":"data", 
                "version":0
            },
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://example.com/schema/locator', 
            'payload_schema': ['example'], 
            'doc_version': '0.49.0'
        }

        replacements = []
        for i in range(2):
            key = kw["pgp_keys"][i]

            signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])

            rd3 = copy.deepcopy(base_rd3)
            new_id = doc_id.next()
            rd3.update({
                    "doc_ID": new_id,
                    "resource_data": {
                        "testing": "data",
                        "version": i
                    }
                })
            if len(replacements) > 0:
                rd3["replaces"] = [ replacements[-1]["doc_ID"] ]
                rd3["doc_version"] = '0.49.0'

            signed_rd3 = signer.sign(rd3)

            last_id = new_id
            replacements.append(signed_rd3)

            data = { "documents": [signed_rd3] }

            result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)

            assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
            for index, docResults in enumerate(result['document_results']):
                assert(docResults['OK'] == True), "Publish should work for doc_ID {0}".format(data['documents'][index]['doc_ID'])
                assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
                assert(docResults['doc_ID'] == replacements[-1]["doc_ID"]), "Expected doc_id: {0}, got {1}".format(replacements[-1]["doc_ID"], docResults['doc_ID'])          
                published_document = db[docResults['doc_ID']]
                assert published_document['digital_signature']['key_owner'] == replacements[-1]['digital_signature']['key_owner'], "key_owner doesn't match"
                assert published_document['digital_signature']['signature'] == replacements[-1]['digital_signature']['signature'], "signature doesn't match"

                if "replaces" in published_document:
                    for repl_doc_id in published_document["replaces"]:
                        repl_doc = db[repl_doc_id]
                        
                        ## since the replacement is invalid (uses different signing key, no tombstone should have been)
                        ResourceDataModelValidator.validate_model(repl_doc)





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

        self.bauth_user = {
                "name": "mrbasicauth",
                "password": "ABC_123"
        }          


    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    def test_publish_specified_doc_id(self):
        known_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
        document = {
            'update_timestamp': '2011-11-07T14:51:07.137671Z',
            'TOS': {
                      'submission_attribution': 'Smithsonian Education', 
                      'submission_TOS': 'http://si.edu/Termsofuse'
                    }, 
            'payload_placement': 'inline', 
            'active': True, 
            'resource_locator': 'http://example.com', 
            'digital_signature': {
                'key_location': ['http://www.example.com/key'], 
                'key_owner': u'walt grata <wegrata@gmail.com>', 
                'signing_method': 'LR-PGP.1.0', 
                'signature': '-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n\n-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.11 (GNU/Linux)\n\niQEcBAEBAgAGBQJQUzHaAAoJEMNbqtmn2aps0CwH/j63/T2tkLv2dCp3cU7vlPwG\n/vmi0Bq3dDvXOVDkFobY3mQcXxsLjExtN2PKKjqYZ+KWdLfOq36/77QAI7VOQ1+r\nXy3b7aWGMYEjtRmAUcO9Ov39aj2OCGZ8k2aPDhvL968v89X7B1v53wD1wi7+Lges\n1WfAfEyXrnWIVBNubNtuazLA4322K+CAI4bvYiecz4cw7J51xlhf7dacCZb+wts3\n+q1HxTMg3fIQ3l3Xd3SyHc48jXqyBlFpLr56UR0thwRC54fICgd/gEnebSbfVRXQ\nqAZXP6lF7/C9/m3ZDDjvV+vkQCmLLg8LMn7WStenJR1tB+KE/6MTVcY6JOucZIo=\n=DhqM\n-----END PGP SIGNATURE-----\n'
            }, 
            'identity': {
                'signer': 'Smithsonian Education <learning@si.edu>', 
                'submitter': 'Brokers of Expertise on behalf of Smithsonian Education', 
                'submitter_type': 'agent', 
                'curator': 'Smithsonian Education', 
                'owner': 'Smithsonian American Art Museum'
            }, 
            'doc_type': 'resource_data', 
            'resource_data': '\n<nsdl_dc:nsdl_dc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n xmlns:dc="http://purl.org/dc/elements/1.1/"\n xmlns:dct="http://purl.org/dc/terms/"\n xmlns:ieee="http://www.ieee.org/xsd/LOMv1p0"\n xmlns:nsdl_dc="http://ns.nsdl.org/nsdl_dc_v1.02/"\n schemaVersion="1.02.020"\n xsi:schemaLocation="http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd">\n <dc:identifier xsi:type="dct:URI">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type="nsdl_dc:NSDLAccess">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>', 
            'resource_data_type': 'metadata', 
            'payload_schema_locator': 'http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd', 
            'payload_schema': ['NSDL DC 1.02.020'], 
            'doc_version': '0.23.0'
        }
        document["doc_ID"] = known_doc_id
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        data = {
            "documents": 
                    [document]
                }


        result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=headers).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])  
            assert(docResults['doc_ID'] == known_doc_id), "Expected doc_id: {0}, got {1}".format(known_doc_id, docResults['doc_ID'])          
            published_document = db[docResults['doc_ID']]
            assert published_document['digital_signature']['key_owner'] == document['digital_signature']['key_owner'], "key_owner doesn't match"
            assert published_document['digital_signature']['signature'] == document['digital_signature']['signature'], "signature doesn't match"


    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
    @decorators.OAuthRequest(path="/publish", http_method="POST")
    def test_auto_signature_dont_sign_specified_doc_id(self):
        known_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
        document = {'update_timestamp': '2011-11-07T14:51:07.137671Z',
                    'TOS': {
                              'submission_attribution': 'Smithsonian Education', 
                              'submission_TOS': 'http://si.edu/Termsofuse'
                            }, 
                            'payload_placement': 'inline', 
                            'active': True, 
                            'resource_locator': 'http://example.com', 
                            'digital_signature': {
                                'key_location': ['http://www.example.com/key'], 
                                'key_owner': u'walt grata <wegrata@gmail.com>', 
                                'signing_method': 'LR-PGP.1.0', 
                                'signature': '-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n\n-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.11 (GNU/Linux)\n\niQEcBAEBAgAGBQJQUzHaAAoJEMNbqtmn2aps0CwH/j63/T2tkLv2dCp3cU7vlPwG\n/vmi0Bq3dDvXOVDkFobY3mQcXxsLjExtN2PKKjqYZ+KWdLfOq36/77QAI7VOQ1+r\nXy3b7aWGMYEjtRmAUcO9Ov39aj2OCGZ8k2aPDhvL968v89X7B1v53wD1wi7+Lges\n1WfAfEyXrnWIVBNubNtuazLA4322K+CAI4bvYiecz4cw7J51xlhf7dacCZb+wts3\n+q1HxTMg3fIQ3l3Xd3SyHc48jXqyBlFpLr56UR0thwRC54fICgd/gEnebSbfVRXQ\nqAZXP6lF7/C9/m3ZDDjvV+vkQCmLLg8LMn7WStenJR1tB+KE/6MTVcY6JOucZIo=\n=DhqM\n-----END PGP SIGNATURE-----\n'
                                }, 
                                'identity': {
                                    'signer': 'Smithsonian Education <learning@si.edu>', 
                                    'submitter': 'Brokers of Expertise on behalf of Smithsonian Education', 
                                    'submitter_type': 'agent', 
                                    'curator': 'Smithsonian Education', 
                                    'owner': 'Smithsonian American Art Museum'
                                }, 
                                'doc_type': 'resource_data', 
                                'resource_data': '\n<nsdl_dc:nsdl_dc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n xmlns:dc="http://purl.org/dc/elements/1.1/"\n xmlns:dct="http://purl.org/dc/terms/"\n xmlns:ieee="http://www.ieee.org/xsd/LOMv1p0"\n xmlns:nsdl_dc="http://ns.nsdl.org/nsdl_dc_v1.02/"\n schemaVersion="1.02.020"\n xsi:schemaLocation="http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd">\n <dc:identifier xsi:type="dct:URI">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type="nsdl_dc:NSDLAccess">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>', 
                                'resource_data_type': 'metadata', 
                                'payload_schema_locator': 'http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd', 
                                'payload_schema': ['NSDL DC 1.02.020'], 
                                'doc_version': '0.23.0'}
        document["doc_ID"] = known_doc_id
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]
        data = {
            "documents": 
                    [document]
                }
        h={}
        h.update(headers)
        h.update(self.oauth.header)

        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])            
            assert(docResults['doc_ID'] == known_doc_id), "Expected doc_id: {0}, got {1}".format(known_doc_id, docResults['doc_ID'])          
            published_document = db[docResults['doc_ID']]
            assert published_document['digital_signature']['key_owner'] == document['digital_signature']['key_owner'], "key_owner doesn't match"
            assert published_document['digital_signature']['signature'] == document['digital_signature']['signature'], "signature doesn't match"

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
    @decorators.OAuthRequest(path="/publish", http_method="POST")
    def test_auto_signature_specify_doc_id(self):
        known_doc_id = 'urn:{domain}:nosetest:{uuid}'.format(domain=socket.gethostname(), uuid=uuid.uuid1())
        document = {'update_timestamp': '2011-11-07T14:51:07.137671Z',
                    'TOS': {
                              'submission_attribution': 'Smithsonian Education', 
                              'submission_TOS': 'http://si.edu/Termsofuse'
                            }, 
                            'payload_placement': 'inline', 
                            'active': True, 
                            'resource_locator': 'http://example.com', 
                                'identity': {
                                    'signer': 'Smithsonian Education <learning@si.edu>', 
                                    'submitter': 'Brokers of Expertise on behalf of Smithsonian Education', 
                                    'submitter_type': 'agent', 
                                    'curator': 'Smithsonian Education', 
                                    'owner': 'Smithsonian American Art Museum'
                                }, 
                                'doc_type': 'resource_data', 
                                'resource_data': '\n<nsdl_dc:nsdl_dc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n xmlns:dc="http://purl.org/dc/elements/1.1/"\n xmlns:dct="http://purl.org/dc/terms/"\n xmlns:ieee="http://www.ieee.org/xsd/LOMv1p0"\n xmlns:nsdl_dc="http://ns.nsdl.org/nsdl_dc_v1.02/"\n schemaVersion="1.02.020"\n xsi:schemaLocation="http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd">\n <dc:identifier xsi:type="dct:URI">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type="nsdl_dc:NSDLAccess">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>', 
                                'resource_data_type': 'metadata', 
                                'payload_schema_locator': 'http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd', 
                                'payload_schema': ['NSDL DC 1.02.020'], 
                                'doc_version': '0.23.0'}
        document["doc_ID"] = known_doc_id
        data = {
            "documents": 
                    [document]
                }
        h={}
        h.update(headers)
        h.update(self.oauth.header)
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]
        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        assert(len(result['document_results']) == 1), "Expected 1 result and got {0}".format(len(result['document_results']))
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])            
            assert(docResults['doc_ID'] == known_doc_id), "Expected doc_id: {0}, got {1}".format(known_doc_id, docResults['doc_ID'])          
            published_document = db[docResults['doc_ID']]
            assert 'digital_signature' in published_document
            assert 'signature' in published_document['digital_signature']

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
    @decorators.OAuthRequest(path="/publish", http_method="POST")
    def test_auto_signature_dont_sign(self):
        document = {'update_timestamp': '2011-11-07T14:51:07.137671Z',
                    'TOS': {
                              'submission_attribution': 'Smithsonian Education', 
                              'submission_TOS': 'http://si.edu/Termsofuse'
                            }, 
                            'payload_placement': 'inline', 
                            'active': True, 
                            'resource_locator': 'http://example.com', 
                            'digital_signature': {
                                'key_location': ['http://www.example.com/key'], 
                                'key_owner': u'walt grata <wegrata@gmail.com>', 
                                'signing_method': 'LR-PGP.1.0', 
                                'signature': '-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n\n-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.11 (GNU/Linux)\n\niQEcBAEBAgAGBQJQUzHaAAoJEMNbqtmn2aps0CwH/j63/T2tkLv2dCp3cU7vlPwG\n/vmi0Bq3dDvXOVDkFobY3mQcXxsLjExtN2PKKjqYZ+KWdLfOq36/77QAI7VOQ1+r\nXy3b7aWGMYEjtRmAUcO9Ov39aj2OCGZ8k2aPDhvL968v89X7B1v53wD1wi7+Lges\n1WfAfEyXrnWIVBNubNtuazLA4322K+CAI4bvYiecz4cw7J51xlhf7dacCZb+wts3\n+q1HxTMg3fIQ3l3Xd3SyHc48jXqyBlFpLr56UR0thwRC54fICgd/gEnebSbfVRXQ\nqAZXP6lF7/C9/m3ZDDjvV+vkQCmLLg8LMn7WStenJR1tB+KE/6MTVcY6JOucZIo=\n=DhqM\n-----END PGP SIGNATURE-----\n'
                                }, 
                                'identity': {
                                    'signer': 'Smithsonian Education <learning@si.edu>', 
                                    'submitter': 'Brokers of Expertise on behalf of Smithsonian Education', 
                                    'submitter_type': 'agent', 
                                    'curator': 'Smithsonian Education', 
                                    'owner': 'Smithsonian American Art Museum'
                                }, 
                                'doc_type': 'resource_data', 
                                'resource_data': '\n<nsdl_dc:nsdl_dc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n xmlns:dc="http://purl.org/dc/elements/1.1/"\n xmlns:dct="http://purl.org/dc/terms/"\n xmlns:ieee="http://www.ieee.org/xsd/LOMv1p0"\n xmlns:nsdl_dc="http://ns.nsdl.org/nsdl_dc_v1.02/"\n schemaVersion="1.02.020"\n xsi:schemaLocation="http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd">\n <dc:identifier xsi:type="dct:URI">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type="nsdl_dc:NSDLAccess">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>', 
                                'resource_data_type': 'metadata', 
                                'payload_schema_locator': 'http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd', 
                                'payload_schema': ['NSDL DC 1.02.020'], 
                                'doc_version': '0.23.0'}
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]
        data = {
            "documents": 
                    [document]
                }
        h={}
        h.update(headers)
        h.update(self.oauth.header)

        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])            
            published_document = db[docResults['doc_ID']]
            assert published_document['digital_signature']['key_owner'] == document['digital_signature']['key_owner'], "key_owner doesn't match"
            assert published_document['digital_signature']['signature'] == document['digital_signature']['signature'], "signature doesn't match"
            assert published_document['identity']['signer'] == document['identity']['signer'], "signer doesn't match"

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
    @decorators.OAuthRequest(path="/publish", http_method="POST")
    def test_auto_signature(self):
        document = {'update_timestamp': '2011-11-07T14:51:07.137671Z',
                    'TOS': {
                              'submission_attribution': 'Smithsonian Education', 
                              'submission_TOS': 'http://si.edu/Termsofuse'
                            }, 
                            'payload_placement': 'inline', 
                            'active': True, 
                            'resource_locator': 'http://example.com', 
                                'identity': {
                                    'signer': 'Smithsonian Education <learning@si.edu>', 
                                    'submitter': 'Brokers of Expertise on behalf of Smithsonian Education', 
                                    'submitter_type': 'agent', 
                                    'curator': 'Smithsonian Education', 
                                    'owner': 'Smithsonian American Art Museum'
                                }, 
                                'doc_type': 'resource_data', 
                                'resource_data': '\n<nsdl_dc:nsdl_dc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n xmlns:dc="http://purl.org/dc/elements/1.1/"\n xmlns:dct="http://purl.org/dc/terms/"\n xmlns:ieee="http://www.ieee.org/xsd/LOMv1p0"\n xmlns:nsdl_dc="http://ns.nsdl.org/nsdl_dc_v1.02/"\n schemaVersion="1.02.020"\n xsi:schemaLocation="http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd">\n <dc:identifier xsi:type="dct:URI">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type="nsdl_dc:NSDLAccess">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>', 
                                'resource_data_type': 'metadata', 
                                'payload_schema_locator': 'http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd', 
                                'payload_schema': ['NSDL DC 1.02.020'], 
                                'doc_version': '0.23.0'}
        data = {
            "documents": 
                    [document]
                }
        h={}
        h.update(headers)
        h.update(self.oauth.header)
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]
        result = json.loads(self.app.post(self.oauth.path, params=json.dumps(data), headers=h, extra_environ=self.oauth.env).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])            
            published_document = db[docResults['doc_ID']]
            assert 'digital_signature' in published_document
            assert 'signature' in published_document['digital_signature']


    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=True, oauth=False))
    @decorators.BasicAuthRequest(bauth_user_attrib="bauth_user", bauth_info_attrib="bauth")
    def test_auto_signature_dont_sign_basic(self):
        document = {'update_timestamp': '2011-11-07T14:51:07.137671Z',
                    'TOS': {
                              'submission_attribution': 'Smithsonian Education',
                              'submission_TOS': 'http://si.edu/Termsofuse'
                            },
                            'payload_placement': 'inline',
                            'active': True,
                            'resource_locator': 'http://example.com',
                            'digital_signature': {
                                'key_location': ['http://www.example.com/key'],
                                'key_owner': u'walt grata <wegrata@gmail.com>',
                                'signing_method': 'LR-PGP.1.0',
                                'signature': '-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n\n-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.11 (GNU/Linux)\n\niQEcBAEBAgAGBQJQUzHaAAoJEMNbqtmn2aps0CwH/j63/T2tkLv2dCp3cU7vlPwG\n/vmi0Bq3dDvXOVDkFobY3mQcXxsLjExtN2PKKjqYZ+KWdLfOq36/77QAI7VOQ1+r\nXy3b7aWGMYEjtRmAUcO9Ov39aj2OCGZ8k2aPDhvL968v89X7B1v53wD1wi7+Lges\n1WfAfEyXrnWIVBNubNtuazLA4322K+CAI4bvYiecz4cw7J51xlhf7dacCZb+wts3\n+q1HxTMg3fIQ3l3Xd3SyHc48jXqyBlFpLr56UR0thwRC54fICgd/gEnebSbfVRXQ\nqAZXP6lF7/C9/m3ZDDjvV+vkQCmLLg8LMn7WStenJR1tB+KE/6MTVcY6JOucZIo=\n=DhqM\n-----END PGP SIGNATURE-----\n'
                                },
                                'identity': {
                                    'signer': 'Smithsonian Education <learning@si.edu>',
                                    'submitter': 'Brokers of Expertise on behalf of Smithsonian Education',
                                    'submitter_type': 'agent',
                                    'curator': 'Smithsonian Education',
                                    'owner': 'Smithsonian American Art Museum'
                                },
                                'doc_type': 'resource_data',
                                'resource_data': '\n<nsdl_dc:nsdl_dc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n xmlns:dc="http://purl.org/dc/elements/1.1/"\n xmlns:dct="http://purl.org/dc/terms/"\n xmlns:ieee="http://www.ieee.org/xsd/LOMv1p0"\n xmlns:nsdl_dc="http://ns.nsdl.org/nsdl_dc_v1.02/"\n schemaVersion="1.02.020"\n xsi:schemaLocation="http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd">\n <dc:identifier xsi:type="dct:URI">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type="nsdl_dc:NSDLAccess">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>',
                                'resource_data_type': 'metadata',
                                'payload_schema_locator': 'http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd',
                                'payload_schema': ['NSDL DC 1.02.020'],
                                'doc_version': '0.23.0'}
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]
        data = {
            "documents":
                    [document]
                }
        h = {}
        h.update(headers)
        h.update(self.bauth.header)

        result = json.loads(self.app.post('/publish', params=json.dumps(data), headers=h).body)
        assert(result['OK']), self._PUBLISH_UNSUCCESSFUL_MSG
        for index, docResults in enumerate(result['document_results']):
            assert(docResults['OK'] == True), "Publish should work for doc version {0}".format(data['documents'][index]['doc_version'])
            assert('doc_ID' in docResults), "Publish should return doc_ID for doc version {0}".format(data['documents'][index]['doc_version'])
            published_document = db[docResults['doc_ID']]
            assert published_document['digital_signature']['key_owner'] == document['digital_signature']['key_owner'], "key_owner doesn't match"
            assert published_document['digital_signature']['signature'] == document['digital_signature']['signature'], "signature doesn't match"


    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz(basicauth=False, oauth=True))
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
                        {
                            "doc_type": "resource_data",
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
                            "doc_version": "0.49.0",
                            "active": True,
                            "identity": {
                                "signer": "Smithsonian Education <learning@si.edu>",
                                "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                                "submitter_type": "agent",
                                "curator": "Smithsonian Education",
                                "owner": "Smithsonian American Art Museum"
                            },
                            "replaces": ["someDocId"]
                        }
                        
                        #
                        # Deprecating support of pre - 0.23.0 documents.
                        #

                        # {"doc_type": "resource_data",
                        # "resource_locator": "http://example.com/1",
                        #  "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                        #  "TOS": {"submission_attribution": "Smithsonian Education",
                        #  "submission_TOS": "http://si.edu/Termsofuse"},
                        #  "resource_data_type": "metadata",
                        #  "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                        #  "payload_placement": "inline",
                        #  "payload_schema": ["NSDL DC 1.02.020"],
                        #  "create_timestamp": "2011-11-07T14:51:07.137671Z",
                        #  "doc_version": "0.21.0",
                        #  "active": True,
                        #  "identity": {
                        #         "signer": "Smithsonian Education <learning@si.edu>",
                        #         "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                        #         "submitter_type": "agent",
                        #         "curator": "Smithsonian Education",
                        #         "owner": "Smithsonian American Art Museum"
                        #         }
                        # },
                        
                        # {
                        # "doc_type": "resource_data",
                        # "resource_locator": "http://example.com/2",
                        #  "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                        #  "TOS": {"submission_attribution": "Smithsonian Education",
                        #  "submission_TOS": "http://si.edu/Termsofuse"},
                        #  "resource_data_type": "metadata",
                        #  "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                        #  "payload_placement": "inline",
                        #  "payload_schema": ["NSDL DC 1.02.020"],
                        #  "create_timestamp": "2011-11-07T14:51:07.137671Z",
                        #  "doc_version": "0.11.0",
                        #  "active": True,
                        #  "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                        #  "submitter_type": "agent",
                        #  }
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

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
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

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
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

    def current_timestamp(self):
        return "%sZ"%datetime.utcnow().isoformat()

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    def test_publish_created_timestamps(self):
        s = Server(config["app_conf"]['couchdb.url.dbadmin'])
        db = s[config["app_conf"]['couchdb.db.resourcedata']]

        ts_fields = ['create_timestamp', 'update_timestamp', 'node_timestamp']

        data = { 
                "documents": 
                     [
                        { 
                        "active" : True,
                        "doc_type" : "resource_data",
                        "doc_version": "0.23.0",
                        "payload_schema": ["none"],
                        "resource_data_type": "metadata",
                        "resource_locator" : "http://example.com",
                        "identity": { "submitter" : "anonymous", "submitter_type" : "anonymous"},
                        "payload_placement": "inline",
                        "resource_data" : "something",
                        "TOS" : { "submission_TOS" : "http://example.com" },
                        "weight" : 0,
                        "resource_TTL" : 0,
                        }
                     ]
                }
        def publish_doc():
            sleep(1)
            start_time = self.current_timestamp()
            sleep(1)
            result = json.loads(self.app.post('/publish',params=json.dumps(data), headers=headers).body)
            sleep(1)
            end_time = self.current_timestamp()
            assert start_time < end_time, "not enough time has passed."
            assert(result['OK'] == True), self._PUBLISH_UNSUCCESSFUL_MSG
            assert(result['document_results'][0]['OK'] == True), "Should have published successfully."
            published = db[result['document_results'][0]['doc_ID']]

            for field in ts_fields:
                assert start_time < published[field] and end_time > published[field], "bad timestamp set for %s"%field
        
        publish_doc()
        
        publish_doc()        




    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    def test_empty_document_array(self):
        data = { "documents": [] }
        result = json.loads(self.app.post('/publish',params=json.dumps(data), headers=headers).body)
        assert(result['OK'] == False), "Should catch empty documents array on publish, no error returned"
        assert(result['error'] == "List of documents is empty"), "Incorrect error message returned"

    # Handles case where documents field is missing
    # Example here is trying to publish a document without the wrapper
    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
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

    @decorators.ModifiedServiceDoc(config["app_conf"]['lr.publish.docid'], decorators.update_authz())
    def test_multiple_version(self):
        
        data = {
            "documents": 
                    [
                       {
                            "doc_type": "resource_data",
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
                        {
                            "doc_type": "resource_data",
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
                            "doc_version": "0.49.0",
                            "active": True,
                            "identity": {
                                "signer": "Smithsonian Education <learning@si.edu>",
                                "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                                "submitter_type": "agent",
                                "curator": "Smithsonian Education",
                                "owner": "Smithsonian American Art Museum"
                            },
                            "replaces": ["someDocId"]
                        }

                        #
                        # Deprecating support for pre - 0.23.0 envelopes
                        #
                         
                        # {"doc_type": "resource_data",
                        # "resource_locator": "http://example.com/1",
                        #  "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                        #  "TOS": {"submission_attribution": "Smithsonian Education",
                        #  "submission_TOS": "http://si.edu/Termsofuse"},
                        #  "resource_data_type": "metadata",
                        #  "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                        #  "payload_placement": "inline",
                        #  "payload_schema": ["NSDL DC 1.02.020"],
                        #  "node_timestamp": "2011-12-21T04:57:18.343124Z",
                        #  "digital_signature": {"key_location": ["http://pgp.mit.edu:11371/pks/lookup?op=get&search=0xE006035FD5EFEA67"],
                        #  "signing_method": "LR-PGP.1.0",
                        #  "signature": "-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA256\n\n316c7e1e9436cc45f5c2f0a1ba8d560adefb22e2ca4abf72fa5279267c88ac6e-----BEGIN PGP SIGNATURE-----\nVersion: BCPG v1.46\n\niQFdBAEBCABHBQJOt+/6QBxTbWl0aHNvbmlhbiBFZHVjYXRpb24gKFNtaXRoc29u\naWFuIEVkdWNhdGlvbikgPGxlYXJuaW5nQHNpLmVkdT4ACgkQ4AYDX9Xv6merCAf+\nPJQ6TX7jTo79a9XKhaSmFbYTgRz+D/uN9ksWJjsmvvoprqjMnsZBivD+3YDE/nTK\nttexx5Gy173Sj0wsojY4UPVezPmwbBjA2+2CG9btTKIsg3WwQpqzPeA/6LT46Ski\n2v3UbbGAMAU00ereuOjmdsqRZkXD/ABtZ/LYVMQCIqVMdR3aeQorHzuLlxTuzt/A\nMFxJb4A+a2jVw5nUM2Ry/x31Cb0pQ9uNO+jIWr8Xl3fjqiD5dUtySmVYvOEjEYcN\nh1twKySLmRWx0OfLN/Fnr1+N+sXT/s7lPCopKV3leEC2FOKDTjHhFM3mKUJvV4E+\ncXWLz6hBgEtIJlRuIj/o"},
                        #  "create_timestamp": "2011-11-07T14:51:07.137671Z",
                        #  "doc_version": "0.21.0",
                        #  "active": True,
                        #  "identity": {"signer": "Smithsonian Education <learning@si.edu>",
                        #  "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                        #  "submitter_type": "agent",
                        #  "curator": "Smithsonian Education",
                        #  "owner": "Smithsonian American Art Museum"}
                        # },
                        
                        # {
                        # "doc_type": "resource_data",
                        # "resource_locator": "http://example.com/2",
                        #  "resource_data": "\n<nsdl_dc:nsdl_dc xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n xmlns:dct=\"http://purl.org/dc/terms/\"\n xmlns:ieee=\"http://www.ieee.org/xsd/LOMv1p0\"\n xmlns:nsdl_dc=\"http://ns.nsdl.org/nsdl_dc_v1.02/\"\n schemaVersion=\"1.02.020\"\n xsi:schemaLocation=\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\">\n <dc:identifier xsi:type=\"dct:URI\">http://www.myboe.org/go/resource/23466</dc:identifier>\n <dc:title>Posters to Go</dc:title>\n <dc:description>PDF version of a set of fifteen posters from the National Portrait Gallery and the Smithsonian American Art Museum. Includes an application for receiving the actual posters for the classroom. Arranged into themes: Westward Expansion Civil War Harlem Renaissance World War II and the Sixties.</dc:description>\n <dc:creator/>\n <dc:language>en-US</dc:language>\n <dct:accessRights xsi:type=\"nsdl_dc:NSDLAccess\">Free access</dct:accessRights>\n <dc:format>text/html</dc:format>\n <dc:date>2010-07-26</dc:date>\n <dct:modified>2010-07-26</dct:modified>\n</nsdl_dc:nsdl_dc>",
                        #  "TOS": {"submission_attribution": "Smithsonian Education",
                        #  "submission_TOS": "http://si.edu/Termsofuse"},
                        #  "resource_data_type": "metadata",
                        #  "payload_schema_locator": "http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd",
                        #  "payload_placement": "inline",
                        #  "payload_schema": ["NSDL DC 1.02.020"],
                        #  "create_timestamp": "2011-11-07T14:51:07.137671Z",
                        #  "doc_version": "0.11.0",
                        #  "active": True,
                        #  "submitter": "Brokers of Expertise on behalf of Smithsonian Education",
                        #  "submitter_type": "agent",
                        #  }
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
