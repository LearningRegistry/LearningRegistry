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
    __TARGET_NODE_INFO = 'taget_node_info'
    __OK = 'OK'
    __ERROR = 'error'
    
    def __before__(self):
        self.resource_data = appConfig['couchdb.db.resourcedata']
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('distribute', 'distribute')
    
    def destination(self):
        """GET /destination: return node information"""
        # url('distribute')
        response = {'OK': True}
        
        try:
            response[self.__TARGET_NODE_INFO] = sourceLRNode.distributeInfo
            if appConfig.has_key("distribute_sink_url"):
                  response['target_node_info']['distribute_sink_url'] = appConfig["distribute_sink_url"]
        except Exception as ex:
            log.exception(ex)
            response["error":"Internal error"]
        
        log.info("received distribute request...returning: \n"+pprint.pformat(response, 4))
        return json.dumps(response)
        
    def _getDistinationInfo(self, connection):
        # Make sure we only have one slash in the url path. More than one 
        #confuses pylons routing libary.
        destinationURL = urlparse.urljoin(connection.destination_node_url.strip(),
                                                                "destination")
        
        request = urllib2.Request(destinationURL)
        credential = sourceLRNode.getDistributeCredentialFor(destinationURL)
        
        if credential is not None:
            base64string = base64.encodestring('%s:%s' % (credential['username'],credential['password'])).replace("\n", "")
            request.add_header("Authorization", "Basic %s" % base64string)
        
        log.info("\n\nAccess destination node at: "+pprint.pformat(request.__dict__))
        return json.load(urllib2.urlopen(request))

    def _canDistributeTo(self, connection, sourceNodeInfo):
        
        if  not connection.active:
            return {self.__OK: False, 
                         'connection_id': connection.connection_id, 
                         self.__ERROR: 'Inactive connection'}
              
        result={self.__OK:True, 'connection_id': connection.connection_id }
        sourceNodeInfo = h.dictToObject(sourceNodeInfo)
        try:
            destinationNodeInfo = h.dictToObject(self._getDistinationInfo(connection)[self.__TARGET_NODE_INFO])
            result['destinationNodeInfo'] = destinationNodeInfo
            
            if ((sourceNodeInfo.gateway_node or destinationNodeInfo.gateway_node)  != connection.gateway_connection):
                result[self.__ERROR] = " 'gateway_connection' mismatch between nodes and connection data"
            
            elif ((sourceNodeInfo.community_id != destinationNodeInfo.community_id) and
                    ((not sourceNodeInfo.social_community) or (not destinationNodeInfo.social_community))):
                result[self.__ERROR] = 'cannot distribute across non social communities'
             
            elif ((sourceNodeInfo.network_id != destinationNodeInfo.network_id) and
                    ((not sourceNodeInfo.gateway_node)or(not destinationNodeInfo.gateway_node))):
                result[self.__ERROR] = 'cannot distribute across networks (or communities) unless gateway'
            
            elif ((sourceNodeInfo.gateway_node and destinationNodeInfo.gateway_node)
                    and (sourceNodeInfo.network_id == destinationNodeInfo.network_id)):
                result[self.__ERROR]  = 'gateway must only distribute across different networks'

            elif (sourceNodeInfo.gateway_node and not destinationNodeInfo.gateway_node):
                result[self.__ERROR]  = 'gateways can only distribute to gateways'
        except urllib2.URLError as ex:
            log.exception(ex)
            result[self.__ERROR] = "Cannot reach destination node.  "+str(ex.reason)
        except Exception as ex:
            log.exception(ex)
            result[self.__ERROR] = "Internal error. Cannot process destination node info"
        
        if result.has_key(self.__ERROR):
            result[self.__OK] = False
        
        return result


    def _getDistributeDestinations(self):
        """"Method to test the connections and returns a list of destionation node
             if the connections are valid"""
        gatewayConnectionList = []
        connectionsStatusInfo = {self.__OK:True, 'connections':[]}
        
        for connection in sourceLRNode.connections:
            # Make sure that the connection is active
            connectionsStatusInfo['connections'].append(self._canDistributeTo(connection, sourceLRNode.distributeInfo))
        
            if connectionsStatusInfo['connections'][-1][self.__OK] and connection.gateway_connection == True:
                gatewayConnectionList.append(connection)
              # Only one gateway  connection is allowed, faulty network description
            if len(gatewayConnectionList) > 1:
                log.info("***Abort distribution. More than one gateway node connection")
                connectionsStatusInfo[self.__ERROR] ="only one active gateway connection is allowed, faulty network description"
                break
        if len (sourceLRNode.connections) == 0:
            connectionsStatusInfo[self.__ERROR] ="No connection present for distribution"

        if connectionsStatusInfo.has_key(self.__ERROR) :
            connectionsStatusInfo[self.__OK] = False
          
        return connectionsStatusInfo
        
    def create(self):
        """POST / distribute start distribution"""
        
        def doDistribution(destinationNodeInfo, server, sourceUrl, lock):
            # We want to always use the replication filter function to replicate
            # only distributable doc and filter out any other type of documents.
            # However we don't have any query arguments until we test if there is any filter.
            replicationOptions={'filter':ResourceDataModel.REPLICATION_FILTER, 
                                             'query_params': None}
            # If the destination node is using an filter and is not custom use it
            # as the query params for the filter function
            if ((destinationNodeInfo.filter_description is not None ) and 
                 (destinationNodeInfo.filter_description.get('custom_filter') == False)):
                     replicationOptions['query_params'] = destinationNodeInfo.filter_description
                     
            #if distinationNode['distribute service'] .service_auth["service_authz"] is not  None:
                #log.info("Destination node '{}' require authentication".format(destinationUrl))
                #Try to get the user name and password the url
            destinationUrl = destinationNodeInfo.resource_data_url

            credential = sourceLRNode.getDistributeCredentialFor(destinationUrl)
            if credential is not None:
                parsedUrl = urlparse.urlparse()
                destinationUrl = destinationUrl.replace(parsedUrl.netloc, "{0}:{1}@{2}".format(
                                                credential['username'], credential['password'], parsedUrl.netloc))
            
            log.info("\n\nReplication started\nSource:{0}\nDestionation:{1}\nArgs:{2}".format(
                            sourceUrl, destinationUrl, str(replicationOptions)))

            if replicationOptions['query_params'] is  None: 
                del replicationOptions['query_params']
            results = server.replicate(sourceUrl, destinationNodeInfo.resource_data_url, **replicationOptions)
            log.debug("Replication results: "+str(results))
            with lock:
                server = couchdb.Server(appConfig['couchdb.url'])
                db = server[appConfig['couchdb.db.node']]
                doc = db[appConfig['lr.nodestatus.docid']]
                doc['last_out_sync'] = h.nowToISO8601Zformat()
                db[appConfig['lr.nodestatus.docid']] = doc
        
        log.info("Distribute.......\n")
        ##Check if the distribte service is available on the node.
        #if(sourceLRNode.isServiceAvailable(NodeServiceModel.DISTRIBUTE) == False):
            #log.info("Distribute not available on node ")
            #return
        if((sourceLRNode.connections is None) or 
            (len(sourceLRNode.connections) ==0)):
            log.info("No connection present for distribution")
            return json.dumps({self.__ERROR:''})
        log.info("Connections: \n{0}\n"+pprint.pformat([c.specData for c in sourceLRNode.connections]))
        
        lock = threading.Lock()
        connectionsStatusInfo = self._getDistributeDestinations()
        log.debug("\nSource Node Info:\n{0}".format(pprint.pformat(sourceLRNode.distributeInfo)))
        log.debug("\n\n Distribute connections:\n{0}\n\n".format(pprint.pformat(connectionsStatusInfo)))
        
        for connectionStatus in  connectionsStatusInfo['connections']:
            if connectionStatus.has_key(self.__ERROR) == False:
                replicationArgs = (connectionStatus['destinationNodeInfo'], 
                                              defaultCouchServer, 
                                              self.resource_data ,lock)
                    # Use a thread to do the actual replication.
                replicationThread = threading.Thread(target=doDistribution, args=replicationArgs)
                replicationThread.start()
            return json.dumps(connectionsStatusInfo)
