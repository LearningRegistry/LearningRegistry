'''
Created on Aug 16, 2011

@author: jklo
'''
import couchdb 
import sys, os, gnupg, json, getpass
import traceback
from uuid import uuid4
import lrnodetemplate as t
from pprint import pprint
import urlparse


#Default url to the couchdb server.
_DEFAULT_COUCHDB_URL =  "http://127.0.0.1:5984"
_DEFAULT_AUTH_COUCHDB_URL =  "http://admin:password@127.0.0.1:5984"

class ResponseFile(object):
    def __init__(self, filename=None):
        self._response_file = None
        ResponseFile.set(self, filename)
    
    def set(self, path):
        self._path = path
        try:
            self._response_file = open(path, "w")
            self._response_file.truncate()
            self._response_file.flush()
        except:
            pass


    def write(self, response):
        if self._response_file:
            self._response_file.write("{0}{1}".format(response, os.linesep))
            self._response_file.flush()

    def close(self):
        if self._response_file:
            self._response_file.close()
            self._response_file = None
            self._path = None

response_file = ResponseFile()


def publishService(nodeUrl, server, dbname, serviceType, serviceName):
    service = {}
    service.update(t.service_description)
    service['service_type'] =serviceType
    service['service_id'] = uuid4().hex
#    service['service_name'] = serviceName+" service"
    service['service_name'] = serviceName
    service["service_endpoint"] = urlparse.urljoin(nodeUrl, serviceName)
    service['service_description']= "{0} {1} service".format(serviceType, serviceName)
    PublishDoc(server, dbname,  "{0}:{1} service".format(serviceType, serviceName), service)

def CreateDB(couchServer = _DEFAULT_COUCHDB_URL,  dblist=[], deleteDB=False):
    '''Creates a DB in Couch based upon config'''
    for db in dblist:
        if deleteDB:
            try:
                del couchServer[db]
            except couchdb.http.ResourceNotFound as rnf:
                print("DB '{0}' doesn't exist on '{1}', creating".format(db, couchServer))
        else:
            try:
                existingDB = couchServer[db]
                print("Using existing DB '{0}' on '{1}'\n".format(db, couchServer))
                continue
            except:
                pass
        try:
            couchServer.create(db)
            print("Created DB '{0}' on '{1}'\n".format(db, couchServer))
        except Exception as e:
            print("Exception while creating database: {0}\n".format(e) )


def PublishDoc(couchServer, dbname, name, doc_data):
    try:
        #delete existing document.
        db = couchServer[dbname]
        if "_rev" in doc_data:
            del doc_data["_rev"]
       
        try:
            del db[name]
        except:
            pass
        db[name] = doc_data
        print("Added config document '{0}' to '{1}".format(name, dbname))
    except  Exception as ex:
        print("Exception when add config document:\n")
        exc_type, exc_value, exc_tb = sys.exc_info()
        pprint(traceback.format_exception(exc_type, exc_value, exc_tb))


def testCouchServer(serverURL):
    try:
        couchServer =  couchdb.Server(url=serverURL)
        # Try to get the server configuration to ensure the the server is up and
        # and running. There may be a better way of doing that.
        couchServer.version()
    except Exception as e:
        print(e)
        print("Cannot connect to couchDB server '{0}'\n".format(serverURL))
        return False
    return True

def testAuthCouchServer(serverURL):
    try:
        couchServer =  couchdb.Server(url=serverURL)
        # Try to get the server configuration to ensure the the server is up and
        # and running. There may be a better way of doing that.
        couchServer.config()
    except Exception as e:
        print(e)
        print("Cannot connect to couchDB server '{0}'\n".format(serverURL))
        return False
    return True

def getInput(question, defaultInput=None,  validateFunc=None, hide_input=False):
    ques = question+':  '
    if defaultInput is not None:
            ques = question+' [{0}]:  '.format(defaultInput)

    while True:
        if not hide_input:
            userInput = raw_input(ques)
        else:
            userInput = getpass.getpass(ques)

        inputLen =  len(userInput.strip())
        if inputLen == 0:
            if defaultInput is not None:
                userInput = defaultInput
            else:
                continue

        if validateFunc is not None and validateFunc(userInput) == False:
            continue

        response_file.write(userInput)

        return userInput
    
_DEFAULT_ENDPOINT = "http://www.example.com"



def isValidKey(userInput):
    pass

