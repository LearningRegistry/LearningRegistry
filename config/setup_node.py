#!/usr/bin/python
#    Copyright 2011 Lockheed Martin
# 

#
#Simple script to setup and initialize a learning registry node documents and
# commit to a specified coudbserver.
#

import ConfigParser, os
import couchdb
import sys
import json
import urlparse

import lrnodetemplate as t
from uuid import uuid4

c = __import__("setup-couch-db")

_PYLONS_CONFIG = '../LR/development.ini'
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG)

_DEFAULT_COUCHDB_URL =  "http://localhost:5984/"

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
            
            
def getSetupInfo():
    """Get the user node info"""
    nodeSetup = {}
    couchDBUrl  = getInput("Enter your couchDB server URL",  
                                            None, testCouchServer)
                                            
    nodeSetup['couchDBUrl'] = couchDBUrl
    
    nodeName = getInput("Enter your node name", "Node@{0}".format(couchDBUrl))
    nodeSetup['node_name'] = nodeName
    
    nodeDescription = getInput("Enter your node description", nodeName)
    nodeSetup['node_description'] = nodeDescription
    
    adminUrl = getInput("Enter node admin URL", 
                                    "{0}.node.admin@learningregistry.org".format(couchDBUrl))
    nodeSetup['node_admin_url'] = adminUrl
                                    
    distributeTargets = getInput("Enter the URLs of nodes that you wish to distribute to",
                                                 "")
    nodeSetup['connections'] = distributeTargets.split()
    
    isNodeOpen = getInput('Is the  node "open" (T/F)', 'T')
    nodeSetup['open_connect_source']  = (isNodeOpen=='T')
    
    isDistributeDest = getInput("Does the node want to be the destination for replication (T/F)", 'T')
    nodeSetup['open_connect_dest'] =(isDistributeDest =='T')
    return nodeSetup
    
    
if __name__ == "__main__":
    
    from optparse import OptionParser
    import os
    
    parser = OptionParser()
    parser.add_option("-d", "--devel", dest="devel", action="store_true", default=False, 
                      help="Development mode allows the setting of network and community.",
                    )
    (options, args) = parser.parse_args()
    print("\n\n=========================\nNode Configuration\n")
    if options.devel:
        community = getInput("Enter the cummunity id")
        t.community_description['community_id'] = community
        t.community_description['community_name'] = community
        t.community_description['community_description'] = community
        t.network_description['community_id'] = community
        t.node_description['community_id'] = community
       
        network = getInput("Enter the network id")
        t.network_description['network_id'] = network
        t.network_description['network_name'] = network
        t.network_description['network_description'] = network
        t.node_description['network_id'] = network
        t.network_policy_description['network_id'] = network
        t.network_policy_description['policy_id'] =network+" policy"
        
        
         
                        
    nodeSetup = getSetupInfo()
    print("\n\n=========================\nNode Configuration\n")
    for k in nodeSetup.keys():
        print("{0}:  {1}".format(k, nodeSetup[k]))
        
    #Update pylons config file to use the couchdb url
    _config.set("app:main", "couchdb.url", nodeSetup['couchDBUrl'])
    configfile = open(_PYLONS_CONFIG, 'w')
    _config.write(configfile)
    configfile.close()
    
    server =  couchdb.Server(url= nodeSetup['couchDBUrl'])
    
    #Create the databases.
    c.CreateDB(server, dblist=[c._RESOURCE_DATA])
    c.CreateDB(server, dblist=[ c._NODE, c._NETWORK, c._COMMUNITY], deleteDB=True)
    
    #Add the network and community description
    c.PublishDoc(c._COMMUNITY, "community_description", t.community_description)
    c.PublishDoc(c._NETWORK,  "network_description", t.network_description)
    policy = {}
    policy.update(t.network_policy_description)
    c.PublishDoc(c._NETWORK,'network_policy_description', policy)
    
    
    #Add node description
    node_description = {}
    node_description.update(t.node_description)
    node_description['node_name'] = nodeSetup['node_name']
    node_description['node_description'] = nodeSetup['node_description']
    node_description['node_admin_url'] = nodeSetup['node_admin_url']
    node_description["open_connect_source"] = nodeSetup["open_connect_source"]
    node_description["open_connect_dest"] = nodeSetup["open_connect_dest"]
    node_description['node_id'] = uuid4().hex
    c.PublishDoc(c._NODE,'node_description',node_description)
    
    for dest_node_url in nodeSetup['connections']:
        connection = {}
        connection.update(t.connection_description)
        connection['connection_id'] = uuid4().hex
        connection['source_node_url']=nodeSetup['couchDBUrl']
        connection['destination_node_url'] = dest_node_url
        c.PublishDoc(c._NODE, "{0}_to_{1}_connection".format(
                                                nodeSetup['node_name'], dest_node_url), connection)
                                                
    
    #Install the services, by default all the services are installed.
    for service_type in ['access', 'broker', 'publish', 'administrative', 'distribute']:
        service = {}
        service.update(t.service_description)
        service['service_type'] =service_type
        service['service_id'] = uuid4().hex
        service['service_name'] = service_type + " service"
        service['service_description']= service_type + " service"
        c.PublishDoc(c._NODE, service_type + " service", service)
        
    
