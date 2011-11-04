#from pylons import config

import ConfigParser
import couchdb
from node_config import services, lrnodetemplate as nodeTemplate, setup_utils, couch_utils
from node_config.setup_node import publishNodeConnections
import os
from os import path
import uuid
import json
import urllib2
import urlparse
from node_config.services.Resource_Data_Distribution import __ResourceDataDistributionServiceTemplate as DistributeServiceTemplate
import subprocess
from lr.lib import helpers as h
from datetime import datetime

import logging

log = logging.getLogger(__name__)

_PWD = path.abspath(path.dirname(__file__))
_PYLONS_CONFIG = path.abspath(path.join(_PWD, "../../../../development.ini.orig"))
_RESOURCE_DATA_FILTER_APP = path.abspath(path.join(_PWD,  "../../../../../couchdb/resource_data/apps/filtered-replication"))
_TEST_DATA_PATH = path.abspath(path.join(_PWD, "../../data/nsdl_dc/data-000000000.json"))

            

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
    def __init__(self, nodeConfig, nodeName, communityId, networkId):
        self._nodeConfig = nodeConfig
        self._nodeName = nodeName
        self._pylonsConfigPath = path.abspath(path.join(path.dirname(_PYLONS_CONFIG),
                                                                        self._nodeName+"_config.ini"))
        self._setupPylonsConfig()
        self._setupDescriptions()
        self._setupNode()
        self._setupDistributeService()
        self.setNodeId(nodeName)
        self.setCommunityId(communityId)
        self.setNetworkId(networkId)

    #def __del__(self):
        #self.stop()
        #self.clear()

    def _getNodeDatabaseList(self):
        return [self._nodeConfig.get("couch_info", db) for db in self._CONFIG_DATABASE_NAMES]

    def _getNodeUrl(self):
        return self._nodeConfig.get("node_config", "node_url")

    def _setupDescriptions(self):
        #  Set the node, network and community
        self._communityDescription = dict(nodeTemplate.community_description)
        self._networkDescription = dict(nodeTemplate.network_description)
        self._nodeDescription = dict (nodeTemplate.node_description) 
    
    def _setupNode(self):
        #create the couch db databases
        self._server = couchdb.Server(url=self._nodeConfig.get("couch_info", "server"))
        setup_utils.CreateDB(self._server,  dblist=self._getNodeDatabaseList(), deleteDB=True)
        policy = dict(nodeTemplate.network_policy_description)
        setup_utils.PublishDoc(self._server, 
                                            self._nodeConfig.get("couch_info", "network"), 
                                            'network_policy_description', policy)
        #Push the filter design document for the ressource_data.
        couch_utils.pushCouchApp(_RESOURCE_DATA_FILTER_APP,  
                                        urlparse.urljoin(self._nodeConfig.get("couch_info", "server"),
                                                                 self._nodeConfig.get("couch_info", "resourcedata")))
        #Get the filter for distributable and change to filter resource_data
        resourceDataDB = self._server[self._nodeConfig.get("couch_info", "resourcedata")]
        doc = resourceDataDB["_design/"+_RESOURCE_DATA_FILTER_APP.split("/")[-1]]
        doc["filters"]["replicated_resource_data_filter"] = \
                    doc["filters"]["replication_filter"].replace("resource_data_distributable", "resource_data")
        doc["filters"]["resource_data_filter"] = self._RESOURCE_DATA_FILTER
        resourceDataDB.update([doc])
        
        
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
    
        #Add the distribute_sink_url
        pylonsConfig.set("app:main", "distribute_sink_url",  
                                    urlparse.urljoin(self._nodeConfig.get("couch_info", "server"),
                                                           self._nodeConfig.get("couch_info", "resourcedata")))
        configFile = open(self._pylonsConfigPath, 'w')
        pylonsConfig.write(configFile)
        configFile.close()
    
    def setCommunityId(self, community):
        self._communityDescription["community_id"]= community
        self._communityDescription["community_name"] = community
        self._communityDescription["community_description"] = community
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

    def setNetworkId(self, network):
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
    
    def setNodeId(self, nodeName):
       self._nodeDescription["node_id"] =  uuid.uuid4().hex
       self._nodeDescription["node_name"] = nodeName
       self._nodeDescription["node_description"] = nodeName
       self._nodeDescription["node_admin_identity"] = "testNode@admin.distribute"
       
       setup_utils.PublishDoc(self._server, self._nodeConfig.get("couch_info", "node"),  
                                        self._nodeDescription["doc_type"] , 
                                        self._nodeDescription)

    def publishResourceData(self, docs):
        resourceDatabase = self._server[self._nodeConfig.get("couch_info", "resourcedata")]
        for d in docs:
            doc = {}
            doc.update(d)
            #delete any previous revision number for the docs
            del doc['_rev']
            doc['doc_ID'] = uuid.uuid4().hex
            now = datetime.utcnow().isoformat()+"Z"
            doc['node_timestamp'] = now
            doc['create_timestamp'] = now
            doc['update_timestamp']  = now
            resourceDatabase[doc['doc_ID']] = doc
    
    def addConnections(self, connections):
        publishNodeConnections(self._getNodeUrl(), self._server, 
                                                self._nodeConfig.get("couch_info", "node"),
                                                self._nodeName, connections)  
    
    def distribute(self):
        if hasattr(self, '_pylonsProcess'):
            data = json.dumps({"dist":"dist"})
            request = urllib2.Request(urlparse.urljoin(self._getNodeUrl(), "distribute"), 
                                                    data,
                                                    {'Content-Type':'application/json; charset=utf-8'})
            response = urllib2.urlopen(request) 

    def compareDistributedResources(self, destination, 
                                                            sourceNodeComparisonFilter="filtered-replication/resource_data_filter",
                                                            filterArgs={}):
        """This method considered this node as source node.
        It compares its resource_data document with the destionation node to
        verify that data was distributed.  This comparison assumes that distribute/
        replication is done and that there is no other additions or deletions the
        nodes that are being compared"""
        sourceDatabase = self._server[self._nodeConfig.get("couch_info", "resourcedata")]
        destinationDatabase = destination._server[destination._nodeConfig.get("couch_info", "resourcedata")]
        
        #For source node get all the resource_data documents using the filter
        # that was using to distribute the document to destination node.
        sourceResults = sourceDatabase.changes(**{"filter": sourceNodeComparisonFilter,
                                                                                  "include_docs":True,
                                                                                   "query_params":filterArgs})["results"]
        #Get all the resource_data of hte destionation node.
        destinationResults = destinationDatabase.changes(**{"filter":"filtered-replication/resource_data_filter",
                                                                                                "include_docs":True})["results"] 
        
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
            self._pylonsProcess.terminate()
        
    def start(self):
        command = '(cd {0}; paster serve {1})'.format(
                                        path.abspath(path.dirname(self._pylonsConfigPath)),
                                        self._pylonsConfigPath) 
        self._pylonsProcess = subprocess.Popen(command, shell=True)
        
    def clear(self):
        self.stop()
        #Delete the generated pylons configuration files
        os.remove(self._pylonsConfigPath)
        #Delete the generated database.
        for database in self._getNodeDatabaseList():
            del self._server[database]



def getNodeConfiguration():
    #for confFiles in path.join(path.abspath(__file__),  '../config'):
        #print     
        pass
    
def test_distribute_common_nodes_same_community_same_network():
    #node1 = Node("couchURL", "nodeURL", {})
    #node2 = Node("couchURL", "nodeURL", {})
    
    #setupNode(node1)
    #setupNode(node2)
    pass
    
    assert True == True, "The truth is not true"
    pass
