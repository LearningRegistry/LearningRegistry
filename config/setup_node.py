#!/usr/bin/env python
#    Copyright 2011 Lockheed Martin
#

#
#Simple script to setup and initialize a learning registry node documents and
# commit to a specified coudbserver.
#

import ConfigParser
import os
import couchdb
import urlparse
import subprocess
import lrnodetemplate as t
from uuid import uuid4
import shutil
import logging
from setup_utils import *
import re
log = logging.getLogger(__name__)
scriptPath = os.path.dirname(os.path.abspath(__file__))

_PYLONS_CONFIG_SRC =  os.path.join(scriptPath, '..', 'LR', 'development.ini.orig')
_PYLONS_CONFIG_DEST = os.path.join(scriptPath, '..', 'LR', 'development.ini')
_COUCHAPP_PATH = os.path.join(scriptPath, '..', 'couchdb')

# add path to virtualenv if the environment variable is set
if os.getenv('VIRTUAL_ENV') is not None:
    _VIRTUAL_ENV_PATH = os.path.expandvars('${VIRTUAL_ENV}')
else:
    _VIRTUAL_ENV_PATH = ''

print ("\n{0}\n{1}\n{2}".format(
                _PYLONS_CONFIG_SRC, _PYLONS_CONFIG_DEST, _COUCHAPP_PATH))

#Read the pylons configuration to get the database names.
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG_SRC)

_RESOURCE_DATA = _config.get("app:main", "couchdb.db.resourcedata")
_NODE = _config.get("app:main", "couchdb.db.node")
_COMMUNITY = _config.get("app:main", "couchdb.db.community")
_NETWORK = _config.get("app:main", "couchdb.db.network")

# Dictionary of types services and the corresponding services that are added 
# by default to the node.  The format is 
# "<serviceType>":["<list of services of serviceType>"]
_DEFAULT_SERVICES = {"administrative":
                                                    ["Network Node Description", 
                                                     "Network Node Services", 
                                                     "Network Node Status", 
                                                     "Resource Distribution Network Policy"],
                                        "access":
                                                    ["Basic Obtain", 
                                                     "OAI-PMH Harvest", "Slice", 
                                                     "Basic Harvest", 
                                                     "SWORD APP Publish V1.3"],
                                        "broker":[],
                                        "distribute":
                                                    ["Resource Data Distribution",
                                                     "Push To Distribution",
                                                    ],
                                        "publish":
                                                    ["Basic Publish"]}
                                                    
#Create specific gateway node service list.  It saves the user from setting up 
# services that will be available on gateway nodes.  This also avoid the confusion 
# of setting up services asavailable yet cannot be use since the node was setup 
# as gateway node.
_GATEWAY_NODE_SERVICES ={"administrative":
                                                    ["Network Node Description", 
                                                     "Network Node Services", 
                                                     "Network Node Status", 
                                                     "Resource Distribution Network Policy"],
                                        "distribute":
                                                    ["Resource Data Distribution",
                                                     "Push To Distribution"
                                                    ]
                                    }
def makePythonic(text):
    return re.sub('''[ \.]''', "_", text)

def publishNodeDescription(server, dbname):
    node_description = {}
    node_description.update(t.node_description)
    node_description['node_name'] = nodeSetup['node_name']
    node_description['node_description'] = nodeSetup['node_description']
    node_description['node_admin_identity'] = nodeSetup['node_admin_identity']
    node_description["open_connect_source"] = nodeSetup["open_connect_source"]
    node_description["open_connect_dest"] = nodeSetup["open_connect_dest"]
    node_description['node_id'] = uuid4().hex
    PublishDoc(server, dbname, 'node_description', node_description)
    
def publishNodeServices(nodeUrl, server, dbname, services=_DEFAULT_SERVICES):
    for serviceType in services.keys():
        for serviceName in services[serviceType]:
            plugin = None
            try:
                plugin = __import__("services.%s" % makePythonic(serviceName), fromlist=["install"])
                plugin.install(server, _NODE, nodeSetup)
            except Exception as e:
                if plugin != None:
                    log.exception("Error occurred with %s plugin." % serviceName)
                publishService(nodeUrl, server, dbname, serviceType, serviceName)

