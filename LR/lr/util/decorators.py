'''
Created on Oct 11, 2011

@author: jklo
'''
from contextlib import closing
from functools import wraps
from ijson.parse import items
from lr.lib.signing import reloadGPGConfig
from pylons import config
from uuid import uuid1
from LRSignature.sign.Sign  import Sign_0_21
import base64
import copy
import couchdb
import gnupg
import ijson
import json
import logging
import os
import shutil
import tempfile
import time
import urllib, urlparse, oauth2, socket, uuid
import urllib2

log = logging.getLogger(__name__)

class SetFlowControl(object):
    def __init__(self,enabled,serviceDoc,doc_limit=100,id_limit=100):
        server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.nodeDb = server[config['couchdb.db.node']]
        self.enabled = enabled
        self.serviceDoc = serviceDoc
        self.doc_limit=doc_limit
        self.id_limit=id_limit

    def __call__(self,f):
        @wraps(f)
        def set_flow_control(obj, *args, **kw):
            serviceDoc = self.nodeDb[self.serviceDoc]
            service_data = copy.deepcopy(serviceDoc['service_data'])     
            serviceDoc['service_data']['flow_control'] = self.enabled
            serviceDoc['service_data']['doc_limit'] = self.doc_limit
            serviceDoc['service_data']['id_limit'] = self.id_limit  
            self.nodeDb[self.serviceDoc] = serviceDoc
            try:
                return f(obj, *args, **kw)
            finally:
                serviceDoc['service_data'] = service_data         
                self.nodeDb[self.serviceDoc] = serviceDoc  
        return set_flow_control

class ModifiedServiceDoc(object):
    def __init__(self, service_doc_id, update=None):
        server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.nodeDb = server[config['couchdb.db.node']]
        self.service_doc_id = service_doc_id
        self.update_fn = update
        
    def __call__(self,f):
        @wraps(f)
        def wrapped(*args, **kw):
            orig_serviceDoc = self.nodeDb[self.service_doc_id]
            copy_serviceDoc = copy.deepcopy(orig_serviceDoc)
            if self.update_fn:
                copy_serviceDoc =self.update_fn(copy_serviceDoc)
                self.nodeDb[self.service_doc_id] = copy_serviceDoc
            try:
                return f(*args, **kw)
            finally:
                orig_serviceDoc["_rev"] = self.nodeDb[self.service_doc_id]["_rev"]       
                self.nodeDb[self.service_doc_id] = orig_serviceDoc  
        return wrapped

def update_authz(basicauth=False, oauth=False):
        def update(orig):
                orig["service_auth"] = orig["service_auth"] or { }
                orig["service_auth"]["service_authz"] = []
                if basicauth == True:
                        orig["service_auth"]["service_authz"].append("basicauth")
                if oauth == True:
                        orig["service_auth"]["service_authz"].append("oauth")

                if len(orig["service_auth"]["service_authz"]) == 0:
                        orig["service_auth"]["service_authz"].append("none")
                return orig
        return update

def ForceCouchDBIndexing():
    json_headers = {"Content-Type": "application/json"}
    couch = {
        "url": config["couchdb.url"],
        "resource_data": config["couchdb.db.resourcedata"]
    }

    def indexTestData(obj):

        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        design_docs = obj.db.view('_all_docs', **opts)
        for row in design_docs:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                for view in row.doc["views"].keys():
#                    view = row.doc["views"].keys()[0]
                    view_name = "{0}/_view/{1}".format( row.key, view)
                    index_opts = { "limit": 1, "descending": 'true'}
                    if "reduce" in row.doc["views"][view]:
                        index_opts["reduce"] = 'false'
                    # log.debug("Indexing: {0}".format( view_name))
                    req = urllib2.Request("{url}/{resource_data}/{view}?{opts}".format(view=view_name, opts=urllib.urlencode(index_opts), **couch), 
                                          headers=json_headers)
                    try:
                        res = urllib2.urlopen(req)
                    except Exception, e:
                        log.info("Problem indexing: %s", req)
