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
import nginx_util
import json

import re
log = logging.getLogger(__name__)
scriptPath = os.path.dirname(os.path.abspath(__file__))

_PYLONS_CONFIG_SRC =  os.path.join(scriptPath, '..', 'LR', 'development.ini.orig')
_PYLONS_CONFIG_DEST = os.path.join(scriptPath, '..', 'LR', 'development.ini')


# add path to virtualenv if the environment variable is set
if os.getenv('VIRTUAL_ENV') is not None:
    _VIRTUAL_ENV_PATH = os.path.expandvars('${VIRTUAL_ENV}')
else:
    _VIRTUAL_ENV_PATH = ''

print ("\n{0}\n{1}".format(_PYLONS_CONFIG_SRC, _PYLONS_CONFIG_DEST))

#Read the pylons configuration to get the database names.
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG_SRC)

_RESOURCE_DATA = _config.get("app:main", "couchdb.db.resourcedata")
_NODE = _config.get("app:main", "couchdb.db.node")
_COMMUNITY = _config.get("app:main", "couchdb.db.community")
_NETWORK = _config.get("app:main", "couchdb.db.network")

try:
    _INCOMING = _config.get("app:main", "couchdb.db.incoming")
except:
    _INCOMING = 'incoming'
# Dictionary of types services and the corresponding services that are added 
# by default to the node.  The format is 
# "<serviceType>":["<list of services of Name>"]
_DEFAULT_SERVICES = {"administrative":
                                                    ["Network Node Description", 
                                                     "Network Node Services", 
                                                     "Network Node Status", 
                                                     "Resource Distribution Network Policy"],
                                        "access":
                                                    ["Basic Obtain", 
                                                     "OAI-PMH Harvest", 
                                                     "Slice", 
                                                     "Basic Harvest", 
                                                     "SWORD APP Publish V1.3"],
                                        "broker":[],
                                        "distribute":
                                                    ["Resource Data Distribution"],
                                        "publish":
                                                    ["Basic Publish"]}
                                                    
