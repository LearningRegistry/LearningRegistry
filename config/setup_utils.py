'''
Created on Aug 16, 2011

@author: jklo
'''
import couchdb 
import sys
import traceback
from uuid import uuid4
import lrnodetemplate as t
from pprint import pprint
import urlparse


#Default url to the couchdb server.
_DEFAULT_COUCHDB_URL =  "http://127.0.0.1:5984"

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
        couchServer.config()
    except Exception as e:
        print(e)
        print("Cannot connect to couchDB server '{0}'\n".format(serverURL))
        return False
    return True

def getInput(question, defaultInput=None,  validateFunc=None):
    ques = question+':  '
    if defaultInput is not None:
            ques = question+' [{0}]:  '.format(defaultInput)

    while True:
        userInput = raw_input(ques)
        inputLen =  len(userInput.strip())
        if inputLen == 0:
            if defaultInput is not None:
                userInput = defaultInput
            else:
                continue

        if validateFunc is not None and validateFunc(userInput) == False:
            continue

        return userInput
    
_DEFAULT_ENDPOINT = "http://www.example.com"

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

def getSetupInfo():
    """Get the user node info"""
    nodeSetup = {}
    
    nodeUrl = getInput("Enter the node service endpoint URL", _DEFAULT_ENDPOINT, isURL)
    nodeSetup['nodeUrl'] = nodeUrl
    
    couchDBUrl  = getInput("Enter your couchDB server URL",
                                            _DEFAULT_COUCHDB_URL, testCouchServer)

    nodeSetup['couchDBUrl'] = couchDBUrl

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

    nodeSetup['distributeResourceDataUrl'] = getInput("\nEnter distribute/replication "+
                        "resource_data destination URL \n(this is the resource_data URL that another node couchdb "+
                        "will use to replicate/distribute to this node)", "{0}/resource_data".format(nodeUrl))
    
    isDistributeDest = getInput("Does the node want to be the destination for replication (T/F)", 'T')
    nodeSetup['open_connect_dest'] =(isDistributeDest =='T')
    return nodeSetup
