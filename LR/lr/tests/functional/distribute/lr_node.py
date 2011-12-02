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
import subprocess
from lr.lib import helpers as h
from datetime import datetime
from time import sleep
import signal

import logging

log = logging.getLogger(__name__)


_PYLONS_CONFIG = path.abspath(path.join(_PWD, "../../../../development.ini.orig"))
_RESOURCE_DATA_FILTER_APP = path.abspath(path.join(_PWD,  "../../../../../couchdb/resource_data/apps/filtered-replication"))
_DISTRIBUTE_TEST_LOG = "test_distribute.log"


class Node(object):
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
        self._pylonsConfigPath = path.abspath(path.join(path.dirname(_PYLONS_CONFIG),
                                                                        self._nodeName+"_config.ini"))
        self._setupPylonsConfig()
        self._setupDescriptions()
        self._setupNode()
        self._setupDistributeService()
        self.setNodeInfo(nodeName)
        if communityId is not None:
            self.setCommunityInfo(community)
        if networkId is not None:
            self.setNetworkInfo(networkId)
        self.removeTestLog()

    def _getNodeDatabaseList(self):
        return [self._nodeConfig.get("couch_info", db) for db in self._CONFIG_DATABASE_NAMES]

    def _getNodeUrl(self):
        return self._nodeConfig.get("node_config", "node_url")

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
            os.remove(path.abspath(path.join(self._pylonsConfig, _DISTRIBUTE_TEST_LOG)))
        except:
            pass

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
    
    def addConnectionTo(self, destinationUrl, gateway_connection=False):
        connection = dict(nodeTemplate.connection_description)
        connection['connection_id'] = uuid.uuid4().hex
        connection['source_node_url']=self._getNodeUrl()
        connection['gateway_connection'] = gateway_connection
        connection['destination_node_url'] = destinationUrl
        setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                "{0}_to_{1}_connection".format(self._nodeName, destinationUrl),
                                 connection)
      
    
    def distribute(self):
        if hasattr(self, '_pylonsProcess'):
            data = json.dumps({"dist":"dist"})
            request = urllib2.Request(urlparse.urljoin(self._getNodeUrl(), "distribute"), 
                                                    data,
                                                    {'Content-Type':'application/json; charset=utf-8'})
            response = urllib2.urlopen(request) 

    def getResourceDataDocs(self, filter_description=None):
        
        db = self._server[self._nodeConfig.get("couch_info", "resourcedata")]
        
        #For source node get all the resource_data documents using the filter
        # that was using to distribute the document to destination node.
        options = { "filter": "filtered-replication/change_feed_filter",
                            "include_docs":True,
                            "doc_type":"resource_data"}
        if filter_description is not None:
            options["filter_description"] = json.dumps(filter_description)
        return db.changes(**options)["results"]
        
    def compareDistributedResources(self, destination, filter_description=None):
        """This method considered this node as source node.
        It compares its resource_data document with the destionation node to
        verify that data was distributed.  This comparison assumes that distribute/
        replication is done and that there is no other additions or deletions the
        nodes that are being compared"""

        sourceResults = self.getResourceDataDocs(filter_description)
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
        if hasattr(self, '_pylonsProcess'):
            os.killpg(self._pylonsProcess.pid, signal.SIGTERM)
        
    def start(self):
        command = '(cd {0}; paster serve {1} --log-file {2}.log)'.format(
                                        path.abspath(path.dirname(self._pylonsConfigPath)),
                                        self._pylonsConfigPath, _DISTRIBUTE_TEST_LOG) 
        #Create a process group name as so that the shell and all its process
        # are terminated when stop is called.
        self._pylonsProcess = subprocess.Popen(command, shell=True, 
                                                            preexec_fn=os.setsid)
    
    def resetResourceData(self):
        del self._server[ self._nodeConfig.get("couch_info", "resourcedata")]
        self._setupResourceData()
        
    
    def tearDown(self):
        self.stop()
        #Delete the generated pylons configuration files
        os.remove(self._pylonsConfigPath)
        #Delete the generated database.
        for database in self._getNodeDatabaseList():
            del self._server[database]


