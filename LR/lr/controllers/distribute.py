#   Copyright 2011 Department of Defence

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import logging
import couchdb
import urlparse
import json
import  urllib2
import threading
import re
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.model import LRNode as sourceLRNode, \
            NodeServiceModel, ResourceDataModel, LRNodeModel, defaultCouchServer, appConfig
from lr.lib.base import BaseController, render
from lr.lib import helpers as h
import base64
import pprint

log = logging.getLogger(__name__)

class DistributeController(BaseController):
    def __before__(self):
        self.resource_data = appConfig['couchdb.db.resourcedata']
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('distribute', 'distribute')
    def index(self, format='html'):
        """GET /distribute: All items in the collection"""
        # url('distribute')
        distributeInfo = {'OK': True}
        
        #if sourceLRNode.isServiceAvailable(NodeServiceModel.DISTRIBUTE) == False:
            #distributeInfo['OK'] = False
        #else:
        distributeInfo['node_config'] = sourceLRNode.config
        distributeInfo['distribute_sink_url'] = urlparse.urljoin(request.url,self.resource_data)
        log.info("received distribute request...returning: \n"+json.dumps(distributeInfo))
        return json.dumps(distributeInfo)
    
    def _getDistributeDestinations(self):
        """"Method to test the connections and returns a list of destionation node
             if the connections are valid"""
        nodeDestinationList =[]
        gatewayConnectionList = []
        for connection in sourceLRNode.connections:
            # Make sure that the connection is active 
            if connection.active == False:
                continue
            destinationLRNode = None
           
            if connection.gateway_connection == True:
                gatewayConnectionList.append(connection)
            try:
                # Make sure we only have one slash in the url path. More than one 
                #confuses pylons routing libary.
                destinationURL = urlparse.urljoin(connection.destination_node_url.strip(),
                                                                        "distribute")
                
                request = urllib2.Request(destinationURL)
                credential = sourceLRNode.getDistributeCredentialFor(destinationURL)
                
                if credential is not None:
                    base64string = base64.encodestring('%s:%s' % (credential['username'],credential['password'])).replace("\n", "")
                    request.add_header("Authorization", "Basic %s" % base64string)
                
                log.info("\n\nAccess destination node at: "+pprint.pformat(request.__dict__))
                distributeInfo = json.load(urllib2.urlopen(request))
                destinationLRNode = LRNodeModel(distributeInfo['node_config'])
            except Exception as ex:
                log.exception(ex)
                continue
             # Use of local variable to store if  the connection is gateway connection. It is
            # done this way to deal with mismatch between node de and connection
            # description.
            isGatewayConnection = (
                        (sourceLRNode.nodeDescription.gateway_node == True) and
                        (destinationLRNode.nodeDescription.gateway_node ==True))
            # Skip the connection if there is any mismatch between the connection and
            # the node data.
            if isGatewayConnection != connection.gateway_connection:
                log.info("Skip connection. 'gateway_connection' mismatch between node and connection data")
                continue
        
            # Only one gateway  connection is allowed, faulty network description
            if len(gatewayConnectionList) > 1:
                log.info("***Abort distribution. More than one gateway node connection")
                #Clear the node destination list no distribution is network description 
                # is faulty
                nodeDestinationList = []
                break
            #Calcuate if the connection is gateway one, if so 
            #cannot distribute across non social communities
            if ((sourceLRNode.communityDescription.community_id != 
                 destinationLRNode.communityDescription.community_id) and
                 ((sourceLRNode.communityDescription.social_community == False) or
                  (destinationLRNode.communityDescription.social_community == False))):
                      log.info("Cannot distribute across non social communities")
                      continue
            # Cannot distribute across networks (or communities) unless gateway
            if((isGatewayConnection == False) and
                ((sourceLRNode.communityDescription.community_id != 
                 destinationLRNode.communityDescription.community_id) or
                (sourceLRNode.networkDescription.network_id != 
                  destinationLRNode.networkDescription.network_id))):
                      log.info("Different Network. Cannot distribute across networks (or communities) unless gateway")
                      continue
            # Gateway must only distribute across different networks.
            if((isGatewayConnection ==True) and
                   (sourceLRNode.networkDescription.network_id == 
                    destinationLRNode.networkDescription.network_id)):
                        log.info("Gateway must only distribute across different networks")
                        continue
            # Only gateways can distribute on gateway connection. This is really for 
            # catching mismatch in the data where a connection says it is between 
            # gateways when the nodes are not both gateways.
            if((connection.gateway_connection == True) and 
                ((sourceLRNode.nodeDescription.gateway_node == False) or
                (destinationLRNode.nodeDescription.gateway_node == False))):
                    log.info("Only gateways can distribute on gateway connection")
                    continue
            nodeInfo = { "distributeInfo": distributeInfo,
                                  "destinationBaseUrl":connection.destination_node_url,
                                  "destinationNode":destinationLRNode}
            nodeDestinationList.append(nodeInfo)
            
        return nodeDestinationList
        
    def create(self):
        """POST / distribute start distribution"""
        
        def doDistribution(destinationNode, server, sourceUrl, destinationUrl):
            # We want to always use the replication filter function to replicate
            # only distributable doc and filter out any other type of documents.
            # However we don't have any query arguments until we test if there is any filter.
            replicationOptions={'filter':ResourceDataModel.REPLICATION_FILTER, 
                                             'query_params': None}
            # If the destination node is using an filter and is not custom use it
            # as the query params for the filter function
            if ((destinationNode.filterDescription is not None) and 
                 (destinationNode.filterDescription.custom_filter == False)):
                     replicationOptions['query_params'] = destinationNode.filterDescription.specData
                     
            #if distinationNode['distribute service'] .service_auth["service_authz"] is not  None:
                #log.info("Destination node '{}' require authentication".format(destinationUrl))
                #Try to get the user name and password the url.
            credential = sourceLRNode.getDistributeCredentialFor(destinationUrl)
            if credential is not None:
                parsedUrl = urlparse.urlparse(destinationUrl)
                destinationUrl = destinationUrl.replace(parsedUrl.netloc, "{0}:{1}@{2}".format(
                                                credential['username'], credential['password'], parsedUrl.netloc))
            
            log.info("\n\nReplication started\nSource:{0}\nDestionation:{1}\nArgs:{2}".format(
                            sourceUrl, destinationUrl, str(replicationOptions)))

            if replicationOptions['query_params'] is  None: 
                del replicationOptions['query_params']
            server = couchdb.Server(config['couchdb.url'])
            db = server[config['couchdb.db.node']]
            doc = db[config['lr.nodestatus.docid']]
            doc['last_out_sync'] = h.nowToISO8601Zformat()
            doc['out_sync_node'] = destinationNode
            db.save(doc)                
            results = server.replicate(sourceUrl, destinationUrl, **replicationOptions)
            log.debug("Replication results: "+str(results))
        
        log.info("Distribute.......\n")
        ##Check if the distribte service is available on the node.
        #if(sourceLRNode.isServiceAvailable(NodeServiceModel.DISTRIBUTE) == False):
            #log.info("Distribute not available on node ")
            #return
        if((sourceLRNode.connections is None) or 
            (len(sourceLRNode.connections) ==0)):
            log.info("No connection present for distribution")
            return
        log.info("Connections: "+str(sourceLRNode.connections)+"\n")

        for connectionInfo in self._getDistributeDestinations():
            replicationArgs = (connectionInfo['destinationNode'], 
                                         defaultCouchServer, 
                                         self.resource_data, 
                                         urlparse.urljoin(connectionInfo['destinationBaseUrl'], self.resource_data))
                                         
            # Use a thread to do the actual replication.
            replicationThread = threading.Thread(target=doDistribution, 
                                                                        args=replicationArgs)
            replicationThread.start()

