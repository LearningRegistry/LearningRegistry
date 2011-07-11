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
import json 
import couchdb
from lr.model.base_model import appConfig
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)  
trues = ['T','t','True','true']
class ObtainController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('obtain', 'obtain')
    def get_view(self,view_name = '_design/learningregistry/_view/resources',keys=[], include_docs = False):
        s = couchdb.Server(appConfig['couchdb.url'])
        db = s[appConfig['couchdb.db.resourcedata']]
        if len(keys) > 0:
          view = db.view(view_name, include_docs=include_docs, keys=keys,stale='ok')
        else:
          view = db.view(view_name, include_docs=include_docs,stale='ok')
        return view

    def format_data(self, full_docs, data, currentResumptionToken):
        yield '{"documents":['
        num_sent = 0
        currentID = ""
        byIDResponseChunks = None
        if data is not None:
            firstID = True
            for doc in data:
                if full_docs: 
                    if doc.key != currentID:                        
                        currentID = doc.key                        
                        if not firstID:
                            yield ']' + byIDResponseChunks[1] + ','                            
                        byIDResponseChunks = json.dumps({'doc_ID':doc.key,'document':[]}).split(']')
                        yield byIDResponseChunks[0] + json.dumps(doc.doc)                                                                                    
                        firstID = False
                    else:                        
                        yield ',' + json.dumps(doc.doc)
                else:
                    if doc.key != currentID:
                        currentID = doc.key
                        if not firstID:
                            yield ','
                        firstID = False
                        yield json.dumps({'doc_ID': doc.key})
    
        if full_docs and byIDResponseChunks is not None:             
            yield ']' + byIDResponseChunks[1]                        
        yield "]}"
    def index(self, format='html'):
        """GET /obtain: All items in the collection"""
        data = self._parseParams()                      
        return self._performObtain(data)
        # url('obtain')
    def _performObtain(self,data):
        keys = data['request_IDs']
        full_docs = (not data.has_key('ids_only')) or data['ids_only'] == False
        by_doc_ID =(data.has_key('by_doc_ID') and data['by_doc_ID'])
        by_resource_ID = (data.has_key('by_resource_ID') and data['by_resource_ID'])
        resumption_token = 0
        if by_doc_ID and by_resource_ID:
            raise Exception("by_doc_ID and by_resource_ID cannot both be True")
        if not data.has_key('by_resource_ID') and not by_doc_ID:
            by_resource_ID = True
        if not by_doc_ID and not by_resource_ID:
            raise Exception("by_doc_ID and by_resource_ID cannot both be False")
        if data.has_key('resumption_token'):
            resumption_token = int(data['resumption_token'])            
        if  by_doc_ID:
            view = self.get_view(keys=keys, include_docs=full_docs)
        elif by_resource_ID:
            view = self.get_view('_design/learningregistry/_view/resource-location',keys, include_docs=full_docs)        
        return self.format_data(full_docs,view, resumption_token)        
    def create(self):
        """POST /obtain: Create a new item"""
        data = json.loads(request.body)
        return self._performObtain(data)

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
        data = self._parseParams()
        keys=[id]
        data['request_IDs'] = keys
        return self._performObtain(data)
        # url('obtain', id=ID)
    def _parseParams(self):
        data = {
            'by_doc_ID':False,
            'by_resource_ID':True,
            'ids_only': False,
            'request_IDs': []
        }
        if request.params.has_key('by_doc_ID'):
            data['by_doc_ID'] = request.params['by_doc_ID'] in trues
            data['by_resource_ID'] = False
        if request.params.has_key('by_resource_ID'):
            data['by_resource_ID'] = request.params['by_resource_ID'] in trues
        if request.params.has_key('ids_only'):
            data['ids_only'] = request.params['ids_only'] in trues
        if request.params.has_key('resumption_token'):
            data['resumption_token'] = request.params['resumption_token']
        return data        
    def edit(self, id, format='html'):
        """GET /obtain/id/edit: Form to edit an existing item"""
        # url('edit_obtain', id=ID)