#Create specific gateway node service list.  It saves the user from setting up 
# services that are not available on gateway nodes.  This also avoid the confusion 
# of setting up services as available yet cannot be use since the node was setup 
# as gateway node.
_GATEWAY_NODE_SERVICES ={"administrative":
                                                    ["Network Node Description", 
                                                     "Network Node Services", 
                                                     "Network Node Status", 
                                                     "Resource Distribution Network Policy"],
                                        "distribute":
                                                    ["Resource Data Distribution"]
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
                    raise(e)
                else:
                    print ("\n\n--Cannot find custom plugin for: '{0}:{1}'".format(serviceType, serviceName))
                    publishService(nodeUrl, server, dbname, serviceType, serviceName)

def makeDBPublicReadOnly(server, dbname):
    import couch_utils, os
    from services.service_template import getCouchAppPath

    dba_url = nodeSetup['couchDBUrlDBA']
    db = server[dbname]

    # Add doc change handler
    couch_utils.pushCouchApp(os.path.join(getCouchAppPath(),"resource_data","apps","restrict-writers"), "%s/%s" % (dba_url, dbname))

    # Add security object
    _, _, exist_sec_obj = db.resource.get_json('_security')

    sec_obj = {
        "admins": {
            "names": [],
            "roles": []
        },
        "readers": {
            "names": [],
            "roles": []
        }
    }
    
    sec_obj.update(exist_sec_obj)

    parts = urlparse.urlsplit(dba_url)
    if (hasattr(parts,'username') and parts.username is not None 
        and parts.username not in sec_obj["admins"]["roles"]):
        sec_obj["admins"]["names"].append(parts.username)

    db = server[dbname]
    _, _, result = db.resource.put_json('_security', sec_obj)
    print json.dumps(result)


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
 
def writeConfig():
    destConfigfile = open(_PYLONS_CONFIG_DEST, 'w')
    _config.write(destConfigfile)
    destConfigfile.close()

def setConfigFile(nodeSetup):
    
    #create a copy of the existing config file as to not overide it.
    if os.path.exists(_PYLONS_CONFIG_DEST):
        backup = _PYLONS_CONFIG_DEST+".backup"
        print("\nMove existing {0} to {1}".format(_PYLONS_CONFIG_DEST, backup))
        shutil.copyfile(_PYLONS_CONFIG_DEST, backup)

    #Update pylons config file to use the couchdb url
    _config.set("app:main", "couchdb.url", nodeSetup['couchDBUrl'])
    _config.set("app:main", "couchdb.url.dbadmin", nodeSetup['couchDBUrlDBA'])

    # set the url to for destribute/replication (that is the url that a source couchdb node
    # will use for replication.
    _config.set("app:main", "lr.distribute_resource_data_url",  nodeSetup['distributeResourceDataUrl'])
    _config.set("app:main", "lr.distribute_incoming_url", nodeSetup['distributeIncomingUrl'])
    if server.version() < "1.1.0":
        _config.set("app:main", "couchdb.stale.flag", "OK")
        
    writeConfig()
      
      #Re-read the database info to make we have the correct urls
    global _RESOURCE_DATA, _NODE, _COMMUNITY, _NETWORK, _INCOMING
    _config.read(_PYLONS_CONFIG_DEST)
    _RESOURCE_DATA = _config.get("app:main", "couchdb.db.resourcedata")
    _NODE = _config.get("app:main", "couchdb.db.node")
    _COMMUNITY = _config.get("app:main", "couchdb.db.community")
    _NETWORK = _config.get("app:main", "couchdb.db.network")
    try:
        _INCOMING = _config.get("app:main", "couchdb.db.incoming")
    except:
        _INCOMING = 'incoming'

def writeNGINXConfig(setupInfo, filename):
    print("##############################################")
    print("### NGINX Site Configuration #################")
    
    nginx_cfg = nginx_util.getNGINXSiteConfig(setupInfo, _config)
    print nginx_cfg
    print("##############################################")

    with open(filename, "w") as f:
        f.truncate(0)
        f.flush()
        f.write(nginx_cfg)
        f.close()
        print ("### Site configuration written to: %s" % filename)
        print ("### For most installations you should copy this to /etc/nginx/sites-available then")
        print ("###   ln -s /etc/nginx/sites-available /etc/nginx/sites-enabled")
        print ("### and then subsequently restart or reload nginx")

if __name__ == "__main__":

    from optparse import OptionParser
    import os
    
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
    
    parser = OptionParser()
    parser.add_option("-d", "--devel", dest="devel", action="store_true", default=False,
                      help="Development mode allows the setting of network and community.",
                    )
    parser.add_option("-r", "--response", dest="response_file", default=None,
                      help="Specify a filename for writing a response_file to input.")
    (options, args) = parser.parse_args()
    print("\n\n=========================\nNode Configuration\n")
    if options.devel:
        setCommunityId()
        setNetworkId()
    
    if options.response_file:
        print("Saving a response file to: {0}".format(options.response_file))
        response_file.set(options.response_file)

    nodeSetup = getSetupInfo()
    print("\n\n=========================\nNode Configuration\n")
    for k in nodeSetup.keys():
        print("{0}:  {1}".format(k, nodeSetup[k]))


    server =  couchdb.Server(url= nodeSetup['couchDBUrlDBA'])
    setConfigFile(nodeSetup)
    

    #Create the databases.
    CreateDB(server, dblist=[_RESOURCE_DATA])
    CreateDB(server, dblist=[_INCOMING])
    
    #Delete the existing databases
    CreateDB(server, dblist=[ _NODE, _NETWORK, _COMMUNITY], deleteDB=True)
    
      #Install the services, by default all the services are installed.
    services = _DEFAULT_SERVICES
    if nodeSetup['gateway_node']:
        services = _GATEWAY_NODE_SERVICES
    publishNodeServices(nodeSetup["nodeUrl"], server, _NODE, services)
    
    if setNodeSigning(server, _config, nodeSetup):
        writeConfig()


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

    #make resource data publicly read only
    makeDBPublicReadOnly(server, _RESOURCE_DATA)

    #provide a basic NGINX site configuraition
    writeNGINXConfig(nodeSetup, "learningregistry.conf")

    response_file.close()