def publishNodeConnections(nodeUrl, server, dbname,  nodeName, connectionList):
    for dest_node_url in connectionList:
        connection = dict(t.connection_description)
        connection['connection_id'] = uuid4().hex
        connection['source_node_url']=nodeUrl
        connection['destination_node_url'] = dest_node_url
        PublishDoc(server, dbname, "{0}_to_{1}_connection".format(nodeName, dest_node_url), connection)

def publishCouchApps(databaseUrl, appsDirPath):
    import couch_utils
    couch_utils.pushAllCouchApps(appsDirPath, databaseUrl)

def setCommunityId():
    community = getInput("Enter the community id")
    t.community_description['community_id'] = community
    t.community_description['community_name'] = community
    t.community_description['community_description'] = community
    t.network_description['community_id'] = community
    t.node_description['community_id'] = community
    
def setNetworkId():
    network = getInput("Enter the network id")
    t.network_description['network_id'] = network
    t.network_description['network_name'] = network
    t.network_description['network_description'] = network
    t.node_description['network_id'] = network
    t.network_policy_description['network_id'] = network
    t.network_policy_description['policy_id'] =network+" policy"
        
def setConfigFile(nodeSetup):
    
    #create a copy of the existing config file as to not overide it.
    if os.path.exists(_PYLONS_CONFIG_DEST):
        backup = _PYLONS_CONFIG_DEST+".backup"
        print("\nMove existing {0} to {1}".format(_PYLONS_CONFIG_DEST, backup))
        shutil.copyfile(_PYLONS_CONFIG_DEST, backup)

    #Update pylons config file to use the couchdb url
    _config.set("app:main", "couchdb.url", nodeSetup['couchDBUrl'])
    # set the url to for destribute/replication (that is the url that a source couchdb node
    # will use for replication.
    _config.set("app:main", "lr.distribute_resource_data_url",  nodeSetup['distributeResourceDataUrl'])
    
    destConfigfile = open(_PYLONS_CONFIG_DEST, 'w')
    _config.write(destConfigfile)
    destConfigfile.close()



if __name__ == "__main__":

    from optparse import OptionParser
    import os
    
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
    
    parser = OptionParser()
    parser.add_option("-d", "--devel", dest="devel", action="store_true", default=False,
                      help="Development mode allows the setting of network and community.",
                    )
    (options, args) = parser.parse_args()
    print("\n\n=========================\nNode Configuration\n")
    if options.devel:
        setCommunityId()
        setNetworkId()
    
    
    nodeSetup = getSetupInfo()
    print("\n\n=========================\nNode Configuration\n")
    for k in nodeSetup.keys():
        print("{0}:  {1}".format(k, nodeSetup[k]))

    setConfigFile(nodeSetup)
    
    server =  couchdb.Server(url= nodeSetup['couchDBUrl'])
    if server.version() < "1.1.0":
        _config.set("app:main", "couchdb.stale.flag", "OK")
    destConfigfile = open(_PYLONS_CONFIG_DEST, 'w')
    _config.write(destConfigfile)
    destConfigfile.close()

    

    #Create the databases.
    CreateDB(server, dblist=[_RESOURCE_DATA])
    
    #Delete the existing databases
    CreateDB(server, dblist=[ _NODE, _NETWORK, _COMMUNITY], deleteDB=True)
    
      #Install the services, by default all the services are installed.
    services = _DEFAULT_SERVICES
    if nodeSetup['gateway_node']:
        services = _GATEWAY_NODE_SERVICES
    publishNodeServices(nodeSetup["nodeUrl"], server, _NODE, services)
    
    #Add the network and community description
    PublishDoc(server, _COMMUNITY, "community_description", t.community_description)
    PublishDoc(server, _NETWORK,  "network_description", t.network_description)
    policy = {}
    policy.update(t.network_policy_description)
    PublishDoc(server, _NETWORK,'network_policy_description', policy)

    #Add node description
    publishNodeDescription(server, _NODE)

    #Add the node connections
    publishNodeConnections(nodeSetup["nodeUrl"], server, _NODE,  
                                            nodeSetup["node_name"],  nodeSetup['connections'])


    #Push the couch apps
    #Commands to go the couchapp directory and push all the apps.
    print("\n============================\n")
    print("Pushing couch apps ...")
#    resourceDataUrl = urlparse.urljoin( nodeSetup['couchDBUrl'], _RESOURCE_DATA)
    publishCouchApps(nodeSetup['couchDBUrl'],  _COUCHAPP_PATH)
    print("All CouchApps Pushed")
