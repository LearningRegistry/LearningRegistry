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
from resource_data import ResourceDataModel
from node_filter import NodeFilterModel, defaultCouchServer, appConfig

def dictToObject(dictionary):
    class DictToObject(object):
        def __init__(self, data):
            self.data = data
        def __getattr__(self, name):
            if  isinstance(self.data, dict) and name in self.data.keys():
                return self.data[name]
            else:
                raise AttributeError()
    return DictToObject(dictionary)
    
class LRNodeModel(object):
    """Class that models a learning registry node"""
    def __init__(self, data):
        
        self._config = {}
        self._communityDescription = None
        self._networkDescription = None
        self._filterDescription = None
        self._nodeStatus = None
        config = data
        
        if isinstance(data, dict):
            config = dictToObject(data)
            
        # Check first if node description is set. if not look for in the DB if not in the db
        # create it from the config and save the db.
        
        self._communityDescription = self._initModel(CommunityModel, 
                                        config.community_description['community_id'],
                                        config.community_description)
        self._config['community_description'] = config.community_description
        
        self._networkDescription = self._initModel(NetworkModel, 
                                                                config.network_description['network_id'],
                                                                config.network_description)
        self._config['network_description'] = config.network_description
        
        self._nodeDescription = self._initModel(NodeModel, 
                                                                      config.node_description['node_id'],
                                                                      config.node_description)
        self._config['node_description'] = config.node_description
        
        self._networkDistributionPolicy = self._initModel(NetworkPolicyModel, 
                                                                    config.network_policy_description['policy_id'],
                                                                    config.network_policy_description)
        self._config['network_policy_description'] = config.network_policy_description
        
        self._nodeServices = []
        self._config['node_services'] =   config.node_services
    
        for service in config.node_services:
            self._nodeServices.append(self._initModel(NodeServiceModel,
                                                                     service['service_id'],
                                                                     service))
        
        filterDescriptionId = self._nodeDescription.node_id+"_filter"
        filters = None
        try:
            filters = config.node_filter_description
            self._config['node_filter_description'] =filters
        except AttributeError:
            #There no filter for the node
            pass
        if filters is not None:
            self._filterDescription = self._initModel(NodeFilterModel, 
                                                                     filterDescriptionId,
                                                                    config.node_filter_description)
        
        self._connections = []
        connections = None
        try:
            connections = config.node_connectivity
        except AttributeError:
            # The node does not have any connections
            pass
        if connections is not None:
            for connection in connections:
                self._connections.append(self._initModel(NodeConnectivityModel,
                                                                                connection['connection_id'],
                                                                                connection))
        self._setNodeStatus() 
        
    def _initModel(self, modelClass, modelId, modelConf):
        modelDoc = modelClass.get(modelId)
        if modelDoc is None:
            model = modelClass(modelConf)
            model.save(doc_id=modelId)
            return model
        else:
            return modelClass(modelDoc)
     
    def _setNodeStatus(self):
        nodeStatus = None
        nodeStatusId = "status_"+self._nodeDescription.node_id
        nodeStatus = NodeStatusModel.get(nodeStatusId)
        if nodeStatus is None:
            statusData = NodeStatusModel()
            statusData.active = self.nodeDescription.active
            statusData.node_id = self.nodeDescription.node_id
            statusData.node_name = self.nodeDescription.node_name
            statusData.start_time = str(datetime.utcnow())
            statusData.install_time = statusData.start_time
            statusData.save(doc_id = nodeStatusId)
        else:
            nodeStatus = NodeStatusModel(nodeStatus)
            nodeStatus.start_time = str(datetime.utcnow())
            nodeStatus.update()
        self._nodeStatus = nodeStatus
          
    def _getStatusDescription(self):
        statusData = {'doc_count': ResourceDataModel._defaultDB.info()['doc_count'],
                                'timestamp': str(datetime.utcnow())}
        statusData.update(self._nodeStatus.specData)
        return statusData
        
        
    def isServiceAvailable(self, serviceType):
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
    config = property(lambda self: dict(self._config), None, None, None)
    connections = property(lambda self: self._connections[:], None, None, None)
    nodeServices = property(lambda self: self._nodeServices[:], None, None, None)
    
    status = property(_getStatusDescription, None, None, None)


