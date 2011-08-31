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

import logging, urllib2, couchdb, json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
import lr.model as m

log = logging.getLogger(__name__)

class PublishController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('publish', 'publisher')

    def index(self, format='json'):
        """GET /publisher: All items in the collection"""
        # url('publisher')

    def create(self):
        data = json.loads(request.body)
        results = map(m.publish,data['documents'])
        return json.dumps({'OK':True, 'document_results':results})
        """POST /publisher: Create a new item"""

    def new(self, format='html'):
        return 'new'
        """GET /publisher/new: Form to create a new item"""
        # url('new_publish')

    def update(self, id):
        """PUT /publisher/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('publish', id=ID),
        #           method='put')
        # url('publish', id=ID)

    def delete(self, id):
        return 'delete'
        """DELETE /publisher/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('publish', id=ID),
        #           method='delete')
        # url('publish', id=ID)

    def show(self, id, format='json'):
        """GET /publisher/id: Show a specific item"""
        # url('publish', id=ID)
    def edit(self, id, format='html'):
        return 'edit'
        """GET /publisher/id/edit: Form to edit an existing item"""
        # url('edit_publish', id=ID)