#                    view_result = obj.db.view(view_name, **index_opts)
                    # log.error("Indexed: {0}, got back: {1}".format(view_name, json.dumps(res.read())))
            else:
                pass#log.error("Not Indexing: {0}".format( row.key))
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                indexTestData(self)
                return fn(self, *args, **kw)
            except :
                raise
            finally:
                indexTestData(self)
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator




def PublishTestDocs(sourceData, prefix, sleep=0, force_index=True):
    
    json_headers = {"Content-Type": "application/json"}
    test_data_log = "test-data-%s.log" % prefix
    couch = {
        "url": config["couchdb.url"],
        "resource_data": config["couchdb.db.resourcedata"]
    }
    
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def writeTestData(obj, **kw):
        
        try:
            key = kw["pgp_keys"][0]
            signer = Sign_0_21(privateKeyID=key["fingerprint"], passphrase=key["passphrase"], gnupgHome=kw["gnupghome"], gpgbin=kw["gpgbin"], publicKeyLocations=key["locations"])
        except:
            signer = None

        if not hasattr(obj, "test_data_ids"):
            obj.test_data_ids = {}
        
        obj.test_data_ids[prefix] = []
        with open(test_data_log, "w") as plog:
            for doc in sourceData:
                if "doc_ID" not in doc:
                    doc["doc_ID"] = prefix+str(uuid1())

                try:
                    doc = signer.sign(doc)
                except:
                    pass

                obj.app.post('/publish', params=json.dumps({"documents": [ doc ]}), headers=json_headers)
                plog.write(doc["doc_ID"] + os.linesep)
                obj.test_data_ids[prefix].append(doc["doc_ID"])
                if sleep > 0:
                    time.sleep(sleep)
            kw["test_data_ids"] = obj.test_data_ids[prefix]

        return kw
    
    def indexTestData(obj):
        
        if force_index == False:
            return
        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        design_docs = obj.db.view('_all_docs', **opts)
        for row in design_docs:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                for view in row.doc["views"].keys():
#                    view = row.doc["views"].keys()[0]
                    view_name = "{0}/_view/{1}".format( row.key, view)
                    index_opts = { "limit": 1, "descending": 'true'}
                    if "reduce" in row.doc["views"][view]:
                        index_opts["reduce"] = 'false'
                    # log.error("Indexing: {0}".format( view_name))
                    req = urllib2.Request("{url}/{resource_data}/{view}?{opts}".format(view=view_name, opts=urllib.urlencode(index_opts), **couch), 
                                          headers=json_headers)
                    try:
                        res = urllib2.urlopen(req)
                    except Exception, e:
                        log.info("Problem forcing index: %s", e)
#                    view_result = obj.db.view(view_name, **index_opts)
                    # log.error("Indexed: {0}, got back: {1}".format(view_name, json.dumps(res.read())))
            else:
                pass# log.error("Not Indexing: {0}".format( row.key))
    
    def cacheTestData(obj, **kw):
        req = urllib2.Request("{url}/{resource_data}/_all_docs?include_docs=true".format(**couch), 
                              data=json.dumps({"keys":obj.test_data_ids[prefix]}), 
                              headers=json_headers)
        res = urllib2.urlopen(req)
        docs = list(items(res, 'rows.item.doc'))
        
        if not hasattr(obj, "test_data_sorted"):
            obj.test_data_sorted = {}
        
        def sortkey(k):
            try:
                return k['node_timestamp']
            except:
                return k['create_timestamp']

        obj.test_data_sorted[prefix] = sorted(docs, key=lambda k: sortkey(k))
        kw["test_data_sorted"] = obj.test_data_sorted[prefix]

        return kw
        
        
        
    def removeTestData(obj):
        for doc_id in obj.test_data_ids[prefix]:
            try:
                del obj.db[doc_id]
            except Exception as e:
                print e.message
            try:
                del obj.db[doc_id+"-distributable"]
            except Exception as e:
                print e.message
        
        try:        
            del obj.test_data_ids[prefix]
        except Exception as e:
            print e.message
        
        try:
            del obj.test_data_ids[prefix]
        except Exception as e:
            print e.message
        
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                kw = writeTestData(self, **kw)
                indexTestData(self)
                kw = cacheTestData(self, **kw)
                return fn(self, *args, **kw)
            except :
                raise
            finally:
                removeTestData(self)
                indexTestData(self)
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator


