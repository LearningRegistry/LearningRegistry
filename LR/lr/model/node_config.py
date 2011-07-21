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
import json
_COUCHDB_FIELDS =['_id', '_rev', 
                                    '_attachments', 
                                    '_deleted', 
                                    '_revisions', 
                                    '_revs_info',
                                    '_conflicts',
                                    '_deleted_conflicts' ]
                                    
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
    def __init__(self, data, startMonitor = True):
        self._config = {}
        self._communityDescription = None
        self._networkDescription = None
        self._filterDescription = None
        self._nodeStatus = None
        self._monitoringChanges = False
        self._lastChangeSeq = -1
        self._changeMonintoringThread = None
        config = data
        if startMonitor:
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
        def updateView():
            designDocs = db.view('_all_docs',include_docs=True,startkey='_design%2F',endkey='_design0')
            for designDoc in designDocs:
                if designDoc.doc.has_key('views') and len(designDoc.doc['views']) > 0:
                    viewName = "{0}/_view/{1}".format(designDoc.id,designDoc.doc['views'].keys()[0])
                    log.debug('start view update %s' % viewName)
                    log.debug(len(db.view(viewName)))        
        def distribute():
            log.debug('start distribute')
            data = json.dumps({"dist":"dist"})
            log.debug(self._distUrl)
            request = urllib2.Request(self._distUrl,data,{'Content-Type':'application/json; charset=utf-8'})
            response = urllib2.urlopen(request)   
            log.debug('end distribute')            
        def recordChanges():
            if self._monitoringChanges == True:
                return
            self._monitoringChanges = True;
            db = ResourceDataModel._defaultDB
            self._seqOfLastViewUpdate = 0
            self._seqOfLastDist = 0
            self._updateThreshold = int(appConfig['couchdb.threshold.viewupdate'])
            self._distributeThreshold = int(appConfig['couchdb.threshold.distrbutes'])
            self._resourcesview = appConfig['couchdb.db.resourcesview']
            self._distUrl = appConfig['lr.distribute.url']
            self._updateThread = None
            self._distributeThread = None
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
                    currentSeq = change['seq']
                    lastViewDelta = currentSeq - self._seqOfLastViewUpdate
                    if lastViewDelta > self._updateThreshold:
                        if self._updateThread == None or not self._updateThread.isAlive():
                            self._updateThread = threading.Thread(target = updateView)
                            self._updateThread.start()
                        self._seqOfLastViewUpdate = currentSeq
                    if currentSeq - self._seqOfLastDist > self._distributeThreshold:                     
                        if self._distributeThread == None or not self._distributeThread.isAlive():
                            self._distributeThread = threading.Thread(target = distribute)
                            self._distributeThread.start()                        
                        self._seqOfLastDist = currentSeq                                    
                    # See if the document is of resource_data type if not ignore it.
                    doc = change['doc']
                    if  ((not 'resource_data' in doc) and
                          (not 'resource_data_distributable'  in doc)):
                        continue
                    log.info("Change to handle ....")
                    # Handle resource_data. 
                    if doc['doc_type'] == 'resource_data':
                        log.info("\*******Changes to resource_document: "+doc['_id'])
                        distributableID = doc['_id']+"-distributable"
                        # Use the ResourceDataModel class to create an object that 
                        # contains only a the resource_data spec data.
                        distributableDoc = ResourceDataModel(doc)._specData
                        #remove the node timestamp
                        del distributableDoc['node_timestamp']
                        #change thet doc_type 
                        distributableDoc['doc_type']='resource_data_distributable'
                        
                        log.debug("\n\ndistributable doc:\n{0}\n".format(pprint.pformat(distributableDoc)))
                        
                        # Check to see if a corresponding distributatable document exist.
                        # not create a new distribuation document without the 
                        # node_timestamp and _id+distributable.
                        if not distributableID in db:
                            try:
                                log.info('Adding distributable doc %s...\n' % distributableID)
                                db[distributableID] = distributableDoc
                            except Exception as e:
                                log.error("Cannot save distributable document %s\n" % distributableID)
                                log.exception(e)
                        else:
                            # A distributable copy of the document is in the database. See
                            # if need be updated.
                            try:
                                savedDistributableDoc = db[distributableID]
                            except Exception as e:
                                log.error("Cannot get existing distributatable document\n")
                                log.exception(e)
                                continue
                            temp = {}
                            temp.update(savedDistributableDoc);
                            # Remove the couchdb generated field so that can compare
                            # the two document and see it there is a need for update.
                            for k in _COUCHDB_FIELDS:
                                if k in temp:
                                    del temp[k]
                            if distributableDoc != temp:
                                savedDistributableDoc.update(distributableDoc)
                                log.info("\n\nUpdate distribuatable doc:\n")
                                log.debug("\n{0}\n\n".format(pprint.pformat(distributableDoc)))
                                try:

                                    db.update([savedDistributableDoc])
                                except Exception as e:
                                    log.error("Failed to update existing distributable doc: {0}".format(
                                                    pprint.pformat(savedDistributableDoc)))
                                    log.exception(e)
                              
                    elif doc['doc_type'] == 'resource_data_distributable':
                        log.info("\n-------Changes to distributable resource doc: "+doc['_id'])
                        #check if the document is alredy in the database.
                        resourceDataID = doc['doc_ID']
                        # Create a resource_data object from the distributable data.
                        # the specData will generate a node_timestamp be default
                        resourceDataDoc = ResourceDataModel(doc)._specData
                        resourceDataDoc['doc_type'] = 'resource_data'
                        if resourceDataID not in db:
                            try:
                                log.info("Adding new resource_data for distributable")
                                db[resourceDataID] = resourceDataDoc
                            except Exception as e:
                                log.error("\n\nCannot get current document:  {0}".format(
                                                pprint.pformat(resourceDataDoc)))
                                log.exception(e)
                        else:
                            # There exist already a resource_data document for the distributable
                            # get it and see if it needs to be updated.
                            try:
                                savedResourceDoc = db[resourceDataID]
                            except Exception as e:
                                log.error("\n\nCannot find existing resource_data doc for distributable: \n{0}".format(
                                                pprint.pformat(doc)))
                                log.exception(e)
                                continue
                                
                            #Remove the couchdb generated fields.
                            temp = {}
                            temp.update(savedResourceDoc)
                            for k in _COUCHDB_FIELDS:
                                if k in temp:
                                    del temp[k]
                            # Now deleate the node_timestamp field on both document
                            # before comparing them.
                            del temp['node_timestamp']
                            del resourceDataDoc['node_timestamp']
                            
                            if temp != resourceDataDoc:
                                savedResourceDoc.update(resourceDataDoc)
                                try:
                                    log.info("\nUpdate existing resource data from distributable\n")
                                    db.update([savedResourceDoc])
                                except Exception as e:
                                    log.error("\n\nFailed to udpate existing resource_data doc:\n{0}".format(
                                                    pprint.pformat(savedResourceDoc)))
                                    log.exception(e)
                    # Keep  last change sequence.
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


