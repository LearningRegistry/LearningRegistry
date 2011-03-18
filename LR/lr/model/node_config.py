#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 10, 2011

Base model class for learning registry data model

@author: jpoyau
'''
import sys
from network import NetworkModel
from community import CommunityModel
from node import NodeModel
from node_status import NodeStatusModel
from datetime import datetime

from node_filter import NodeFilterModel, defaultCouchServer, appConfig

NODE_DESCRIPTION_CONFIG = appConfig['init.node.description']
NETWORK_DESCRIPTION_CONFIG = appConfig['init.network.description']
COMMUNITY_DESCRIPTION_CONFIG = appConfig['init.community.description']
FILTER_DESCRIPTION_CONFIG =appConfig['init.filter.description']


class LRNode(object):
    def __init__(self):
        self._nodeDescription = None
        self._networkDescription = None
        self._communityDescription = None
        self._filterDescription = None
        self._statusDescription = None
        
    def _setNodeDescription(self, node):
        if isinstance(node, NodeModel):
            self._nodeDescription = node
        else:
            self._nodeDescription = NodeModel(node)
            
    def _getNodeDescription(self):
        if self._nodeDescription is None:
            self._nodeDescription = NodeModel(NODE_DESCRIPTION_CONFIG)
            self._nodeDescription.save()
        return self._nodeDescription
        
    def _setNetworkDescription(self, network):
        if isinstance(network, NetworkModel):
            self._networkDescription = network
        else:
            self._networkDescription = NetworkModel(network)
            
    def _getNetworkDescription(self):
        if self._networkDescription is None:
            self._networkDescription = NetworkModel(NETWORK_DESCRIPTION_CONFIG)
            self._networkDescription.save()
        return self._networkDescription
        
    def _setCommunityDescription(self, community):
        if isinstance(community, CommunityModel):
            self._communityDescription = community
        else:
            self._communityDescription = CommunityModel(community)

            
    def _getCommunityDescription(self):
        if self._communityDescription is None:
            self._communityDescription = CommunityModel(COMMUNITY_DESCRIPTION_CONFIG)
            self._communityDescription.save()
        return self._networkDescription
        
    def _setFilterDescription(self, filter_desc):
        if isinstance(filter_desc, NodeFilterModel):
            self._filterDescription = node
        else:
            self._filterDescription = NodeFilterModel(community)
            
    def _getFilterDescription(self):
        if self._filterDescription is None:
            self._filterDescription = NodeFilterModel(FILTER_DESCRIPTION_CONFIG)
            self._filterDescription.save()
        return self._filterDescription
    
    def _setStatusDescription(self, status_desc):
        if isinstance(status_desc, NodeStatusModel):
            self._statusDescription = status_desc
        else:
            self._statusDescription = NodeStatusModel(community)
            
    def _getStatusDescription(self):
        if self._statusDescription is None:
            self._statusDescription = NodeStatusModel()
            self._statusDescription.active = self.nodeDescription.active 
            self._statusDescription.node_id = self.nodeDescription.node_id
            self._filterDescription.save()
            
        self._statusDescription.timestamp = str(datetimquite.now())
        return self._statusDescription
    
    
    nodeDescription = property(_getNodeDescription, _setNodeDescription, None, None)
    networkDescription = property(_getNetworkDescription, _setNetworkDescription, None, None)
    communityDescription = property(_getCommunityDescription, _setCommunityDescription, None, None)
    filterDescription = property(_getFilterDescription, _setFilterDescription, None, None)
    status = property(_getStatusDescription, None, None, None)
            
            

            


