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
    
    connections ={n[0]:[n[1]],
                            n[1]:[],
                            n[2]:[n[0], n[3], n[4], n[5]],
                            n[3]:[n[13], n[0], n[6]],
                            n[4]:[n[7], n[3]],
                            n[5]:[n[5], n[0]],
                            n[6]:[n[8], n[9], n[10]],
                            n[7]:[n[4], n[6]],
                            n[8]:[n[6], n[12]],
                            n[9]:[n[13]],
                            n[10]:[],
                            n[11]:[n[10]],
                            n[12]:[n[10]],
                            n[13]:[n[14]],
                            n[14]:[n[13]]
                            }
    _CONNECTIONS = connections
    #Use the distribute order to have the gateway nodes starts for so that
    # the data can get propagated throughout the network
    _DISTRIBUTE_ORDER =[2, 0, 3, 4, 5, 7, 6,  8, 12, 13, 9, 10, 14, 11, 1]
    
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
    
    #Poluate node[2] as the seed node.
    _DATA = json.load(file(_TEST_DATA_PATH))
    n[2].publishResourceData(_DATA["documents"])
    
def firstLevelDistribute():
    #Start the test by starting with the source 
    _NODES[2].start()
    #sleep for little  to let the node create teh distributable data
    sleep(20)
    #Start the nodes that are connectioned to  the first started node.
    for n in _CONNECTIONS[_NODES[2]]:
        n.start()
    
    #Now distribute
    results = _NODES[2].distribute()
    sleep(30)
    #First check to make sure the number of connections results matches the
    #number of connections.
    assert len(results['connections']) == len(_CONNECTIONS[_NODES[2]]), "Missing connection results"
    assert results['ok'] == True, "Distribute Failed"
    for result in results['connections']:
        #Node[0] is gateway node in a different network distribute should fail
        node_index = int(result['connection_id'].split(':')[-1].split('_')[0])-5001
        if result['destinationNodeInfo']['resource_data_url'].find(_NODES[0]._nodeName) != -1:
            assert not result['ok'], "Fail,  should be no distribute  to node {0}..." .format(_NODES[node_index]._nodeName)
            assert not result.has_key('replication_results'), "Fail there should be no replication".format(_NODES[node_index]._nodeName)
            assert result.has_key('error') and result['error'] == 'cannot distribute across networks (or communities) unless gateway', "Fail, {0} there should and error ...".format(_NODES[node_index]._nodeName)
        else:
            assert result['ok'], "Distribute to node {0} failed".format(_NODES[node_index]._nodeName)
            assert result.has_key('replication_results') and  result['replication_results']['ok'], "Replication to node{0} failed".format(_NODES[node_index]._nodeName)
            assert _NODES[2].compareDistributedResources(_NODES[node_index]), "Documents distribute to node {0} failed".format(_NODES[node_index]._nodeName)

def secondLevelDistribute():
    for node in _CONNECTIONS[_NODES[2]]:
        for destinationNode in   _CONNECTIONS[node]:
            destinationNode.start()

    for node in _CONNECTIONS[_NODES[2]]:
        node.distribute(True)
    
def  startNodes():
    for node in _NODES:
        node.start()

def doNodesDistribute():
    for n in _DISTRIBUTE_ORDER:
        print("\n\n==========Node {0} distribute results==========".format(_NODES[n]._nodeName))
        _NODES[n].distribute()
        sleep(5)

def destroyNetwork():
    for node in _NODES:
        node.tearDown()
    _NODES.clear()
    #keep around the replication document so that I can all the replication info can
    # be deleted.  It seems like the replicator database will not do replication if the
    # source and target node is already in the dabatase as completed document,
    # eventhough source and target are new document.

def testLargeNetwork():
    createNetwork()
    firstLevelDistribute()
