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
import ConfigParser
import os
import urllib2
import json
from distributepoints_util import setupDistributionConnections, getDocFromExistingCouchDB, getExistingDistributionConnections


scriptPath = os.path.dirname(os.path.abspath(__file__))
_PYLONS_CONFIG =  os.path.join(scriptPath, '..', 'LR', 'development.ini.orig')
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG)

'''Default values read in from development.ini.orig'''
_DEFAULT_COUCHDB_URL = "http://localhost:5984/"
try:
    _DEFAULT_COUCHDB_URL = _config.get("app:main", "couchdb.url")
except Exception, e:
    print('Cannot find couchdb url from config file')

_NODE = "node"
try:
    _NODE = _config.get("app:main", "couchdb.db.node")
except Exception, e:
    print('Cannot find couchdb node from config file')

_DEFAULT_ENDPOINT = "http://localhost/"
try:
    _DEFAULT_ENDPOINT = _config.get("app:main", "node.endpoint.url")
except Exception, e:
    print('Cannot find node endpoint url from config file')

_DEFAULT_DISTRIBUTE_RESOURCE_DATA_URL = _DEFAULT_ENDPOINT + "/resource_data"
try:
    _DEFAULT_DISTRIBUTE_RESOURCE_DATA_URL = _config.get("app:main", "lr.distribute_resource_data_url")
except Exception, e:
    print('Cannot find distribute resource data url from config file')

_NODE_DESCRIPTION = "node_description"



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
        print("Added config document '{0}' to '{1}'".format(name, dbname))
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


def isURL(userInput):
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

def setupServices(nodeSetup, newNode, gatewayNode='F'):
    '''Add service values to nodeSetup'''
    nodeSetup['activeObtain'] = 'T'
    nodeSetup['flowControlObtain'] = 'F'
    nodeSetup['maxIDObtain'] = '100'
    nodeSetup['maxDocObtain'] = '100'

    nodeSetup['activeHarvest'] = 'T'
    nodeSetup['flowControlHarvest'] = 'F'
    nodeSetup['maxIDHarvest'] = '100'
    nodeSetup['maxDocHarvest'] = '100'

    nodeSetup['activeOAIPMHHarvest'] = 'T'
    nodeSetup['flowControlOAIPMHHarvest'] = 'F'
    nodeSetup['maxIDOAIPMHHarvest'] = '100'
    nodeSetup['maxDocOAIPMHHarvest'] = '100'

    nodeSetup['activeSlice'] = 'T'
    nodeSetup['flowControlSlice'] = 'F'
    nodeSetup['maxIDSlice'] = '100'
    nodeSetup['maxDocSlice'] = '100'
    
    nodeSetup['activePublish'] = 'T'
    nodeSetup['maxSizePublish'] = '1000'
    nodeSetup['maxDocPublish'] = '1000'
            
    nodeSetup['activeSWORD'] = 'T'        
    nodeSetup['activeResourceDataDistribution'] = 'T'
    nodeSetup['activeResourceDistributionNetworkPolicy'] = 'T'
    nodeSetup['activeNetworkNodeDescription'] = 'T'
    nodeSetup['activeNetworkNodeService'] = 'T'
    nodeSetup['activeNetworkNodeStatus'] = 'T'
    
    '''List of service docs'''
    serviceDocs = ['access:Basic Obtain service',
                        'access:Basic Harvest service',                    
                        'access:OAI-PMH service',
                        'access:slice',
                        'publish:Basic Publish service',
                        'publish:SWORD APP Publish V1.3 service',
                        'distribute:Resource Data Distribution service',
                        'administrative:Resource Distribution Network Policy service',
                        'administrative:Network Node Description service',
                        'administrative:Network Node Services service',
                        'administrative:Network Node Status service'
                        ]
           
    '''If user is updating node and it is not a gateway node then retrieve existing service values'''                    
    if not newNode and gatewayNode == 'F':
        for doc in serviceDocs:
            try:
                nodeDoc = getDocFromExistingCouchDB(_NODE, _DEFAULT_COUCHDB_URL, doc)

                if doc == 'access:Basic Obtain service':
                    nodeSetup['activeObtain'] = str(nodeDoc['active'])[:1]
                    nodeSetup['flowControlObtain'] = str(nodeDoc['service_data']['flow_control'])[:1]      
                    if nodeSetup['flowControlObtain'] == 'T':    
                        nodeSetup['maxIDObtain'] = str(nodeDoc['service_data']['id_limit'])
                        nodeSetup['maxDocObtain'] = str(nodeDoc['service_data']['doc_limit'])            
                
                elif doc == 'access:Basic Harvest service':
                    nodeSetup['activeHarvest'] = str(nodeDoc['active'])[:1]
                    nodeSetup['flowControlHarvest'] = str(nodeDoc['service_data']['flow_control'])[:1]   
                    if nodeSetup['flowControlHarvest'] == 'T':    
                        nodeSetup['maxIDHarvest'] = str(nodeDoc['service_data']['id_limit'])
                        nodeSetup['maxDocHarvest'] = str(nodeDoc['service_data']['doc_limit'])

                elif doc == 'access:OAI-PMH service':        
                    nodeSetup['activeOAIPMHHarvest'] = str(nodeDoc['active'])[:1]
                    nodeSetup['flowControlOAIPMHHarvest'] = str(nodeDoc['service_data']['flow_control'])[:1] 
                    if nodeSetup['flowControlOAIPMHHarvest'] == 'T':    
                        nodeSetup['maxIDOAIPMHHarvest'] = str(nodeDoc['service_data']['id_limit'])
                        nodeSetup['maxDocOAIPMHHarvest'] = str(nodeDoc['service_data']['doc_limit'])
                
                elif doc == 'access:slice':        
                    nodeSetup['activeSlice'] = str(nodeDoc['active'])[:1]
                    nodeSetup['flowControlSlice'] = str(nodeDoc['service_data']['flow_control'])[:1]
                    if nodeSetup['flowControlSlice'] == 'T':    
                        nodeSetup['maxIDSlice'] = str(nodeDoc['service_data']['id_limit'])
                        nodeSetup['maxDocSlice'] = str(nodeDoc['service_data']['doc_limit'])

                elif doc == 'publish:Basic Publish service':       
                    nodeSetup['activePublish'] = str(nodeDoc['active'])[:1]
                    nodeSetup['maxSizePublish'] = str(nodeDoc['service_data']['msg_size_limit'])
                    nodeSetup['maxDocPublish'] = str(nodeDoc['service_data']['doc_limit'])        

                elif doc == 'publish:SWORD APP Publish V1.3 service':
                    nodeSetup['activeSWORD'] = str(nodeDoc['active'])[:1]
                    
                elif doc == 'distribute:Resource Data Distribution service':            
                    nodeSetup['activeResourceDataDistribution'] = str(nodeDoc['active'])[:1]

                elif doc == 'administrative:Resource Distribution Network Policy service':   
                    nodeSetup['activeResourceDistributionNetworkPolicy'] = str(nodeDoc['active'])[:1]    

                elif doc == 'administrative:Network Node Description service':   
                    nodeSetup['activeNetworkNodeDescription'] = str(nodeDoc['active'])[:1]

                elif doc == 'administrative:Network Node Services service':   
                    nodeSetup['activeNetworkNodeService'] = str(nodeDoc['active'])[:1]
                    
                elif doc == 'administrative:Network Node Status service':
                    nodeSetup['activeNetworkNodeStatus'] = str(nodeDoc['active'])[:1]                   

            except Exception, e:
                print('Could not retrieve ' + doc)

