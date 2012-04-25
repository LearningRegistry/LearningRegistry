#!/usr/bin/env python
#    Copyright 2011 Lockheed Martin
#
'''
Created on Nov 11, 2011

@author: jpoyau
'''
from lr_node import Node

import os
from os import path
import ConfigParser
import json
from time import sleep
import pprint

_PWD = path.abspath(path.dirname(__file__))
_TEST_DATA_PATH = path.abspath(path.join(_PWD, "../../data/nsdl_dc/data-000000000.json"))
_TEST_NODE_CONFIG_DIR = path.abspath(path.join(_PWD, "config"))



_NODES = []
_COMMUNITIES = {}
_GATEWAYS =[]
_CONNECTIONS = []
_DISTRIBUTE_ORDER = []
_DATA = None

def generateNodeConfig(numberOfNodes):
    
    nodeConfigs = {}
    for i in range(0, numberOfNodes):
        nodeName = "test_node_"+str(i)
        port = str(5001+i)
        config = ConfigParser.ConfigParser()
        #Create the sections
        config.add_section('couch_info')
        config.add_section('pylons_server')
        config.add_section('node_config')
        #Set the node url
        config.set("node_config", "node_url",  "http://localhost:"+port)
        #Set the pylons server stuff
        config.set("pylons_server", "port", port)
        config.set("pylons_server", "use", "egg:Paste#http")
        #Set the couchdb sutff
        config.set("couch_info", "server",  "http://localhost:5984")
        config.set("couch_info", "resourcedata", nodeName+"_resource_data")
        config.set("couch_info", "community", nodeName+"_community")
        config.set("couch_info", "node",  nodeName+"_node")
        config.set("couch_info", "network",  nodeName+"_network")
        config.set("couch_info", "incoming", nodeName+"_incoming")
        
        nodeConfigs[nodeName] = config
    return nodeConfigs

def createNodes(numberOfNodes):
    nodes = {}
    configs = generateNodeConfig(numberOfNodes)
    #Make sure the node name matches the index.  Make it easier for debugging.
    for c in sorted(configs, key=lambda k: int(k.split('_')[-1])):
        node =Node(configs[c], c)
        nodes[c] = node
        _NODES.append( node)
    return nodes

def createCommunity(communityName, networkName, nodes):
    for node in nodes:
        node.setCommunityId(communityId)
        node.setNetworkId(networkId)

def setCommunity(community):
    for network in community["networks"]:
        for node in community["networks"][network]:
            node.setCommunityInfo(community["communityId"], community["social_community"])
            node.setNetworkInfo(network)