def getExtraEnvironment(base_url=None):
    env = {}
    if base_url:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
        if query or fragment:
            raise ValueError(
                "base_url (%r) cannot have a query or fragment"
                % base_url)
        if scheme:
            env['wsgi.url_scheme'] = scheme
        if netloc:
            if ':' not in netloc:
                if scheme == 'http':
                    netloc += ':80'
                elif scheme == 'https':
                    netloc += ':443'
                else:
                    raise ValueError(
                        "Unknown scheme: %r" % scheme)
            host, port = netloc.split(':', 1)
            env['SERVER_PORT'] = port
            env['SERVER_NAME'] = host
            env['HTTP_HOST'] = netloc
        if path:
            env['SCRIPT_NAME'] = urllib.unquote(path)
    return env

class OAuthRequest(object):
    def __init__(self,  path, http_method="GET", url_base="http://www.example.com",  oauth_user_attrib="oauth_user", oauth_info_attrib="oauth" ):
        self.oauth_user_attrib = oauth_user_attrib
        self.oauth_info_attrib = oauth_info_attrib
        self.http_method = http_method
        self.url_base = url_base
        self.path = path
        self.server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.users =  self.server[config['couchdb.db.users']] 

    def __call__(self, fn):

        def create_user(oauth_user):
            try:
                del self.users[oauth_user["_id"]]
            except:
                pass
            finally:
                print oauth_user
                self.users.save(oauth_user)

        def remove_user(oauth_user):
            try:
                del self.users[oauth_user["_id"]]
            except:
                pass

        @wraps(fn)
        def test_decorator(cls, *args, **kwargs):
            if (hasattr(cls, self.oauth_user_attrib)):
                self.oauth_user = getattr(cls, self.oauth_user_attrib)
            else:
                err = AttributeError()
                err.message = "Missing attribute '%s' which should be data for CouchDB OAuth User" % self.oauth_user_attrib
                raise  err

            consumer = oauth2.Consumer(key=self.oauth_user["name"], secret=self.oauth_user["oauth"]["consumer_keys"][self.oauth_user["name"]])
            token = oauth2.Token(key="node_sign_token", secret=self.oauth_user["oauth"]["tokens"]["node_sign_token"])

            params = {
                "oauth_signature_method": "HMAC-SHA1",
            }


            req = oauth2.Request.from_consumer_and_token(consumer, token, http_method=self.http_method, http_url="{0}{1}".format(self.url_base, self.path), parameters=params)

            # Sign the request.
            signature_method = oauth2.SignatureMethod_HMAC_SHA1()
            req.sign_request(signature_method, consumer, token)
            
            header = req.to_header()
            header["Authorization"] = str(header["Authorization"])

            extraEnv = getExtraEnvironment(self.url_base)

            class OauthInfo(object):
                def __init__(self, consumer, token, request, header, extraEnv, path):
                    self.consumer = consumer
                    self.token = token
                    self.request = request
                    self.header = header
                    self.env = extraEnv
                    self.path = path


            setattr(cls, self.oauth_info_attrib, OauthInfo(consumer, token, req, header, extraEnv, self.path))
    
            try:
                create_user(self.oauth_user)
                result = fn(cls, *args, **kwargs)
                return result
            finally:
                delattr(cls, self.oauth_info_attrib)
                remove_user(self.oauth_user)

        return test_decorator