'''If user is updating, retrieve existing node values from CouchDB'''
def getExistingNodeDescriptionValues(couchdbURL, dbName, docID, endpointURL):
    newNodeDescriptionValues = {'_DEFAULT_NODE_NAME' : "Node@" + _DEFAULT_ENDPOINT,
                                    '_DEFAULT_NODE_ADMIN_IDENTITY' : "admin@learningregistry.org",  
                                    '_DEFAULT_NODE_DESCRIPTION' : "Node@" + _DEFAULT_ENDPOINT,   
                                    '_DEFAULT_GATEWAY_NODE' : "F",
                                    '_DEFAULT_OPEN_CONNECT_SOURCE' : "T",   
                                    '_DEFAULT_OPEN_CONNECT_DEST' : "T",
                                    '_DEFAULT_CONNECTIONS' : []
                                    }

    try:
        node_desc = getDocFromExistingCouchDB(dbName, couchdbURL, docID)
        
        newNodeDescriptionValues['_DEFAULT_NODE_NAME'] = node_desc['node_name']
        newNodeDescriptionValues['_DEFAULT_NODE_ADMIN_IDENTITY'] = node_desc['node_admin_identity']
        newNodeDescriptionValues['_DEFAULT_NODE_DESCRIPTION'] = node_desc['node_description']
        newNodeDescriptionValues['_DEFAULT_GATEWAY_NODE'] = str(node_desc['gateway_node'])[:1]
        newNodeDescriptionValues['_DEFAULT_OPEN_CONNECT_SOURCE'] = str(node_desc['open_connect_source'])[:1]
        newNodeDescriptionValues['_DEFAULT_OPEN_CONNECT_DEST'] = str(node_desc['open_connect_dest'])[:1]
            
    except Exception, e:
        print(e)
        print('Connection to Node database not established, using default setup values')

    return newNodeDescriptionValues


