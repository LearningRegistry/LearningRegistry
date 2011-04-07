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
            distributeInfo['distribute_sink_url'] = urlparse.urljoin(request.url, appConfig['couchdb.db.resourcedata'])
        log.info("received distribute request...returning: \n"+json.dumps(distributeInfo))
        return json.dumps(distributeInfo)
    
    
    def create(self):
        if ((sourceLRNode.isServiceAvailable(NodeServiceModel.DISTRIBUTE) == False)
            or (sourceLRNode.connections is None)):
            return
        
        sourceNodeDBUrl = ResourceDataModel._defaultDB.resource.url
        
        def doDistribution(destinationNode, server, sourceUrl, destinationUrl):
      
            if ((destinationNode.filterDescription is not None) and 
                 (destinationNode.filterDescription.custom_filter == True)):
                destinationDB =None
                try:
                    destinationDB = couchdb.Database(destinationUrl)
                except Exception as ex:
                    log.exception(ex)
                    return
                 # Post everything directly to couchdb if the target is doing custom filter
                 # for now we are assuming that target sink is couchdb   
                for doc in ResourceDataModel.getAll():
                    try:
                                destinationDB[doc['_id']] = doc
                    except Exception as e:
                        log.exception(e)
            else:
                filterFunction = (ResourceDataModel._defaultDB.name+"/" + 
                                          ResourceDataModel.DEFAULT_FILTER)
                                          
                replicationOptions={'filter':filterFunction,  
                                        'query_params': None}
                if destinationNode.filterDescription is not None:
                    replicationOptions['query_params'] = destinationNode.filterDescription.specData
                    server.replicate(sourceUrl, destinationUrl, **replicationOptions)
                else:
                    server.replicate(sourceUrl,destinationUrl)
    
        
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
                 ((sourceLRNode.community.social_community == False) or
                  (destinationLRNode.community.social_community == False))):
                      continue
             
            if ((sourceLRNode.nodeDescription.gateway_node == False) and 
                  (sourceLRNode.networkDescription.network_id != 
                  destinationLRNode.networkDescription.network_id)):
                      continue
            replicationArgs = (destinationLRNode, 
                                         defaultCouchServer, 
                                         sourceNodeDBUrl, 
                                         distributeInfo['distribute_sink_url'])
                                         
            # Use a thread to do the actual replication.                             
            replicationThread = threading.Thread(target=doDistribution, 
                                                                        args=replicationArgs)
            replicationThread.start()


    def new(self, format='html'):
        """GET /distribute/new: Form to create a new item"""
        # url('new_distribute')

    def update(self, id):
        """PUT /distribute/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('distribute', id=ID),
        #           method='put')
        # url('distribute', id=ID)

    def delete(self, id):
        """DELETE /distribute/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('distribute', id=ID),
        #           method='delete')
        # url('distribute', id=ID)

    def show(self, id, format='html'):
        """GET /distribute/id: Show a specific item"""
        # url('distribute', id=ID)

    def edit(self, id, format='html'):
        """GET /distribute/id/edit: Form to edit an existing item"""
        # url('edit_distribute', id=ID)
