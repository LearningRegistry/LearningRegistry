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
from resource_data import ResourceDataModel
from node_filter import NodeFilterModel, defaultCouchServer, appConfig
import logging
import threading
import pprint
from lr.lib import helpers as h
import urllib2
from urlparse import urlparse, urlunparse, ParseResult
import json
import atexit
_COUCHDB_FIELDS =['_id', '_rev', 
                                    '_attachments', 
                                    '_deleted', 
                                    '_revisions', 
                                    '_revs_info',
                                    '_conflicts',
                                    '_deleted_conflicts' ]
                                    
log = logging.getLogger(__name__)

_ACCESS_CREDENTIALS_ID = "access_credentials"
class LRNodeModel(object):
    """Class that models a learning registry node"""
    def __init__(self, data):
        self._communityDescription = None
        self._networkDescription = None
        self._nodeStatus = None
 
        if isinstance(data, dict):
            config = h.dictToObject(data)
            
        # Check first if node description is set. if not look for in the DB if not in the db
        # create it from the config data.
        
        self._communityDescription = self._initModel(CommunityModel, 
                                        config.community_description.community_id,
                                        config.community_description)
       
        self._networkDescription = self._initModel(NetworkModel, 
                                                                config.network_description.network_id,
                                                                config.network_description)
        
        self._nodeDescription = self._initModel(NodeModel, 
                                                                      config.node_description.node_id,
                                                                      config.node_description)
        
        self._networkPolicyDescription = self._initModel(NetworkPolicyModel, 
                                                                    config.network_policy_description.policy_id,
                                                                    config.network_policy_description)
        
        self._initServices(config.node_services)
        self._initFilter(config)
        self._initConnections(config)
        self._setNodeStatus() 
        self._initConfig(config)

    def _initModel(self, modelClass, modelId, modelConf):
        #Try to get the model data from the database.
        model = None
        modelDoc = modelClass.get(modelId)
        if modelDoc is None:
            model = modelClass(modelConf)
            return model
        else:
            model = modelClass(modelDoc)
        model.validate()
        return model
    
    def _initFilter(self, config):
        if hasattr(self, '_filterDescription') or not hasattr(config, 'node_filter_description') :
            return
        self._filterDescription = self._initModel(NodeFilterModel, 
                                                                     "Node filter",
                                                                     config.node_filter_description)
        
    def _initConfig(self, config):
        if hasattr(self, "_config"):
            return
        self._config = {}
        self._config['community_description'] = config.community_description
        self._config['network_description'] = config.network_description
        self._config['node_description'] = config.node_description
        self._config['network_policy_description'] = config.network_policy_description
        self._config['node_services'] =   config.node_services
        if hasattr(config, 'node_filter_description'):
            self._config['node_filter_description'] = config.node_filter_description
        
    def _initServices(self, services):
        if hasattr(self, "nodeServices"):
            return
        self._nodeServices = {}
        for service in services:
            serviceModel  =self._initModel(NodeServiceModel,
                                                            service['service_id'],
                                                            service)
            self._nodeServices[serviceModel.service_name] = serviceModel

    def _initConnections(self, config):
        if hasattr(self,  "_connections") or not hasattr(config, "node_connectivity"):
            return
        self._connections = []
        for connection in config.node_connectivity:
            self._connections.append(self._initModel(NodeConnectivityModel,
                                                                                connection['connection_id'],
                                                                                connection))
    
    def _setNodeStatus(self):
        nodeStatus = None
        nodeStatusId = "node status"
        nodeStatus = NodeStatusModel.get(nodeStatusId)
        if nodeStatus is None:
            nodeStatus = NodeStatusModel()
            nodeStatus.active = self.nodeDescription.active
            nodeStatus.node_id = self._nodeDescription.node_id
            nodeStatus.node_name = self.nodeDescription.node_name
            nodeStatus.start_time = h.nowToISO8601Zformat()
            nodeStatus.install_time = nodeStatus.start_time
            nodeStatus.save(doc_id = nodeStatusId)
        else:
            nodeStatus = NodeStatusModel(nodeStatus)
            nodeStatus.start_time = h.nowToISO8601Zformat()
            nodeStatus.update()
        self._nodeStatus = nodeStatus
          
    def _getStatusDescription(self):
        count = 0
        view = ResourceDataModel._defaultDB.view(appConfig['couchdb.db.resourcecount'],stale='ok')
        if len(view.rows) > 0:
            count = view.rows[0].value 
        statusData = {'doc_count': count,
                                'timestamp': h.nowToISO8601Zformat()}
        statusData.update(self._nodeStatus.specData)
        return statusData

    def _getNodeJsonDescription(self):
        description = {'timestamp': h.nowToISO8601Zformat()}
        description.update(self._communityDescription.descriptionDict)
        description.update(self._networkDescription.descriptionDict)
        description.update(self._nodeDescription.descriptionDict)
        description.update(self._networkPolicyDescription.descriptionDict)
        if hasattr(self, '_filterDescription'):
            description['filter'] = self._filterDescription.descriptionDict
        return json.dumps(description, indent=2)
    
    def _getNodeJsonPolicy(self):
        policy = {'timestamp': h.nowToISO8601Zformat()}
        key="network_description"
        if key in self._networkDescription.descriptionDict.keys():
                        policy[key] = self._networkDescription.descriptionDict[key]
        key="network_name"
        if key in self._networkDescription.descriptionDict.keys():
                        policy[key] = self._networkDescription.descriptionDict[key]
        key="node_id"
        if key in self._nodeDescription.descriptionDict.keys():
                        policy[key] = self._nodeDescription.descriptionDict[key]
        key="node_name"
        if key in self._nodeDescription.descriptionDict.keys():
                        policy[key] = self._nodeDescription.descriptionDict[key]
        #    policy.update(self._networkPolicyDescription.descriptionDict)
        policy.update(self._networkPolicyDescription.specData)

        return json.dumps(policy, indent=2)  
      
    def isServiceAvailable(self, service_name):
        """Method to test if serviceType is available """
        return service_name in self._nodeServices and self._nodeServices[service_name].active
     
    
    def _saveConfig(self, model, modeDB=None):
        pass

    def save(self):
        """ Save the node configuration the couchdb database.  The documents will
        be saved to the models default dabase. A document is saved only if 
        it is not already in the database."""

        #Save the model only if it is not already in the database.  It's not in the
        # database if it doesn't have a id.
        if self._nodeDescription is not None and self._nodeDescription.id is None:
            self._nodeDescription.save(doc_id=self._nodeDescription.node_id)
            
        if (self._networkDescription is not None and 
              self._networkDescription.id is None):
            self._networkDescription.save(doc_id=self._networkDescription.network_id)
        
        if (self._communityDescription is not None and 
                self._communityDescription.id is None):
            self._communityDescription.save(
                    doc_id=self._communityDescription.community_id)
        
        if (self._networkPolicyDescription is not None and 
                self._networkPolicyDescription.id is None):
            self._networkPolicyDescription.save(
                            doc_id=self._networkPolicyDescription.policy_id)
        
        if self._connections is not None:
            for c in self._connections:
                if c.id is None:
                    c.save(doc_id=c.connection_id)
       
        if self._nodeServices is not None:
            for s in self._nodeServices:
                if s.id is None:
                    s.save(doc_id=s.service_id)
    
    def saveOrUpdate(self):
        """ Save the node configuration the couchdb database.  The documents will
        be saved to the models default dabase. A document will be updated if 
        it is already in the database."""

        #Save the model only if it is not already in the database.  It's not in the
        # database if it doesn't have a id.
        if self._nodeDescription is not None: 
            if self._nodeDescription.id is None:
                self._nodeDescription.save(doc_id=self._nodeDescription.node_id)
            else:
                self._nodeDescription.update()
                
        if self._networkDescription is not None:
            if self._networkDescription.id is None:
                self._networkDescription.save(doc_id=self._networkDescription.network_id)
            else:
                self._networkDescription.update()
                
        if self._communityDescription is not None: 
                if self._communityDescription.id is None:
                    self._communityDescription.save(
                        doc_id=self._communityDescription.community_id)
                else:
                    self._communityDescription.update()
                    
        if self._networkPolicyDescription is not None:
            if self._networkPolicyDescription.id is None:
                self._networkPolicyDescription.save(
                            doc_id=self._networkPolicyDescription.policy_id)
            else:
                self._networkPolicyDescription.update()
        
        if self._connections is not None:
            for c in self._connections:
                if c.id is None:
                    c.save(doc_id=c.connection_id)
                else:
                    c.update()
       
        if self._nodeServices is not None:
            for s in self._nodeServices:
                if s.id is None:
                    s.save(doc_id=s.service_id)
                else:
                    s.update()

    def getDistributeCredentialFor(self, targetUrl):
        #Get all the passwords for distribute
        if _ACCESS_CREDENTIALS_ID not in NodeModel._defaultDB:
            return None
        #check if we have any credential to access the node url.
        passwords = h.dictToObject(NodeModel._defaultDB[_ACCESS_CREDENTIALS_ID])
        credential = passwords.passwords.get(targetUrl)
        return credential
    
    def getDistributeInfo(self):
        distributeInfo = {'active':self.nodeDescription.active,
                                    'node_id':self.nodeDescription.node_id,
                                    'network_id': self.nodeDescription.network_id,
                                    'community_id': self.nodeDescription.community_id,
                                    'gateway_node':self.nodeDescription.gateway_node,
                                    'social_community':self.communityDescription.social_community,
                                    'resource_data_url': appConfig['lr.distribute_resource_data_url'],
                                    'filter_description':self.filterDescription.specData
                                }
        return distributeInfo

    distributeInfo = property(lambda self: self.getDistributeInfo(), None, None, None)
    nodeDescription = property(lambda self: self._nodeDescription, None, None, None)
    networkDescription = property(lambda self: self._networkDescription, None, None, None)
    communityDescription = property(lambda self: self._communityDescription, None, None, None)
    filterDescription = property(lambda self: self._filterDescription, None, None, None)
  #  networkPolicyDescription = property(lambda self: self._networkPolicyDescription, None, None, None)
    config = property(lambda self: dict(self._config), None, None, None)
    nodeJsonDescription = property(_getNodeJsonDescription, None, None, None)
    nodeJsonPolicy = property(_getNodeJsonPolicy, None, None, None)
    connections = property(lambda self: self._connections[:], None, None, None)
    nodeServices = property(lambda self: self._nodeServices.values(), None, None, None)
    status = property(_getStatusDescription, None, None, None)