def getSetupInfo():

    """Get the user node info"""
    nodeSetup = {}

    '''See if the user is updating or creating a new node'''
    flag = True
    while(flag):
        newOrUpdate = raw_input("\nCreate a [N]ew node or [U]pdate your existing node: ")
        if newOrUpdate == 'U' or newOrUpdate == 'u':
            '''Set the node values the user will be prompted with'''
            nodeDescriptionValues = getExistingNodeDescriptionValues(_DEFAULT_COUCHDB_URL, _NODE, _NODE_DESCRIPTION, _DEFAULT_ENDPOINT) 
            nodeDescriptionValues['_DEFAULT_CONNECTIONS'] =  getExistingDistributionConnections(_DEFAULT_COUCHDB_URL,_NODE,nodeDescriptionValues['_DEFAULT_NODE_NAME'])   
            '''Will not be a new node'''
            nodeSetup['newNode'] = False
            '''Setup node services from existing values'''            
            setupServices(nodeSetup, nodeSetup['newNode'], nodeDescriptionValues['_DEFAULT_GATEWAY_NODE'])
            flag = False

        elif newOrUpdate == 'N' or newOrUpdate == 'n':
            '''Default node description values'''
            nodeDescriptionValues = {'_DEFAULT_NODE_NAME' : "Node@" + _DEFAULT_ENDPOINT,
                                    '_DEFAULT_NODE_ADMIN_IDENTITY' : "admin@learningregistry.org",  
                                    '_DEFAULT_NODE_DESCRIPTION' : "Node@" + _DEFAULT_ENDPOINT,   
                                    '_DEFAULT_GATEWAY_NODE' : "F",
                                    '_DEFAULT_OPEN_CONNECT_SOURCE' : "T",   
                                    '_DEFAULT_OPEN_CONNECT_DEST' : "T",
                                    '_DEFAULT_CONNECTIONS' : []
                                    }

            '''Will be a new node'''                        
            nodeSetup['newNode'] = True
            '''Setup node services with default values'''
            setupServices(nodeSetup, nodeSetup['newNode'])
            flag = False

        else:
            print('\nNot an option, try again\n')    
    
    
    nodeUrl = getInput("\nEnter the node service endpoint URL", 
                                            _DEFAULT_ENDPOINT, isURL)
    nodeSetup['nodeUrl'] = nodeUrl
    

    couchDBUrl  = getInput("Enter your couchDB server URL",
                                            _DEFAULT_COUCHDB_URL, testCouchServer)
    nodeSetup['couchDBUrl'] = couchDBUrl

    
    nodeName = getInput("Enter your node name", 
                                            nodeDescriptionValues['_DEFAULT_NODE_NAME'])
    nodeSetup['node_name'] = nodeName

    
    nodeDescription = getInput("Enter your node description", 
                                            nodeDescriptionValues['_DEFAULT_NODE_DESCRIPTION'])
    nodeSetup['node_description'] = nodeDescription


    adminUrl = getInput("Enter node admin indentity",
                                            nodeDescriptionValues['_DEFAULT_NODE_ADMIN_IDENTITY'])
    nodeSetup['node_admin_identity'] = adminUrl



    distributeFlag = True
    while (distributeFlag):
        manageDistributeTargets = getInput("\nWould you like to edit your distribution URLs?\nInput 'Edit' " +
                                            "to edit targets, or just hit Enter to keep existing targets",
                                            ' '.join(map(str, nodeDescriptionValues['_DEFAULT_CONNECTIONS'])))
    
        if manageDistributeTargets == 'Edit' or manageDistributeTargets == 'edit':    
                distributeFlag = False 
        else:
            if len(manageDistributeTargets) == 0:
                distributeFlag = False 
            else:           
                manageList = manageDistributeTargets.split(' ')    
                distributeFlag = not (manageList[0:] == nodeDescriptionValues['_DEFAULT_CONNECTIONS'][0:])    



    if not (manageDistributeTargets == 'Edit' or manageDistributeTargets == 'edit') :
        nodeSetup['connections'] = nodeDescriptionValues['_DEFAULT_CONNECTIONS']
    else:
        nodeSetup['connections'] = setupDistributionConnections(nodeDescriptionValues['_DEFAULT_CONNECTIONS'])


    
    isGatewayNode = getInput('\nIs the node a gateway node (T/F)', 
                                            nodeDescriptionValues['_DEFAULT_GATEWAY_NODE'])
    nodeSetup['gateway_node'] = (isGatewayNode == 'T' or isGatewayNode =='t')


    
    isNodeOpen = getInput('Is the node "open" (T/F)', 
                                            nodeDescriptionValues['_DEFAULT_OPEN_CONNECT_SOURCE'])
    nodeSetup['open_connect_source'] = (isNodeOpen == 'T' or isNodeOpen == 't')


    nodeSetup['distributeResourceDataUrl'] = getInput("\nEnter distribute/replication "+
                        "resource_data destination URL. This is the resource_data URL that another node couchdb "+
                        "will use to replicate/distribute to this node", 
                                            _DEFAULT_DISTRIBUTE_RESOURCE_DATA_URL)
    

    isDistributeDest = getInput("\nDoes the node want to be the destination for replication (T/F)", 
                                            nodeDescriptionValues['_DEFAULT_OPEN_CONNECT_DEST'])
    nodeSetup['open_connect_dest'] = (isDistributeDest == 'T' or isDistributeDest == 't')

    
    return nodeSetup
