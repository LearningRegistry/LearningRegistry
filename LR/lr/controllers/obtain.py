#   Copyright 2011 Department of Defence

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   See the License for the specific language governing permissions and
#   limitations under the License.
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging 
import json 
from lr.model.base_model import appConfig
import lr.lib.helpers as h
import lr.lib.resumption_token as rt
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)  
trues = ['T','t','True','true']
LIMIT = 100
class ObtainController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('obtain', 'obtain')
    def get_view(self,view_name = '_design/learningregistry/_view/resources',keys=[], include_docs = False,resumption_token=None):                
        log.debug(resumption_token)
        db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])
        args = {}
        if len(keys) > 0:
            args['keys'] = keys
        args['stale'] = 'ok'
        args['limit'] = LIMIT
        args['include_docs'] = include_docs
        if resumption_token is not None:
            args['startkey'] = resumption_token['startkey']
            args['startkey_docid'] = resumption_token['startkey_docid']
            args['skip'] = 1
        view = h.getView(database_url=db_url,view_name=view_name,documentHandler=lambda d: h.document(d),**args)
        return view
    def format_data(self, full_docs, data, currentResumptionToken):
        yield '{"documents":['
        num_sent = 0
        currentID = ""
        byIDResponseChunks = None
        count = 0
        lastStartKey = None
        lastId = None
        if data is not None:
            firstID = True
            for doc in data:
                lastStartKey = doc.key
                lastId = doc.id
                count += 1
                if full_docs: 
                    if doc.key != currentID:                        
                        currentID = doc.key                        
                        if not firstID:
                            yield ']' + byIDResponseChunks[1] + ',\n'                            
                        byIDResponseChunks = json.dumps({'doc_ID':doc.key,'document':[]}).split(']')
                        yield byIDResponseChunks[0] + json.dumps(doc.doc)                                                                                    
                        firstID = False
                    else:                        
                        yield ',\n' + json.dumps(doc.doc)    
                else:
                    if doc.key != currentID:
                        currentID = doc.key
                        if not firstID:
                            yield ',\n'
                        firstID = False
                        yield json.dumps({'doc_ID': doc.key})
        if full_docs and byIDResponseChunks is not None:             
            yield ']' + byIDResponseChunks[1]                        
        if count < LIMIT:			
            yield "]}"
        else:
            token = rt.get_token("obtain",startkey=lastStartKey,endkey=None,startkey_docid=lastId)
            yield '], "resumption_token":"%s"}' % token
    def index(self, format='html'):
        """GET /obtain: All items in the collection"""        
        data = self._parseParams()
        self._validateParams(data)
        return self._performObtain(data)
        # url('obtain')
    def _validateParams(self,data):
        by_doc_ID =(data.has_key('by_doc_ID') and data['by_doc_ID'])
        by_resource_ID = (data.has_key('by_resource_ID') and data['by_resource_ID'])        
        if by_doc_ID and by_resource_ID:
            abort(500,"by_doc_ID and by_resource_ID cannot both be True")
        if not by_doc_ID and not by_resource_ID:
            abort(500,"by_doc_ID and by_resource_ID cannot both be False")        
    def _performObtain(self,data):
        keys = data['request_IDs']
        full_docs = (not data.has_key('ids_only')) or data['ids_only'] == False
        by_doc_ID =(data.has_key('by_doc_ID') and data['by_doc_ID'])
        by_resource_ID = (data.has_key('by_resource_ID') and data['by_resource_ID'])
        resumption_token = None
        if not data.has_key('by_resource_ID') and not by_doc_ID:
            by_resource_ID = True            
        if data.has_key('resumption_token'):
            resumption_token = data['resumption_token']
        if data.has_key('callback'):
            yield "{0}(".format(data['callback'])                    
        if  by_doc_ID:
            view = self.get_view(keys=keys, include_docs=full_docs,resumption_token=resumption_token)
        elif by_resource_ID:
            view = self.get_view('_design/learningregistry/_view/resource-location',keys, include_docs=full_docs,resumption_token=resumption_token)        
        for i in  self.format_data(full_docs,view, resumption_token):        
            yield i
        if(data.has_key('callback')):
            yield ')'
    def create(self):
        """POST /obtain: Create a new item"""
        data = json.loads(request.body)
        self._validateParams(data)
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
            'request_IDs': [],            
        }
        if request.params.has_key('by_doc_ID'):
            data['by_doc_ID'] = request.params['by_doc_ID'] in trues
            data['by_resource_ID'] = False
        
        if request.params.has_key('by_resource_ID'):            
            data['by_resource_ID'] = request.params['by_resource_ID'] in trues
        if request.params.has_key('ids_only'):
            data['ids_only'] = request.params['ids_only'] in trues
        if request.params.has_key('resumption_token'):
            data['resumption_token'] = rt.parse_token('obtain',request.params['resumption_token'])
            log.debug(data['resumption_token'])
        if request.params.has_key('callback'):
            data['callback'] = request.params['callback']
        return data        
    def edit(self, id, format='html'):
        """GET /obtain/id/edit: Form to edit an existing item"""
        # url('edit_obtain', id=ID)
