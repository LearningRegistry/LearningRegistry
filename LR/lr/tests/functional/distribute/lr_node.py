#!/usr/bin/env python
#    Copyright 2011 Lockheed Martin
#
'''
Created on Nov 11, 2011

@author: jpoyau
'''

import os
from os import path

_PWD = path.abspath(path.dirname(__file__))

import sys
#Add the config and lr module the sys path so that they can used.
sys.path.append(path.abspath(path.join(_PWD,"../../../../../config")))
sys.path.append(path.abspath(path.join(_PWD, "../../../../")))


import ConfigParser
import couchdb
import lrnodetemplate as nodeTemplate 
import setup_utils, couch_utils
from setup_node import publishNodeConnections
import uuid
import json
import urllib2
import urlparse
from services.Resource_Data_Distribution import __ResourceDataDistributionServiceTemplate as DistributeServiceTemplate
from services.Push_To_Distribution import __PushToDistributionServiceTemplate as PushToServiceTemplate
import subprocess
from lr.lib import helpers as h
from time import sleep
import pprint
import signal

import logging

log = logging.getLogger(__name__)


_PYLONS_CONFIG = path.abspath(path.join(_PWD, "../../../../development.ini.orig"))
_RESOURCE_DATA_FILTER_APP = path.abspath(path.join(_PWD,  "../../../../../couchdb/resource_data/apps/filtered-replication"))
_TEST_DISTRIBUTE_DIR_LOG = path.abspath(path.join(path.dirname(_PYLONS_CONFIG), "test_distribute_logs"))
        
        
class Node(object):
    _REPLICATOR_DB = '_replicator'
    _CONFIG_DATABASE_NAMES=["community", "network", "node", "resourcedata"]
    _RESOURCE_DATA_FILTER = """
        function(doc , req)
        {
            if (doc.doc_type == "resource_data")
            {
                return true;
            }
            return false;
        }
    """

    def __init__(self, nodeConfig, nodeName, communityId=None, networkId=None):
        self._nodeConfig = nodeConfig
        self._nodeName = nodeName
        self._replicatorUrl = urlparse.urljoin(self._nodeConfig.get("couch_info", "server"), self._REPLICATOR_DB)
        self._setupFilePaths()
        self._setupPylonsConfig()
        self._setupDescriptions()
        self._setupNode()
        self._setupDistributeService()
        self._setupPushToService()
        self.setNodeInfo(nodeName)
        if communityId is not None:
            self.setCommunityInfo(communityId)
        if networkId is not None:
            self.setNetworkInfo(networkId)
        self.removeTestLog()
        # Keep around the replication documents that are store in the replication 
        # database so that they can be deleted when the node is teared down.
        self._replicationIdList = []
        
        
    def _setupFilePaths(self):
        
        self._pylonsConfigPath = path.abspath(path.join(path.dirname(_PYLONS_CONFIG),
                                                                        self._nodeName+"_config.ini"))
        self._logFilePath = path.abspath(path.join(_TEST_DISTRIBUTE_DIR_LOG,
                                                                      self._nodeName+".log"))
                                                                      
    def _getNodeDatabaseList(self):
        return [self._nodeConfig.get("couch_info", db) for db in self._CONFIG_DATABASE_NAMES]

    def _getNodeUrl(self):
        return self._nodeConfig.get("node_config", "node_url").strip()

    def _setupDescriptions(self):
        #  Set the node, network and community
        self._communityDescription = dict(nodeTemplate.community_description)
        self._networkDescription = dict(nodeTemplate.network_description)
        self._nodeDescription = dict (nodeTemplate.node_description) 
        self._nodeFilterDescription = dict(nodeTemplate.filter_description)
    
    def _setupResourceData(self):
        #Push the filter design document for the ressource_data.
        setup_utils.CreateDB(self._server, 
                            dblist=[self._nodeConfig.get("couch_info", "resourcedata")], 
                            deleteDB=True)

        couch_utils.pushCouchApp(_RESOURCE_DATA_FILTER_APP,  
                                        urlparse.urljoin(self._nodeConfig.get("couch_info", "server"),
                                                                 self._nodeConfig.get("couch_info", "resourcedata")))
    
    def removeTestLog(self):
        try:
            os.remove(self._logFilePath)
        except:
            pass

    def getResourceDataDbUrl(self):
        return  urlparse.urljoin(self._nodeConfig.get("couch_info", "server"),
                                              self._nodeConfig.get("couch_info", "resourcedata"))
    def _setupNode(self):
        #create the couch db databases
        self._server = couchdb.Server(url=self._nodeConfig.get("couch_info", "server"))
        setup_utils.CreateDB(self._server,  dblist=self._getNodeDatabaseList(), deleteDB=True)
        policy = dict(nodeTemplate.network_policy_description)
        setup_utils.PublishDoc(self._server, 
                                            self._nodeConfig.get("couch_info", "network"), 
                                            'network_policy_description', policy)
        self._setupResourceData()

    def _setupDistributeService(self):
        custom_opts = {}
        custom_opts["node_endpoint"] = self._getNodeUrl()
        custom_opts["service_id"] = uuid.uuid4().hex
        custom_opts["active"] = True
        
        must = DistributeServiceTemplate()
        config_doc = must.render(**custom_opts)

        doc = json.loads(config_doc)
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node") ,
                          doc["service_type"]+":Resource Data Distribution service", doc)

    def _setupPushToService(self):
        custom_opts = {}
        custom_opts["node_endpoint"] = self._getNodeUrl()
        custom_opts["service_id"] = uuid.uuid4().hex
        custom_opts["active"] = True
        
        must = PushToServiceTemplate()
        config_doc = must.render(**custom_opts)

        doc = json.loads(config_doc)
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node") ,
                          doc["service_type"]+":Push To Distribution service", doc)


    def _setupPylonsConfig(self):
        #Read the original configuration and update with the test node data.
        pylonsConfig = ConfigParser.ConfigParser()
        pylonsConfig.read(_PYLONS_CONFIG)

        #Set the couchdb database info
        for database in self._CONFIG_DATABASE_NAMES:
            pylonsConfig.set("app:main", "couchdb.db.{0}".format(database),
                                       self._nodeConfig.get("couch_info" , database))

        #Set the port number and url.
        for option in self._nodeConfig.options("pylons_server"):
            pylonsConfig.set("server:main", option, self._nodeConfig.get("pylons_server", option))
    
        #Set the ressource data url

        pylonsConfig.set("app:main", "lr.distribute_resource_data_url",  
                                    urlparse.urljoin(self._nodeConfig.get("couch_info", "server"),
                                                           self._nodeConfig.get("couch_info", "resourcedata")))
        #change the logging level to the highest level to avoid spamming log.
        #pylonsConfig.set("logger_lr", "level", "CRITICAL") 
        
        configFile = open(self._pylonsConfigPath, 'w')
        pylonsConfig.write(configFile)
        configFile.close()

    def setCommunityInfo(self, community, isSocialCommunity=True):
        self._communityDescription["community_id"]= community
        self._communityDescription["community_name"] = community
        self._communityDescription["community_description"] = community
        self._communityDescription["social_community"] = isSocialCommunity
        
        self._networkDescription["community_id"] = community
        self._nodeDescription["community_id"] = community
        
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                            self._nodeDescription["doc_type"] , 
                                            self._nodeDescription)
                                            
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "network"),
                                            self._networkDescription["doc_type"], 
                                            self._networkDescription)
        
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "community"),
                                            self._communityDescription["doc_type"], 
                                            self._communityDescription)

    def setNetworkInfo(self, network):
        self._networkDescription["network_name"] = network
        self._networkDescription["network_description"] = network
        self._networkDescription["network_id"] = network
        self._nodeDescription["network_id"] = network
       
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                            self._nodeDescription["doc_type"] , 
                                            self._nodeDescription)
                                            
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "network"),
                                            self._networkDescription["doc_type"], 
                                            self._networkDescription)
    
    def setNodeInfo(self, nodeName=None, isGateway=False, isActive=True):
       self._nodeDescription["node_id"] =  uuid.uuid4().hex
       if nodeName is not None:
           self._nodeDescription["node_name"] = nodeName
           self._nodeDescription["node_description"] = nodeName
       self._nodeDescription["gateway_node"] = isGateway
       self._nodeDescription["active"]= isActive
       self._nodeDescription["node_admin_identity"] = "testNode@admin.distribute"
       
       setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                        self._nodeDescription["doc_type"] , 
                                        self._nodeDescription)
        
    def setFilterInfo(self, filter, include_exclude=True, custom_filter=False):
        self._nodeFilterDescription["filter_name"] = self._nodeName + "_filter"
        self._nodeFilterDescription["include_exclude"] = include_exclude
        self._nodeFilterDescription["custom_filter"] = custom_filter
        self._nodeFilterDescription["filter"]=filter
        
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                        self._nodeFilterDescription["filter_name"] , 
                                        self._nodeFilterDescription)
  

    def publishResourceData(self, docs):
        resourceDatabase = self._server[self._nodeConfig.get("couch_info", "resourcedata")]
        for d in docs:
            doc = {}
            doc.update(d)
            #delete any previous revision number for the docs
            if '_rev'  in doc:
                del doc['_rev']
                
            doc['doc_ID'] = uuid.uuid4().hex
            now = h. nowToISO8601Zformat()
            doc['node_timestamp'] = now
            doc['create_timestamp'] = now
            doc['update_timestamp']  = now
            resourceDatabase[doc['doc_ID']] = doc
        self.waitOnChangeMonitor()
    
    def addConnectionTo(self, destinationUrl, gateway_connection=False):
        connection = dict(nodeTemplate.connection_description)
        connection['connection_id'] = "{0}_to_{1}_connection".format(self._getNodeUrl(), destinationUrl).strip()
        connection['source_node_url']=self._getNodeUrl()
        connection['gateway_connection'] = gateway_connection
        connection['destination_node_url'] = destinationUrl
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                            connection['connection_id'],
                                            connection)

    def _getResourceDataChangeUrl(self):
        return "{0}/{1}/{2}".format(self._server.resource.url,
                                            self._nodeConfig.get("couch_info", "resourcedata"),
                                            "_changes")

    def waitOnChangeMonitor(self):
        """" Wait that for change monitor the recreate all the local copies of a document
        after the distribution has been completed."""
        if hasattr(self, '_pylonsProcess') == False:
            return
    
        try:
            # Get both distributable and local copies of the document compare their 
            # numbers and wait until they are equal.
            while (True) :
                distributableDocs = self.getResourceDataDocs(include_docs= False, 
                                                                            doc_type='resource_data_distributable')
                resourceDataDocs = self.getResourceDataDocs(include_docs=False)
                remaining =  len(distributableDocs) - len(resourceDataDocs)
                
                print("\n....{0} difference {1} for change monitor to catchup {2}\n".format(
                          self._nodeName, remaining, 
                          "\nResourceData Count:\t{0}\nDistributatableData Count: {1}".format(
                        len(resourceDataDocs),  len(distributableDocs))))
        
                if remaining == 0:
                    return;
                #Assume that it takes about .01 seconds to generate the  new copy.
                sleepTime = int(10+abs(remaining)*.01)
            
                print("\n....{0}, Waiting {1} seconds for change monitor to catchup {2}".format(
                          self._nodeName, sleepTime, 
                          "\nResourceData Count:\t{0}\nDistributatableData Count: {1}".format(
                           len(resourceDataDocs),  len(distributableDocs))))
    
                sleep(sleepTime)
            pass
        except Exception as e:
            log.exception(e)
            print(e)
            
    def waitOnReplicationById(self, replicationId, destinationNode=None):
        while(True):
            response = urllib2.urlopen(self._replicatorUrl+'/'+replicationId)
            doc = json.load(response)
            response.close()
            print('\n\n---------------Replication  Status-----------')
            print('--Replication:{1}\n<=From node:\t{0}\n=>To node:\t{2}\n<=>completion status: \t{3}\n'.format(
                            self._nodeName,  replicationId, str(destinationNode), doc.get('_replication_state')))
            if  doc.get('_replication_state') == 'completed':
                break
            sleep(30)


    def waitOnReplication(self,  distributeResults):
        """Wait for the replication to complete on the all node connections specifed
        by dsistributeResults """
        if (distributeResults is None or 
            ('connections' in distributeResults) == False or 
            len (self.getResourceDataDocs(doc_type='resource_data_distributable', include_docs=False) ) == 0):
            print ("node {0}  has no replication results or distributable docs ....".format(self._nodeName))
            return
            
        for connectionResults in distributeResults['connections']:
            if 'replication_results' not in connectionResults:
                continue
            self._replicationIdList.append(connectionResults['replication_results']['id'])
            self.waitOnReplicationById(connectionResults['replication_results']['id'],
                                                      connectionResults['destinationNodeInfo']['resource_data_url'].split('/')[-1].split('_resource_data')[0])
        
    def pushTo(self, destinationNode, predicateFunc=None):
        """Push to destination node.  Use destination node filter if it has a filter"""
        
        pushToOptions = {"destination_database_url": destinationNode.getResourceDataDbUrl()}
            
        if (destinationNode._nodeFilterDescription is None) == False:
            pushToOptions['filter'] = destinationNode._nodeFilterDescription["filter"]
            pushToOptions['include_exclude'] =destinationNode._nodeFilterDescription["include_exclude"]
        
        if (predicateFunc is None) == False:
             pushToOptions['predicate'] = predicateFunc
        
        request = urllib2.Request(self._getNodeUrl()+"/push_to", 
                                                headers={'Content-Type':'application/json' },
                                                data = json.dumps(pushToOptions))
        
        results = json.load(urllib2.urlopen(request))
        self._replicationIdList.append(results['id'])
        self.waitOnReplicationById(results['id'], destinationNode._nodeName)
        print("Push to  reponse: \n{0}".format(pprint.pformat(results)))
         
        return results

    def distribute(self, waitOnReplication=True):
        """ Distribute to all the node connections.  When waited for completion is
        true the this method will that distribution is completed before returning 
        the results. """
        if hasattr(self, '_pylonsProcess'):
            data = json.dumps({"dist":"dist"})
            request = urllib2.Request(urlparse.urljoin(self._getNodeUrl(), "distribute"), 
                                                    data,
                                                    {'Content-Type':'application/json; charset=utf-8'})
                                                    
            results = json.load(urllib2.urlopen(request))
            print("Distribute reponse: \n{0}".format(pprint.pformat(results)))
            
            if waitOnReplication:
                self.waitOnReplication(results)

            return results
    
    def getResourceDataDocs(self, filter_description=None, predicate=None, 
                        doc_type='resource_data', include_docs=True):
        
        db = self._server[self._nodeConfig.get("couch_info", "resourcedata")]        
        #For source node get all the resource_data documents using the filter
        # that was using to distribute the document to destination node.
        options = { "filter": "filtered-replication/change_feed_filter",
                            "include_docs":include_docs,
                            "doc_type":doc_type}
        if filter_description is not None:
            options["filter_description"] = json.dumps(filter_description)
        if predicate  is not None:
            options["predicate"] = predicate
        return db.changes(**options)["results"]


    def compareDistributedResources(self, destination, filter_description=None, predicate=None):
        """This method considers this node as source node.
        It compares its resource_data document with the destionation node to
        verify that data was distributed.  This comparison assumes that distribute/
        replication is done and that there is no other additions or deletions the
        nodes that are being compared"""

        sourceResults = self.getResourceDataDocs(filter_description, predicate)
        destinationResults = destination.getResourceDataDocs() 
        
        #check the number of source document is the same at destination.
        #otherwise the nodes resource distribution failed somehow.
        if len(destinationResults) != len(sourceResults):
            return False
                
        #Sort the documents by doc id for easy comparison
        sourceDocs = sorted(sourceResults, key= lambda doc: doc["id"])
        destinationDocs = sorted(destinationResults, key= lambda doc: doc["id"])
        
        # compare documents by documents and check that the destionation time is
        # greater than the source node time.
        for i  in range(len(sourceDocs)):
            sourceDoc = {}
            sourceDoc.update(sourceDocs[i]["doc"])
            destDoc ={}
            destDoc.update(destinationDocs[i]["doc"])
            if (h.convertToISO8601UTC(destDoc["node_timestamp"]) <= h.convertToISO8601UTC(sourceDoc["node_timestamp"])):
                log.debug("{0} and {1} error".format(sourceDoc['doc_ID'], destDoc['doc_ID']))
                return False
            #remove the node_timestamp and _rev then compare  the docs
            del sourceDoc["node_timestamp"]
            del destDoc["node_timestamp"]
            del destDoc["_rev"]
            del sourceDoc["_rev"]
            if sourceDoc != destDoc:
                 log.debug("{0} and {1} error".format(sourceDoc['doc_ID'], destDoc['doc_ID']))
                 return False
        return True
        
    def stop(self):
        if hasattr(self, '_pylonsProcess') == False:
            return
            
        os.killpg(self._pylonsProcess.pid, signal.SIGTERM)
        # Make sure that process is really dead and the port is releaseed.  This done
        # avoid bug when the node the stop and start methods are called quickly,
        # the dead node is still holding  port which sometimes tricks 
        # the start code thinking the node is up and running already.
        while True:
            try:
                response = urllib2.urlopen(self._getNodeUrl())
                if response.code :
                      os.killpg(self._pylonsProcess.pid, signal.SIGTERM)
                      sleep(5)
            except:
                break;
        del self._pylonsProcess

    def start(self):
        
        # remove any existing log file to start from scratch to avoid ever 
        # growing log file.
        self.removeTestLog()
        
        #Create the log file directory if it does not exists.
        if not path.exists(_TEST_DISTRIBUTE_DIR_LOG):
            print("create dir")
            os.mkdir(_TEST_DISTRIBUTE_DIR_LOG)
            
        command = '(cd {0}; paster serve {1} --log-file {2})'.format(
                                        path.abspath(path.dirname(self._pylonsConfigPath)),
                                        self._pylonsConfigPath, self._logFilePath)
                                        
        #Create a process group name as so that the shell and all its process
        # are terminated when stop is called.
        self._pylonsProcess = subprocess.Popen(command, shell=True, 
                                                            preexec_fn=os.setsid)
                                                            
        #wait for the node to start before returning.
        while True:
            sleep(5)
            try:
                response = urllib2.urlopen(self._getNodeUrl())
                if (response.code /100 ) < 4:
                    break
            except:
                continue
        #Wait the change monitor to cat
        self.waitOnChangeMonitor()
        print("node '{0}' started ....\n".format(self._nodeName) )
    
    def resetResourceData(self):
        del self._server[ self._nodeConfig.get("couch_info", "resourcedata")]
        self._setupResourceData()
        
    def restart(self):
        self.stop()
        self.start()
     
    def removeReplicationDocs(self):
        '''Method to delete replication document results documents from the couchdb
         _replicator database.  Its seems like replication will not work if there is an existing
         replication document stated as completed with the same source and target
         database name eventhough those the document is about database thas been
         deleted and recreated. '''
        for replicationId in self._replicationIdList:
            try:
                #Use urllib request to remove the replication documents, the python
                #couchdb interface has a bug at time of this write that prevents access
                # to the _replicator database.
                
                #first get the lastest version of the doc
                response = urllib2.urlopen(self._replicatorUrl+'/'+replicationId)
                doc = json.load(response)
                response.close()
                print ("\n\n--node {0} deleting replication doc: {1}".format(
                            self._nodeName, 
                            self._replicatorUrl+'/{0}?rev={1}'.format(doc['_id'], doc['_rev'])))
                            
                request = urllib2.Request(self._replicatorUrl+'/{0}?rev={1}'.format(doc['_id'], doc['_rev']), 
                                                        headers={'Content-Type':'application/json' })
        
                request.get_method = lambda: "DELETE"
                
                urllib2.urlopen(request)
            except Exception as e:
                log.exception(e)
            
    def tearDown(self):
        self.stop()
        try:
            #Delete the generated pylons configuration files
            os.remove(self._pylonsConfigPath)
        except Exception as e:
            log.exception(e)
        
        #Delete the generated database.
        for database in self._getNodeDatabaseList():
            try:
                del self._server[database]
            except Exception as e:
                log.exception(e)
                
        #Delete the replication documents
        self.removeReplicationDocs()

