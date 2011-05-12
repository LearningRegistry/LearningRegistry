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


log = logging.getLogger(__name__)

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
        self._monitoringChanges = False
        self._lastChangeSeq = -1
        self._changeMonintoringThread = None
        config = data
        self._monitorResourceDataChanges()
        if isinstance(data, dict):
            config = dictToObject(data)
            
        # Check first if node description is set. if not look for in the DB if not in the db
        # create it from the config data.
        
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
        
        self._networkPolicyDescription = self._initModel(NetworkPolicyModel, 
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
        #Try to get the model data from the database.
        model = None
        modelDoc = modelClass.get(modelId)
        if modelDoc is None:
            model = modelClass(modelConf)
            return model
        else:
            model = modelClass(modelDoc)
        mode.validate()
        return model
        
        
    def _setNodeStatus(self):
        nodeStatus = None
        nodeStatusId = self._nodeDescription.node_id+"_node_status"
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
        statusData = {'doc_count': ResourceDataModel._defaultDB.info()['doc_count'],
                                'timestamp': h.nowToISO8601Zformat()}
        statusData.update(self._nodeStatus.specData)
        return statusData
        
        
    def isServiceAvailable(self, serviceType):
        """Method to test if serviceType is available """
        for service in self._nodeServices:
            if service.active == True and serviceType == service.service_type:
                return True
        return False
    
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
        
        
    def _monitorResourceDataChanges(self):
        """Method that tracks the updates, deletes, and additions time of envelops, 
         resource_data documents in the resource_data database."""
        # First get get the list sequence id of hte latest change to that we can start
        # getting the changes for that sequence number.
        log.info("Start  to log resource_data changes monitoring\n")
        db = ResourceDataModel._defaultDB
        currentChanges = db.changes();
        if self._lastChangeSeq == -1:
            self._lastChangeSeq = currentChanges['last_seq']
        log.info("Last change sequence: "+str(self._lastChangeSeq))
        
        def recordChanges():
            if self._monitoringChanges == True:
                return
            self._monitoringChanges = True;
            db = ResourceDataModel._defaultDB
       
            while True:
                # I have to include the doc since the filter does seems to work.  Otherwise
                # using the same replication filter to get only resource_data document
                # would work been better.
                options ={'feed': 'continuous',
                              'since': self._lastChangeSeq,
                              'include_docs':True
                              }
                changes =  db.changes(**options)
                for change in changes:
                    if 'doc' not in change:
                        continue
                    timestamp =  h.nowToISO8601Zformat()
                    # See if the document is of resource_data type if not ignore it.
                    doc = change['doc']
                    if  not 'resource_data' in doc:
                        continue
                    #get the revision number.
                    log.info("\n\n"+pprint.pformat(change)+"\n\n")
                    revNumber = doc['_rev'].split('-')[0]
                    timestampDoc = {
                                '_id':doc['_id']+"-timestamp",
                                'doc_ID': doc['doc_ID'],
                                'doc_type': 'resource_data_timestamp'
                        }
                    log.info("RevNubmber: {0}\nTimestampDoc {1}".format(revNumber,
                                                pprint.pformat(timestampDoc)))
                    # Remove the document from list change and add the remaining data
                    # to the timestampDoc
                    if  revNumber == '1':
                        log.info("\nSaving new timestamp:\n")
                        timestampDoc['node_timestamp'] = timestamp
                        try:
                            db[timestampDoc['_id']]  = timestampDoc
                        except Exception as ex:
                            log.exception(ex)
                    #else:
                        #log.info("\nupdate existing timestamp\n")
                        #timestampDoc = db.get(timestampDoc['_id'])
                        #timestampDoc['update_timestamp'] = timestamp
                        #try:
                            #db.update(timestampDoc);
                        #except Exception as ex:
                            #log.exception(ex)
                    # Keep the last sequence number
                    self._lastChangeSeq = change['seq']
                    log.info("Time Stamps: "+pprint.pformat(timestampDoc))
                    self._lastChangeSeq = change['seq']
        # Use a separate thread to track to the changes in resource_data.
        self._changeMonitoringThread = threading.Thread(target=recordChanges)
        self._changeMonitoringThread.start()
        
    nodeDescription = property(lambda self: self._nodeDescription, None, None, None)
    networkDescription = property(lambda self: self._networkDescription, None, None, None)
    communityDescription = property(lambda self: self._communityDescription, None, None, None)
    filterDescription = property(lambda self: self._filterDescription, None, None, None)
    networkPolicyDescription = property(lambda self: self._networkPolicyDescription, None, None, None)
    config = property(lambda self: dict(self._config), None, None, None)
    connections = property(lambda self: self._connections[:], None, None, None)
    nodeServices = property(lambda self: self._nodeServices[:], None, None, None)
    
    status = property(_getStatusDescription, None, None, None)