class BasicAuthRequest(object):
    def __init__(self, bauth_user_attrib="bauth_user", bauth_info_attrib="bauth" ):
        self.bauth_user_attrib = bauth_user_attrib
        self.bauth_info_attrib = bauth_info_attrib
        self.server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.users =  self.server[config['couchdb.db.users']] 

    def __call__(self, fn):

        def build_basic_auth_header(name, password):
            base64string = base64.encodestring('%s:%s' % (name, password))[:-1]
            return {"Authorization": "Basic %s" % base64string}


        def create_user(name, password, roles=[]):
            user_doc = {
              "_id"          : "org.couchdb.user:{0}".format(name),
              "type"         : "user",
              "name"     : "{0}".format(name),
              "roles"        : roles,
              "password"     : password
            }
            try:
                del self.users[user_doc["_id"]]
            except:
                pass
            finally:
                _, user_doc["_rev"] = self.users.save(user_doc)
                return user_doc


        def delete_user(user_doc):
            try:
                del self.users[user_doc["_id"]]
            except:
                pass



        class BAuthInfo(object):
            def __init__(self, header, name, password):
                self.header = header
                self.username = name
                self.password = password


        @wraps(fn)
        def wrap(cls, *args, **kwargs):
            try:
                self.bauth_user = getattr(cls, self.bauth_user_attrib)
            except:
                raise AttributeError("Attribute containing Basic Auth user credentials missing.")

            user_doc = create_user(**self.bauth_user)

            header = build_basic_auth_header(**self.bauth_user)

            setattr(cls, self.bauth_info_attrib, BAuthInfo(header, **self.bauth_user))

            try:
                return fn(cls, *args, **kwargs)
            except Exception as e:
                raise e
            finally:
                delete_user(user_doc)

        return wrap


def _backup(prop_list=[]):
    backup = {}
    for prop in prop_list:
        backup[prop] = config["app_conf"][prop]
    return backup

def _restore(backup={}):
    config["app_conf"].update(backup)

class make_gpg_keys(object):
    '''decorator that makes at least 1 gpg key.  first key is set at the node key'''
    def __init__(self, count=1):
        self.count = count
        self.gnupghome = tempfile.mkdtemp(prefix="gnupg_", dir=".")
        self.gpgbin = "gpg"
        self.gpg = gnupg.GPG(gnupghome=self.gnupghome, gpgbinary=self.gpgbin)
        self.gpg.encoding = 'utf-8'
        self.keys = []
        

    def __call__(self, f):
        @wraps(f)
        def wrapped(*args, **kw):
                for i in range(self.count):
                    cfg = {
                        "key_type": "RSA",
                        "key_length": 1024,
                        "name_real": "Test Key #%d" % i,
                        "name_comment": "Test key for %s" % f.__class__.__name__,
                        "name_email": "test-%d@example.com" % i,
                        "passphrase": "secret"
                    }
                    key = self.gpg.gen_key(self.gpg.gen_key_input(**cfg))
                    assert key is not None, "GPG key not generated"
                    assert key.fingerprint is not None, "Key missing fingerprint"

                    cfg.update({
                        "key": key,
                        "fingerprint": key.fingerprint,
                        "key_id": key.fingerprint[-16:],
                        "locations": ["http://www.example.com/pubkey/%s" % key.fingerprint[-16:] ],
                        "owner": "%s (%s)" % (cfg["name_real"], cfg["name_email"]) 
                        })
                    self.keys.append(cfg)

                kw["pgp_keys"] = self.keys
                kw["gnupghome"] = self.gnupghome
                kw["gpgbin"] = self.gpgbin
                kw["gpg"] = self.gpg

                backup_props = [
                    "lr.publish.signing.privatekeyid",
                    "lr.publish.signing.passphrase",
                    "lr.publish.signing.gnupghome",
                    "lr.publish.signing.gpgbin",
                    "lr.publish.signing.publickeylocations",
                    "lr.publish.signing.signer"
                ]
                backup_conf = _backup(backup_props)

                config["app_conf"].update({
                    "lr.publish.signing.privatekeyid": self.keys[0]["key_id"],
                    "lr.publish.signing.passphrase": self.keys[0]["passphrase"],
                    "lr.publish.signing.gnupghome": self.gnupghome,
                    "lr.publish.signing.gpgbin": self.gpgbin,
                    "lr.publish.signing.publickeylocations": '''["http://localhost/pubkey"]''',
                    "lr.publish.signing.signer": self.keys[0]["owner"]
                    })

                reloadGPGConfig(config["app_conf"])

                try:
                    return f(*args, **kw)
                finally:
                    shutil.rmtree(self.gnupghome)
                    _restore(backup_conf)
                    reloadGPGConfig(config["app_conf"])

        return wrapped




