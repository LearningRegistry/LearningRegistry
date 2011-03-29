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
import logging, urllib2, json,urllib, couchdb
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
    def get_view(self,view_name = '_design/learningregistry/_view/resources',keys=[]):
        s = couchdb.Server(appConfig['couchdb.url'])
        db = s[appConfig['couchdb.db.resourcedata']]        
        if len(keys) > 0:
          view = db.view(view_name, include_docs=True, keys=keys)
        else:
          view = db.view(view_name, include_docs=True)          
        return view

    def format_data(self,full_docs,data):
        if full_docs:
          return_data = {'documents' : map(lambda doc: {'doc_ID':doc.id,'resource_data_description':doc.doc},data)}
        else:
          return_data = {'documents' : map(lambda doc: {'doc_ID':doc.id},data)}
        return return_data
    def index(self, format='html'):
        """GET /obtain: All items in the collection"""
        data = self.get_view()	
        return json.dumps(self.format_data(False,data))
        # url('obtain')

    def create(self):
        """POST /obtain: Create a new item"""
        data = json.loads(request.body)
        keys = map(lambda key: key['request_ID'],data['request_IDs'])
        if data['by_doc_ID']:
          view = self.get_view('_all_docs',keys)
        elif data['by_resource_ID']:
          view = self.get_view('_design/filter/_view/resource-location',keys)
        return_data = view
        return_data = self.format_data(data['ids_only'] is None or data['ids_only'] == False,return_data)
        return json.dumps(return_data)
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
        url = 'http://localhost/resource_data/'+id
        r = urllib2.urlopen(url)
        data = r.read()
        return data
        # url('obtain', id=ID)

    def edit(self, id, format='html'):
        """GET /obtain/id/edit: Form to edit an existing item"""
        # url('edit_obtain', id=ID)