def createNetwork():
    nodes = createNodes(15)
    global _NODES, _COMMUNITIES, _GATEWAYS, _CONNECTIONS, _DISTRIBUTE_ORDER, _DATA
    n = _NODES
    openCommunityOne = {"communityId": "Open Community One",
                                            "networks":
                                                {
                                                    "OC1_N1":n[0:2],
                                                    "OC1_N2":n[2:6]
                                                 },
                                            "social_community": True
                                            }
                                            
    openCommunityTwo ={ "communityId": "Open Community Two",
                                            "networks":
                                                {
                                                    "OC2_N1":n[6:10],
                                                    "OC2_N2":n[10:13]
                                                 },
                                            "social_community": True
                                            }
                                            
    closedCommunity = { "communityId":"Closed Community",
                                            "networks":
                                                {
                                                    "CC2_N1":n[13:],
                                                 },
                                            "social_community": False
                                    }
    communities =[openCommunityOne, openCommunityTwo, closedCommunity]
    _COMMUNITIES = communities
  
    
    gateways =[n[0], n[3], n[4],n[5], n[7], n[8], n[9], n[12],n[13]]
    _GATEWAYS = gateways
    F= assertNoDistribute
    S=assertSucessDistribute
    #Add the essert test function to each of the connection destination to test.
    connections ={n[0]:{n[1]: S},
                            
                            n[1]:{},
                            
                            n[2]:{n[0]:F, 
                                     n[3]:S, 
                                     n[4]:S, 
                                     n[5]:S},
                                     
                            n[3]:{n[13]:F,
                                     n[0]:S, 
                                     n[6]:F},
                            
                            n[4]:{n[7]:S, 
                                     n[3]:F},
                                    
                            n[5]:{n[5]:F, 
                                     n[0]:S},
                            
                            n[6]:{n[8]:S, 
                                     n[9]:S,
                                    },
                            
                            n[7]:{n[4]:S, 
                                     n[6]:S},
                                     
                            n[8]:{n[6]:S, 
                                    n[12]:S},
                                    
                            n[9]:{n[13]:F},
                            
                            n[10]:{},
                            
                            n[11]:{n[10]:S,},
                            
                            n[12]:{n[10]:S,
                                       n[11]:S},
                            
                            n[13]:{n[14]:S},
                            
                            n[14]:{n[13]:S}
                            }
    _CONNECTIONS = connections
    #Use the distribute order to have the gateway nodes starts for so that
    # the data can get propagated throughout the network
    _DISTRIBUTE_ORDER =[2, 3, 4, 5, 0, 7, 6,  8, 12, 13, 9, 14, 11, 10, 1]
    
    for community in communities:
        setCommunity(community)
    
    #set the gateway nodes.
    for node in gateways:
         node.setNodeInfo(isGateway=True)
    
    #create node connections.
    for node in connections:
        for destination in connections[node]:
            gatewayConnection = ((destination  in gateways) or (node in gateways))
            node.addConnectionTo(destination._getNodeUrl(), gatewayConnection)
    
    #Populate node[2, 6, 9] as the seed nodes.
    _DATA = json.load(file(_TEST_DATA_PATH))
    n[2].publishResourceData(_DATA["documents"])


def getNodeDistributeResults(sourceNode, destinationNode):
    distributeResultsList = []
    for distributeResults in sourceNode._distributeResultsList:
            if ('connections'  in distributeResults) == False:
                continue
            for connectionResults in distributeResults['connections']:
                if connectionResults['destinationNodeInfo']['node_id'] == destinationNode.nodeId:
                    distributeResultsList.append(connectionResults)
    return distributeResultsList
    
__OK = 'ok'
__ERROR = 'error'
__REPLICATION_RESULTS = 'replication_results'
__CONNECTIONS = 'connections'
        
def assertSucessDistribute(sourceNode, destinationNode):
    for results in getNodeDistributeResults(sourceNode, destinationNode):
        assert (results[__OK] and 
                      results[__REPLICATION_RESULTS][__OK]),  \
                      "failed to processed replication/distribute:\n{0}".format(pprint.pformat(response))
        assert sourceNode.compareDistributedResources(destinationNode), \
                    """Distribute failed all source node documents are Not at destination node.\n{0}""".format(pprint.pformat(results, 4))

def assertNoDistribute(sourceNode, destinationNode):
    for results in getNodeDistributeResults(sourceNode, destinationNode):
        assert (not results[__OK] and 
                      not (__REPLICATION_RESULTS in results)),  \
                      "failed to processed replication/distribute:\n{0}".format(pprint.pformat(results))

def assertNodeDistributeResults(sourceNode):
    for destinationNode in _CONNECTIONS[sourceNode].keys():
        destinationNode.waitOnChangeMonitor()
        _CONNECTIONS[sourceNode][destinationNode](sourceNode, destinationNode)

    
def  startNodes():
    for node in _NODES:
        node.start()

def doNodesDistribute():
    for n in _DISTRIBUTE_ORDER:
        print("\n\n==========Node {0} distribute results==========".format(_NODES[n]._nodeName))
        results = _NODES[n].distribute()
        assert (len(_CONNECTIONS[_NODES[n]]) == 0 or 
                      len(results['connections']) == len(_CONNECTIONS[_NODES[n]])), "Missing connection results"
        assertNodeDistributeResults(_NODES[n])
        sleep(5)

def testLargeNetwork():
    createNetwork()
    startNodes()
    doNodesDistribute()
    

def teardown():
    for node in _NODES:
        node.tearDown()
