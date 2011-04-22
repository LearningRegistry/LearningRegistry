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
import logging, couchdb, urlparse, json, urllib2
import threading
import re

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.model import LRNode as sourceLRNode, \
            NodeServiceModel, ResourceDataModel, LRNodeModel, defaultCouchServer, appConfig
            
from lr.lib.base import BaseController, render

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
        
        if sourceLRNode.isServiceAvailable(NodeServiceModel.DISTRIBUTE) == False:
            distributeInfo['OK'] = False
        else:
            distributeInfo['node_config'] = sourceLRNode.config
            distributeInfo['distribute_sink_url'] = urlparse.urljoin(request.url,self.resource_data)
        log.info("received distribute request...returning: \n"+json.dumps(distributeInfo))
        return json.dumps(distributeInfo)
    
    
    def create(self):
        """POST /obtain: Create a new item"""
        log.info("Distribute.......\n")
        if ((sourceLRNode.isServiceAvailable(NodeServiceModel.DISTRIBUTE) == False)
            or (sourceLRNode.connections is None)):
            log.info("Distribute not available on node")
            return
        
        sourceNodeDBUrl = ResourceDataModel._defaultDB.resource.url
        log.info("Source url: "+sourceNodeDBUrl)
        
        def doDistribution(destinationNode, server, sourceUrl, destinationUrl):
            
            filterFunction = (ResourceDataModel._defaultDB.name+"/" + 
                                          ResourceDataModel.DEFAULT_FILTER)
            # We want to always use the default filter function to filter
            # out design document on replication. But we don't have any
            # query arguments until we test if there is any filter.
            replicationOptions={'filter':filterFunction, 
                                             'query_params': None}
            # If the destination node is using an filter and is not custom use it
            # as the query params for the filter function
            if ((destinationNode.filterDescription is not None) and 
                 (destinationNode.filterDescription.custom_filter == False)):
                     replicationOptions['query_params'] = destinationNode.filterDescription.specData
            
            log.info("Replication started\nSource:{0}\nDestionation:{1}\nArgs:{2}".format(
                            sourceUrl, destinationUrl, str(replicationOptions)))
            if replicationOptions['query_params'] is not None:                
                server.replicate(sourceUrl, destinationUrl, **replicationOptions)
            else:
                server.replicate(sourceUrl,destinationUrl)
        
        log.info("Connections: "+str(sourceLRNode.connections)+"\n")
        for connection in sourceLRNode.connections:
            # Call a get on the distribute url of the connection node 
            if connection.active == False:
                continue
            destinationLRNode = None
            try:
                # Make sure we only have one slash in the url path. More than one 
                #confuses pylons routing libary.
                destinationURL = urlparse.urljoin(connection.destination_node_url.strip(), "distribute")
                log.info("\nAccess destination node at: "+destinationURL)
                distributeInfo = json.load(urllib2.urlopen(destinationURL))
                destinationLRNode = LRNodeModel(distributeInfo['node_config'])
            except Exception as ex:
                log.exception(ex)
                continue
        
            if ((sourceLRNode.communityDescription.community_id != 
                 destinationLRNode.communityDescription.community_id) and
                 ((sourceLRNode.communityDescription.social_community == False) or
                  (destinationLRNode.communityDescription.social_community == False))):
                      print("Distribute failed community test")
                      continue
             
            if ((sourceLRNode.nodeDescription.gateway_node == False) and 
                  (sourceLRNode.networkDescription.network_id != 
                  destinationLRNode.networkDescription.network_id)):
                      print("Distribute failed network test")
                      continue
            replicationArgs = (destinationLRNode, 
                                         defaultCouchServer, 
                                         self.resource_data, 
                                         distributeInfo['distribute_sink_url'])
                                         
            # Use a thread to do the actual replication.                             
            replicationThread = threading.Thread(target=doDistribution, 
                                                                        args=replicationArgs)
            replicationThread.start()

