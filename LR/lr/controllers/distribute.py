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
import logging, couchdb, urlparse

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

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

    def create(self):
        db_to_replicate = request.params['resource_documents_database']
        server = couchdb.Server()
        network_id = 'network_id'
        community_id = 'community_id'
        db = server['community']
        source_description =       json.load(urllib2.urlopen('http://localhost/description')
        for doc in db:           
            base_location = db[doc]['location']
            description = json.load(urllib2.urlopen(urlparse.unparse(base_location,'description'))
            if description['gateway_node'] or source_description[network_id] = description[network_id] or source_description[community_id] = description[community_id]:            
                server.replicate(db_to_replicate,urlparse.unparse(base_location,'replication_data'))
        # url('distribute')

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
