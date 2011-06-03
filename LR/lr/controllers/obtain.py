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
import logging, urllib2, json, couchdb
from lr.model.base_model import appConfig
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)  

class ObtainController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('obtain', 'obtain')
    def get_view(self,view_name = '_design/learningregistry/_view/resources',keys=[], include_docs = False):
        s = couchdb.Server(appConfig['couchdb.url'])
        db = s[appConfig['couchdb.db.resourcedata']]
        if len(keys) > 0:
          view = db.view(view_name, include_docs=include_docs, keys=keys)
        else:
          view = db.view(view_name, include_docs=include_docs)
        return view

    def format_data(self,full_docs,data):
        yield "{'documents':["
        num_sent = 0
        if data is not None and len(data) > 0:
            for doc in data:
                if full_docs:
                    # Get the resource data and update  with the node timestamp data
                    # That the view  has in value['timestamp']
                    resourceData = {}
                    resourceData = doc.doc
                    return_data = {'doc_ID':doc.id,'resource_data_description':resourceData}
                else:
                    return_data = {'doc_ID':doc.key} 
                num_sent = num_sent + 1
                if num_sent < len(data): 
                    yield json.dumps(return_data) + ','
                else:
                    yield json.dumps(return_data) 
        yield "]}"
    def index(self, format='html'):
        """GET /obtain: All items in the collection"""
        data = self.get_view()	
        return self.format_data(False,data)
        # url('obtain')

    def create(self):
        """POST /obtain: Create a new item"""
        data = json.loads(request.body)
        keys = map(lambda key: key['request_ID'],data['request_IDs'])
        full_docs = data['ids_only'] is None or data['ids_only'] == False
        if data['by_doc_ID']:
          view = self.get_view(keys=keys, full_docs=full_docs)
        elif data['by_resource_ID']:
          view = self.get_view('_design/filter/_view/resource-location',keys, full_docs)
        return_data = view  
        return self.format_data(full_docs,return_data)
        # url('obtain')

    def new(self, format='html'):
        """GET /obtain/new: Form to create a new item"""
        # url('new_obtain')

    def update(self, id):
        """PUT /obtain/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('obtain', id=ID),
        #           method='put')
        # url('obtain', id=ID)

    def delete(self, id):
        """DELETE /obtain/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('obtain', id=ID),
        #           method='delete')
        # url('obtain', id=ID)

    def show(self, id, format='html'):
        """GET /obtain/id: Show a specific item"""
        data =self.get_view(keys=[id], include_docs=True)
        return self.format_data(True, data)
        # url('obtain', id=ID)

    def edit(self, id, format='html'):
        """GET /obtain/id/edit: Form to edit an existing item"""
        # url('edit_obtain', id=ID)
