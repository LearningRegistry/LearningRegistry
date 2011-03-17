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
from network_policy import NetworkPolicyModel
from node_connectivity import NodeConnectivityModel
from node_service import NodeServiceModel
from datetime import datetime

from node_filter import NodeFilterModel, defaultCouchServer, appConfig

class LRNode(object):
    """Class that models a learning registry node"""
    def __init__(self, config):
        
        self._communityDescription = None
        self._networkDescription = None
        self._filterDescription = None
        
        # Check first if node description is set. if not look for in the DB if not in the db
        # create it from the config and save the db.
        self._communityDescription = self._initModel(CommunityModel, 
                                        config.community_description['community_id'],
                                        config.community_description)
        
        self._networkDescription = self._initModel(NetworkModel, 
                                                                config.network_description['network_id'],
                                                                config.network_description)
        
        self._nodeDescription = self._initModel(NodeModel, 
                                                                      config.node_description['node_id'],
                                                                      config.node_description)
                                                                      
        self._networkDistributionPolicy = self._initModel(NetworkPolicyModel, 
                                                                    config.network_policy_description['policy_id'],
                                                                    config.network_policy_description)
                                                                    
        filterDescriptionId = self._nodeDescription.node_id+"_filter"
        self._filterDescription = self._initModel(NodeFilterModel, 
                                                                     filterDescriptionId,
                                                                    config.node_filter_description)
        
        self._nodeServices = []
        for service in config.node_services:
            self._nodeServices.append(self._initModel(NodeServiceModel,
                                                                     service['service_id'],
                                                                     service))
     
    def _initModel(self, modelClass, modelId, modelConf):
        modelDoc = modelClass.get(modelId)
        if modelDoc is None:
            model = modelClass(modelConf)
            model.save(doc_id=modelId)
            return model
        else:
            return modelClass(modelDoc)
            
    def _getStatusDescription(self):
        pass
        
    def IsServiceAvailable(self, serviceType):
        """Method to test if serviceType is available """
        for service in self._nodeServices:
            if service.active == True and serviceType == service.service_type:
                return True
        return False
    
    nodeDescription = property(lambda self: self._nodeDescription, None, None, None)
    networkDescription = property(lambda self: self._networkDescription, None, None, None)
    communityDescription = property(lambda self: self._communityDescription, None, None, None)
    filterDescription = property(lambda self: self._filterDescription, None, None, None)
    networkPolicyDescription = property(lambda self: self._networkPolicyt, None, None, None)
    status = property(_getStatusDescription, None, None, None)


