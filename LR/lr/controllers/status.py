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

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from lr.model import LRNode as sourceLRNode, NodeServiceModel
import json

log = logging.getLogger(__name__)

class StatusController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('status', 'status')

    def index(self, format='html'):
        """GET /status: All items in the collection"""
        #if sourceLRNode.isServiceAvailable(NodeServiceModel.ADMINISTRATIVE) == False:
        # return "Administrative service not is available"
            
        return json.dumps(sourceLRNode.status)
        # url('status')

    def create(self):
        """POST /status: Create a new item"""
        # url('status')

    def new(self, format='html'):
        """GET /status/new: Form to create a new item"""
        # url('new_status')

    def update(self, id):
        """PUT /status/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('status', id=ID),
        #           method='put')
        # url('status', id=ID)

    def delete(self, id):
        """DELETE /status/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('status', id=ID),
        #           method='delete')
        # url('status', id=ID)

    def show(self, id, format='html'):
        """GET /status/id: Show a specific item"""
        # url('status', id=ID)

    def edit(self, id, format='html'):
        """GET /status/id/edit: Form to edit an existing item"""
        # url('edit_status', id=ID)
