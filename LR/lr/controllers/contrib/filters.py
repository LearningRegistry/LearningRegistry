import logging, json, couchdb
import hashlib

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect


from lr.lib.base import BaseController, render
import urllib2


log = logging.getLogger(__name__)

_COUCH_SERVER = config['app_conf']['couchdb.url.dbadmin']
_RESOURCE_DATA = config['app_conf']['couchdb.db.resourcedata']
_DESIGN_DOC = '_design/filter'

_BASE_PATH = _RESOURCE_DATA + "/" + _DESIGN_DOC
couchServer = couchdb.Server(_COUCH_SERVER)

class FiltersController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('filter', 'filters', controller='contrib/filters', 
    #         path_prefix='/contrib', name_prefix='contrib_')

    def index(self, format='json'):
        """GET /contrib/filters: All items in the collection"""
        url = 'http://localhost:5984/resource_data/_design/filter'
        res = urllib2.urlopen(url);
        response.headers['content-type'] = 'application/json'
        
        design = json.load(res)
        
        filters = { "filters": design["views"].keys() }
        return json.dumps(filters);
        # url('contrib_filters')

    def create(self):
        """POST /contrib/filters: Create a new item"""
        design = {}
        success = {"status": "OK"}
        maptemplate = """function(doc) {{      
            if (doc.doc_type && doc.doc_type == "resource_data" &&
                doc.node_timestamp) {{
                 
                 var validator = {0};
                 
                 if (validator(doc)) {{
                     emit(doc.node_timestamp, doc.doc_ID);
                 }}
            }}
        }}"""
        
        try:
            data = json.loads(request.body)
            
            viewName = None            
            viewObj = None
            if data.has_key("name") and data.has_key("map") and data.has_key("reduce"):
                jsSha = hashlib.sha1(data["map"]+data["reduce"]).hexdigest()
                viewName = "{0}-{1}".format(data["name"], jsSha)
                viewObj = { "map": maptemplate.format(data["map"]), "reduce": data["reduce"] }
            elif data.has_key("name") and data.has_key("map"):
                jsSha = hashlib.sha1(data["map"]).hexdigest()
                viewName = "{0}-{1}".format(data["name"], jsSha)
                viewObj = { "map": maptemplate.format(data["map"]) }
                
            design = couchServer[_RESOURCE_DATA][_DESIGN_DOC]
            
            if viewName != None and viewObj != None and design.has_key("views") == True and design["views"].has_key(viewName) == True:
                del design["views"][viewName]
            
            if viewName != None and viewObj != None:
                design["views"][viewName] = viewObj
                couchServer[_RESOURCE_DATA].save(design)
                success["filter"] = viewName 
            
            if viewName == None or viewObj == None:
                success["status"] = "ERROR"
                success["message"] = "Unable to create filter. You must provide a JSON object with required fields name and map, optional field reduce"
        except:
            success["status"] = "ERROR"
            success["message"] = "Internal Error: Could not create filter."
            log.exception(success["message"])
        
        response.headers['content-type'] = 'application/json'
        return json.dumps(success)
        # url('contrib_filters')

    def new(self, format='html'):
        """GET /contrib/filters/new: Form to create a new item"""
        # url('contrib_new_filter')

    def update(self, id):
        """PUT /contrib/filters/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('contrib_filter', id=ID),
        #           method='put')
        
        # url('contrib_filter', id=ID)

    def delete(self, id):
        """DELETE /contrib/filters/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('contrib_filter', id=ID),
        #           method='delete')
        design = {}
        success = {"status": "OK"}
        try:
            design = couchServer[_RESOURCE_DATA][_DESIGN_DOC]
            
            if design.has_key("views") == True and design["views"].has_key(id) == True:
                del design["views"][id]
                couchServer[_RESOURCE_DATA].save(design) 
            
        except:
            success["status"] = "ERROR"
            success["message"] = "Internal Error: Could not locate design document."
            log.exception(success["message"])
        
        response.headers['content-type'] = 'application/json'
        return json.dumps(success)
        # url('contrib_filter', id=ID)

    def show(self, id, format='json'):
        """GET /contrib/filters/id: Show a specific item"""
        
        design = couchServer[_RESOURCE_DATA][_DESIGN_DOC]
        
        reduceParam = ""
        if design.has_key("views") == True and design["views"].has_key(id) == True and design["views"][id].has_key("reduce"):
            reduceParam = "?reduce=false"

        uri = 'http://127.0.0.1:5984/resource_data/_design/filter/_view/'+id+reduceParam
        url = urllib2.Request(uri,headers={"Content-Type": "application/json"})
        res = urllib2.urlopen(url);
        response.headers['content-type'] = 'application/json'

        rawjson = res.read()
        return rawjson
        # url('contrib_filter', id=ID)

    def edit(self, id, format='json'):
        """GET /contrib/filters/id/edit: Form to edit an existing item"""
        url = 'http://localhost:5984/resource_data/_design/filter'
        res = urllib2.urlopen(url);
        response.headers['content-type'] = 'application/json'
        
        design = {}
        filters = {}
        try:
            design = json.load(res)
        except:
            log.exception("Unable to load design document.")
        
        if design.has_key("views") == True and design["views"].has_key(id) == True:
            filters = { id : design["views"][id] }
        return json.dumps(filters);
        # url('contrib_edit_filter', id=ID)