def isURL(userInput):
    if userInput.lower() == _DEFAULT_ENDPOINT:
        return False
    
    import re
    return re.match("^https?://[^/]+", userInput.lower()) is not None

YES = ['t', 'true', 'yes', 'y']
NO = ['f', 'false', 'no', 'n']
def isBoolean(userInput):
    if userInput.lower() in YES or userInput.lower in NO:
        return True

def isInt(userInput):
    try:
        int(userInput)
        return True
    except ValueError:
        return False

def getDefaultEndpoint():
    import socket
    hostname = socket.gethostname()
    if hostname != None:
        parts = list(urlparse.urlsplit(_DEFAULT_ENDPOINT))
        parts[1] = hostname
        return urlparse.urlunsplit(parts)
    else:
        return _DEFAULT_ENDPOINT


def getSetupInfo(response_file=None):
    """Get the user node info"""
    nodeSetup = {}
    


    nodeUrl = getInput("Enter the node service endpoint URL", getDefaultEndpoint(), isURL)
    nodeSetup['nodeUrl'] = nodeUrl
    
    couchDBUrl  = getInput("Enter your unauthenticated couchDB server URL",
                                            _DEFAULT_COUCHDB_URL, testCouchServer)
    nodeSetup['couchDBUrl'] = couchDBUrl

    couchDBUrlDBA  = getInput("Enter your AUTHENTICATED CouchDB server DBA URL",
                                            _DEFAULT_AUTH_COUCHDB_URL, testAuthCouchServer)
    nodeSetup['couchDBUrlDBA'] = couchDBUrlDBA

    nodeName = getInput("Enter your node name", "Node@{0}".format(nodeUrl))
    nodeSetup['node_name'] = nodeName

    nodeDescription = getInput("Enter your node description", nodeName)
    nodeSetup['node_description'] = nodeDescription

    adminUrl = getInput("Enter node admin indentity",
                                    "admin@learningregistry.org".format(nodeUrl))
    nodeSetup['node_admin_identity'] = adminUrl

    distributeTargets = getInput("Enter the URLs of nodes that you wish to distribute to",
                                                 "")
    nodeSetup['connections'] = distributeTargets.split()

    isGatewayNode = getInput('Is the node a gateway node" (T/F)', 'F')
    nodeSetup['gateway_node'] = (isGatewayNode == 'T')
    
    isNodeOpen = getInput('Is the node "open" (T/F)', 'T')
    nodeSetup['open_connect_source']  = (isNodeOpen=='T')

    '''
    nodeSetup['distributeResourceDataUrl'] = getInput("\nEnter distribute/replication "+
                        "resource_data destination URL \n(this is the resource_data URL that another node couchdb "+
                        "will use to replicate/distribute to this node)", "{0}/resource_data".format(nodeUrl))
    '''
    nodeSetup['distributeResourceDataUrl'] = "{0}/resource_data".format(nodeUrl)
    nodeSetup['distributeIncomingUrl'] = getInput("\nEnter distribute/replication "+
                        "incoming destination URL \n(this is the incoming URL that another node couchdb "+
                        "will use to replicate/distribute to this node)", "{0}/incoming".format(nodeUrl))
    

    isDistributeDest = getInput("Does the node want to be the destination for replication (T/F)", 'T')
    nodeSetup['open_connect_dest'] =(isDistributeDest =='T')
    return nodeSetup

def getDefaultGnuPGHome():
    return os.path.join(os.path.expanduser('~'), ".gnupg")

def getGPG(gpgbin, gnupghome):
    return gnupg.GPG(gpgbin, gnupghome)

def checkKey(gpg):
    def checkKeyID(userInput):
        try:
            if len(userInput.strip()) == 0:
                return False
            privateKey = gpg.export_keys(userInput, True)
            publicKey = gpg.export_keys(userInput, True)
            foundKey = len(privateKey) > 0 and len(publicKey) > 0
            if not foundKey:
                print("Invalid Private Key ID. Ensure key public and private key exists in keyring. Please try again.\n")
            return foundKey
        except:
            pass
        return False
    return checkKeyID

def checkPassphrase(gpg, keyID):
    def check(userInput):
        try:
            sign = gpg.sign("hello learning registry", keyid=keyID, passphrase=userInput)
            if len(sign.data) > 0 and len(sign.fingerprint) > 0:
                return True
            else:
                print("Bad passphrase! Please try again.\n")
        except:
            pass
        return False
    return check

