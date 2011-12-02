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

_PWD = path.abspath(path.dirname(__file__))
_TEST_DATA_PATH = path.abspath(path.join(_PWD, "../../data/nsdl_dc/data-000000000.json"))
_TEST_NODE_CONFIG_DIR = path.abspath(path.join(_PWD, "config"))

class TestDistribute(object):
    
    @classmethod 
    def setupClass(cls):
        # For now grab the two node configuration files one source and one destination.
        # To test distribute.
        cls._NODES = []
        for c in os.listdir(_TEST_NODE_CONFIG_DIR):
            config = ConfigParser.ConfigParser()
            config.read(path.join(_TEST_NODE_CONFIG_DIR, c))
            cls._NODES.append(Node(config, "Test_Node_{0}".format(len(cls._NODES)+1)))
    
    @classmethod
    def tearDownClass(cls):
        for node in cls._NODES:
            node.tearDown()

    def __init__(self):
        self._sourceNodes = []
        self._destinationNodes = []


    def setUp(self):
        for node in self._NODES:
            node.stop()
            node.resetResourceData()
       
        
    def _setupNodePair(self, sourceNode, destinationNode, 
                                    sourceCommunityId="DistributeTestCommunity",
                                    destinationCommunityId="DistributeTestCommunity",
                                    sourceNetworkId="DistributeTestNetwork",
                                    destinationNetworkId="DistributeTestNetwork",
                                    sourceIsSocialCommunity=True,
                                    destinationIsSocialCommunity=True,
                                    sourceIsGateway = False,
                                    destinationIsGateway = False,
                                    sourceIsActive = True,
                                    destinationIsActive = True,
                                    destinationFilter = None,
                                    isGatewayConnection=None):
        #Set the community id
        sourceNode.setCommunityInfo(sourceCommunityId, sourceIsSocialCommunity)
        destinationNode.setCommunityInfo(destinationCommunityId, destinationIsSocialCommunity)
        
        #set the network id
        sourceNode.setNetworkInfo( sourceNetworkId)
        destinationNode.setNetworkInfo(destinationNetworkId)
        
        #set gateway info.
        sourceNode.setNodeInfo(isGateway=sourceIsGateway, isActive=sourceIsActive)
        destinationNode.setNodeInfo(isGateway=destinationIsGateway, isActive=destinationIsActive)
        
        #set destination node filter
        if(destinationFilter is not None):
            destinationNode.setFilterInfo(**destinationFilter)
        
        #add the destination node as connection to the source node.
        if isinstance(isGatewayConnection, bool):
            sourceNode.addConnectionTo(destinationNode._getNodeUrl(), isGatewayConnection)
        else:
            sourceNode.addConnectionTo(destinationNode._getNodeUrl(), (sourceIsGateway or destinationIsGateway))

    def _doDistributeTest(self, sourceNode, destinationNode):
        #start the node nodes.
        sourceNode.start()
        destinationNode.start()
        sleep(30)
        #Do the distribute
        sourceNode.distribute()
        # Wait for two minutes or that that all the document and be transfer to test that
        # there are indeed distributed correctly
        sleep(30)
        
    def test_common_nodes_same_network_community_no_filter(self):
        """ This tests distribute/replication between to common nodes on the same
            network.  There is no filter on the destination node. Distribution/replication 
            is expected to the successful.
        """
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        self._setupNodePair(sourceNode, destinationNode )
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        assert sourceNode.compareDistributedResources(destinationNode), \
                    """Distribute between two common nodes on the same network and 
                    community and no filter on the destination node."""


    def test_gatewaynodes_on_different_open_communities(self):
        """ This tests distribute/replication between to gateway nodes on different
            networks and community.  There is no filter on destination node.
            Distribution/replication is expected to be successful.
        """
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        self._setupNodePair(sourceNode, destinationNode, 
                                        sourceCommunityId="Test Source Community",
                                        destinationNetworkId="Test Source Network",
                                        sourceIsGateway =True,
                                        destinationIsGateway=True )
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        assert sourceNode.compareDistributedResources(destinationNode), \
                    """Distribute between two gateway nodes on different community
                    and network and no filter on the destination node."""


    def test_gatewaynodes_on_same_communities_different_network(self):
        """ This tests distribute/replication between to gateway nodes on the same
            communities but different network.  There is no filter on the destionation node.
             Distribution/replication is expected to 
            be successful.
        """
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        self._setupNodePair(sourceNode, destinationNode, 
                                        destinationNetworkId="Test Source Network",
                                        sourceIsGateway =True,
                                        destinationIsGateway=True )
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        assert sourceNode.compareDistributedResources(destinationNode), \
                    """Distribute between two gateway nodes on the same community but
                    different network and no filter on the destination node."""


    def _setup_common_nodes_same_network_and_community_filter(self, 
            include_exclude=True, 
            count=50,
            mode=5):
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        filterDescription = {"include_exclude": include_exclude,
                                        "filter":[{"filter_key":"keys", 
                                                    "filter_value":"Filter Me In"},
                                                    {"filter_key":"active", 
                                                    "filter_value":"True"},
                                                    ]}
        self._setupNodePair(sourceNode, destinationNode, destinationFilter=filterDescription)
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        #Add some marker documents that will be filter in.
        for i in range(count):
            data["documents"][i]["keys"].append("Filter Me In")
            if i % mode == 0:
                data["documents"][i]["active"] = False
                
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        
        assert sourceNode.compareDistributedResources(destinationNode, 
                                                                            destinationNode._nodeFilterDescription), \
                    """Distribute between to common nodes on the same network and 
                    community with an include_exclude filter on the destination node."""


    def test_common_nodes_same_network_community_with_filter_in(self):
        """ This tests distribute/replication between two common nodes on the same
            network and community.  There is an include filter on the destionation.
             Distribution/replication is expected to the successful. Only the filtered
             documents should get replicated/distributed to the destination node.
        """
        self._setup_common_nodes_same_network_and_community_filter()
    
        
    def test_common_nodes_same_network_community_with_filter_out(self):
        """ This tests distribute/replication between two common nodes on the same
            network and community.  There is one exclude filter on the destionation.
             Distribution/replication is expected to the successful. Only the filtered
             documents should get replication on the destination node.
        """
        self._setup_common_nodes_same_network_and_community_filter(include_exclude=False, count=100,  mode=2)


    def test_gateway_to_common_node(self):
        """ This tests distribute/replication between a source gateway node on to a
            common node.  There  should be NO distribution/replication.  Distribution
            is not allowed between a gateway and common node.
        """
        
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        self._setupNodePair(sourceNode, destinationNode, 
                                        sourceIsGateway =True)
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        # There should be no replication. Destination node should be 
        # empty of resource_data docs
        assert len (destinationNode.getResourceDataDocs()) == 0, \
                    """There  should be NO distribution/replication.  Distribution
            is not allowed between a gateway and common node."""

    def test_gateway_to_gateway_closed_community(self):
        """Tests distribute between to gateway with one close community. 
        Replication distribute should not happen """
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        self._setupNodePair(sourceNode, destinationNode, 
                                        sourceCommunityId="Closed Source Community Id",
                                        sourceNetworkId = "Closed Source NetworkId",
                                        destinationIsGateway = True,
                                        sourceIsSocialCommunity = False,
                                        sourceIsGateway =True)
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        # There should be no replication. Destination node should be 
        # empty of resource_data docs
        assert len (destinationNode.getResourceDataDocs()) == 0, \
                """There  should be NO distribution/replication.  Distribution
            is not allowed between gateway nodes on closed network."""


    def test_common_to_gateway_same_community_and_network(self):
        """ This tests distribute/replication between common node to a gateway 
            common node.  distribution/replication should work.
        """
        
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        self._setupNodePair(sourceNode, destinationNode, 
                                        destinationIsGateway =True,
                                        isGatewayConnection=True)
        
        #populate the node with test data.
        data = json.load(file(_TEST_DATA_PATH))
        sourceNode.publishResourceData(data["documents"])
        self._doDistributeTest(sourceNode, destinationNode)
        # There should be no replication. Destination node should be 
        # empty of resource_data docs
        assert sourceNode.compareDistributedResources(destinationNode), \
                    """Distribution from a common node to gateway node should work"""


    def test_source_node_with_more_than_two_gateway_connections(self):
        """Test source node with more than on gateway connections.  There should
            be no replication/distribute.  The node connection are invalid"""
        
        sourceNode =self._NODES[0]
        destinationNode = self._NODES[1]
        
        self._setupNodePair(sourceNode, destinationNode, 
                                        destinationIsGateway =True)
        sourceNode.addConnectionTo(destinationNode._getNodeUrl(), True) 
        sourceNode.addConnectionTo("http://fake.node.org",  True)
        
        # There should be no replication. Destination node should be 
        # empty of resource_data docs
        assert len (destinationNode.getResourceDataDocs()) == 0, \
                """There  should be NO distribution/replication.  Source node connections
                are invalid"""
