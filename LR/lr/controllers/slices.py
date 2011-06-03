import logging, urllib2, json, couchdb
from lr.model.base_model import appConfig

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SlicesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('slice', 'slices')

    def _getParams(self):
        req_params = {}
        
        if request.method == "POST":
            req_params = dict(request.params.copy(), **self._parameterizePOSTBody())
        else:
            req_params = request.params.copy()
        return req_params
    
    def _parseParams(self):
        params = {}
        paramKeys = ['start_date', 'identity', 'any_tags', 'full_docs']
        req_params = self._getParams()
        param_count = 0
        
        for paramKey in paramKeys:
            if req_params.has_key(paramKey):
                if paramKey == 'full_docs':
                    params['full_docs'] = req_params[paramKey][0].lower() == 't'
                else:
                    params[paramKey] = str(req_params[paramKey])
                    param_count += 1
            else:
                if paramKey == 'full_docs':
                    params[paramKey] = False
                else:
                    params[paramKey] = ""
        
        
        params['param_count'] = param_count
        
        return params

    def _returnResponse(self, body):
        response.headers["Content-Type"] = "text/xml; charset=utf-8"
        return body
      

    def get_view(self,view_name = '_design/learningregistry/_view/resources',keys=[], include_docs = False):
        s = couchdb.Server(appConfig['couchdb.url'])
        db = s[appConfig['couchdb.db.resourcedata']]
        if len(keys) > 0:
          view = db.view(view_name, include_docs=include_docs, keys=keys)
        else:
          view = db.view(view_name, include_docs=include_docs)
        return view
    
    def _getKeys(self, params):
        keys = []
        start_date = params['start_date']
        identity = params['identity']
        any_tags = params['any_tags']
        param_count = params['param_count']
        
        if any_tags != "" :
            any_tag_list = any_tags.split(",")
        
        if param_count == 1:
            if start_date != "" :
                keys.append(start_date) 
            elif identity != "" :
                keys.append(identity) 
            elif any_tags != "" :
                for tag in any_tag_list:
                    keys.append(tag) 
        elif param_count == 2:
            if start_date == "" :
                for tag in any_tag_list:
                    keys.append([identity, tag]) 
            elif identity == "" :
                for tag in any_tag_list:
                    keys.append([start_date, tag]) 
            elif any_tags == "" :
                keys.append([any_tags, identity]) 
        elif param_count == 3:
            for tag in any_tag_list:
                keys.append([start_date, identity, tag]) 
         
        return keys
        
    def format_data(self,full_docs,data, forceUnique):
        sentIDs = []
        yield "{'documents':["
        num_sent = 0
        if data is not None and len(data) > 0:
            for row in data:
                if (row.id not in sentIDs) or not forceUnique:
                    sentIDs.append(row.id)
                    if full_docs:
                        # Get the resource data and update  with the node timestamp data
                        # That the view  has in value['timestamp']
                        resourceData = {}
                        resourceData = row.doc
                        return_data = {'doc_ID':row.id, 'resource_data_description':resourceData}
                    else:
                        return_data = {'doc_ID':row.id} 
                    num_sent = num_sent + 1
                    if num_sent < len(data): 
                        yield json.dumps(return_data) + ','
                    else:
                        yield json.dumps(return_data) 
        yield "]}"
    
    def index(self, format='html'):
        """GET /slices: All items in the collection"""
        # url('slices')
        params = self._parseParams()
        keys = self._getKeys(params)
        data = self.get_view('_design/learningregistry/_view/slice', keys, True)	
        return self.format_data(params['full_docs'],data,True)
        #return params["start_date"] + " " + params["identity"]  + " " + params["search_key"] + "\n" + str(self.format_data(False,data))
        # url('obtain')

    def create(self):
        """POST /slices: Create a new item"""
        # url('slices')

    def new(self, format='html'):
        """GET /slices/new: Form to create a new item"""
        # url('new_slice')

    def update(self, id):
        """PUT /slices/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('slice', id=ID),
        #           method='put')
        # url('slice', id=ID)

    def delete(self, id):
        """DELETE /slices/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('slice', id=ID),
        #           method='delete')
        # url('slice', id=ID)

    def show(self, id, format='html'):
        """GET /slices/id: Show a specific item"""
        # url('slice', id=ID)

    def edit(self, id, format='html'):
        """GET /slices/id/edit: Form to edit an existing item"""
        # url('edit_slice', id=ID)