def getDefaultSigner(gpg, keyID):
    try:
        for key in gpg.list_keys(True):
            if key['keyid'] == keyID.strip():
                return key['uids'][0]
    except:
        pass
    return None
            

def setNodeSigning(server, config, setupInfo):
    if "oauth" in setupInfo and setupInfo["oauth"]:
        from services.service_template import getCouchAppPath
        import oauth2 as oauth, time

        gpgbin = getInput("Path to GnuPG executable", "gpg")
        setupInfo["lr.publish.signing.gpgbin"] = gpgbin
        config.set("app:main","lr.publish.signing.gpgbin",gpgbin)

        gnupghome = getInput("Path to GnuPG Home", getDefaultGnuPGHome())
        setupInfo["lr.publish.signing.gnupghome"] = gnupghome
        config.set("app:main","lr.publish.signing.gnupghome",gnupghome)

        gpg = getGPG(gpgbin, gnupghome)

        privateKeyId = getInput("Private Key Id for Signing", "", checkKey(gpg)).strip()
        setupInfo["lr.publish.signing.privatekeyid"] = privateKeyId
        config.set("app:main","lr.publish.signing.privatekeyid",privateKeyId)


        publickeylocations = [ "%s/pubkey" %  setupInfo['nodeUrl']]
        setupInfo["lr.publish.signing.publickeylocations"] = json.dumps(publickeylocations)
        config.set("app:main","lr.publish.signing.publickeylocations",json.dumps(publickeylocations))


        signer = getInput("Signer for Resource Data Identity", getDefaultSigner(gpg, privateKeyId))
        setupInfo["lr.publish.signing.signer"] = signer
        config.set("app:main","lr.publish.signing.signer",signer)


        passphrase = getInput("Passphrase for Signing with Private Key [typing is concealed]", "", checkPassphrase(gpg, privateKeyId), hide_input=True)
        setupInfo["lr.publish.signing.passphrase"] = passphrase
        config.set("app:main","lr.publish.signing.passphrase",passphrase)

        

        server.resource("_config","couch_httpd_oauth").put('use_users_db', '"true"')
        server.resource("_config","httpd").put('WWW-Authenticate', '"OAuth"')
        server.resource("_config","browserid").put('enabled', '"true"')

        apps = config.get("app:main", "couchdb.db.apps", "apps")
        try:
            server.create(apps)
        except:
            pass

        oauthCouchApp = os.path.join(getCouchAppPath(),apps,"kanso","oauth-key-management.json")
        with open(oauthCouchApp) as f:
            ddoc = json.load(f)
            try:
                del server[apps]["_design/%s"%ddoc['kanso']['config']['name']]
            except:
                pass
            ddoc["_id"] = "_design/%s"%ddoc['kanso']['config']['name']
            server[apps].save(ddoc)
            setupInfo["oauth.app.name"] = ddoc['kanso']['config']['name']
            setupInfo["lr.oauth.signup"] = "{0}/apps/{1}".format(setupInfo["nodeUrl"],ddoc['kanso']['config']['name']) 
            config.set("app:main","lr.oauth.signup",setupInfo["lr.oauth.signup"])

        ## TODO: Need to make an initial OAuth call to get the oauth view installed.
        users = config.get("app:main", "couchdb.db.users", "_users")
        couch_url = config.get("app:main", "couchdb.url", "http://localhost:5984")

        dummy_user = {
            "_id": "org.couchdb.user:tempuser",
            "name": "tempuser",
            "type": "user",
            "roles": [],
            "oauth": {
                "consumer_keys":
                {
                    "localhost": "walt_2.0"
                },
                "tokens":
                {
                    "temptoken": "learningregistry"
                }
            }
        }
        server[users].save(dummy_user)

        # Create your consumer with the proper key/secret.
        consumer = oauth.Consumer(key="localhost", 
            secret=dummy_user["oauth"]["consumer_keys"]["localhost"])

        token = oauth.Token(key="temptoken",
            secret=dummy_user["oauth"]["tokens"]["temptoken"])



        # Create our client.
        client = oauth.Client(consumer, token=token)
        client.disable_ssl_certificate_validation=True

        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time())
        }
        
        resp, content = client.request("{0}/_session".format(couch_url), "GET", headers={"Content-Type": "application/json"})

        del server[users][dummy_user["_id"]]

        return True
    return False

        
