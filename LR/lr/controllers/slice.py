import logging, urllib2, json, couchdb
from lr.model.base_model import appConfig

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from datetime import datetime, timedelta
from lr.lib.oaipmherrors import *

log = logging.getLogger(__name__)

END_DATE = 'until'
START_DATE = 'from'
IDENTITY = 'identity'
ANY_TAGS = 'any_tags'
#FULL_DOCS = 'full_docs'
IDS_ONLY = 'ids_only'

class SliceController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('slice', 'slices')


    def _get_params(self):
        req_params = {}
        
        if request.method == "POST":
            req_params = dict(request.params.copy(), **self._parameterizePOSTBody())
        else:
            req_params = request.params.copy()
        return req_params
    
    def _validate_params(self, req_params):
        if req_params.has_key(END_DATE) and not req_params.has_key(START_DATE):
            raise BadArgumentError('if an end_date is specified a start_date must also be specified')
            return False
        else :
            return True
    
    def _parse_params(self, req_params):
        params = {}
        param_count = 0
        
        def _set_string_param(paramKey):
            if req_params.has_key(paramKey):
                params[paramKey] = str(req_params[paramKey])
                return True
            else :
                params[paramKey] = ""
                return False
                
        def _set_boolean_param(paramKey):
            if req_params.has_key(paramKey):
                params[paramKey] = req_params[paramKey][0].lower() == 't'
                return True
            else :
                params[paramKey] = False
                return False
        
        if _set_string_param(START_DATE) : param_count += 1
        if _set_string_param(IDENTITY) : param_count += 1
        if _set_string_param(ANY_TAGS) : param_count += 1
        _set_string_param(END_DATE)
        _set_boolean_param(IDS_ONLY)
        
        params['param_count'] = param_count
        
        return params

    def _get_view(self,view_name = '_design/learningregistry/_view/resources',keys=[], include_docs = False):
        s = couchdb.Server(appConfig['couchdb.url'])
        db = s[appConfig['couchdb.db.resourcedata']]
        if len(keys) > 0:
            view = db.view(view_name, include_docs=include_docs, keys=keys, stale='ok')
        else:
            view = db.view(view_name, include_docs=include_docs, stale='ok')
        return view
    
    def _get_keys(self, params):
        print("gettingslicekeys")
        keys = []
        dates = []
        if params[END_DATE] != "" :
            dates = self._get_dates(params);
        else :
            if params[START_DATE] != "" :
                dates = [params[START_DATE]]
        identity = params[IDENTITY].lower()
        any_tags = params[ANY_TAGS].lower()
        param_count = params['param_count']
        
        if any_tags != "" :
            any_tag_list = any_tags.split(",")
        
        if param_count == 1:
            if len(dates)>0 :
                for date in dates :
                    keys.append(date) 
            elif identity != "" :
                keys.append(identity) 
            elif any_tags != "" :
                for tag in any_tag_list:
                    keys.append(tag) 
        elif param_count == 2:
            if len(dates) == 0 :
                for tag in any_tag_list:
                    keys.append([identity, tag]) 
            elif identity == "" :
                for tag in any_tag_list:
                    for date in dates:
                        print("slicegotdateandtag: " + str([date, tag]))
                        keys.append([date, tag]) 
            elif any_tags == "" :
                for date in dates:
                    keys.append([date, identity]) 
        elif param_count == 3:
            for tag in any_tag_list:
                for date in dates:
                    keys.append([date, identity, tag]) 
         
        return keys
    
    
        
    def _get_dates(self, params):
        cur = datetime.strptime(params[START_DATE],"%Y-%m-%d")
        end = datetime.strptime(params[END_DATE], "%Y-%m-%d")
        day = timedelta(days=1)
    
        dates = []
        while cur != end:
            date = datetime.strftime(cur,"%Y-%m-%d")
            dates.append(date)
            cur += day
        print repr(dates)
        return dates
        
        
    def format_data(self,keys_only,data, keys, forceUnique):
        sentIDs = []
        yield '{"keyCount":'+str(len(keys)) +', "resultCount":"'+str(len(data)) +', "replyStart":"'+str(datetime.today())+'", "documents":['
        num_sent = 0
        if data is not None and len(data) > 0:
            for row in data:
                if (row.id not in sentIDs) or not forceUnique:
                    sentIDs.append(row.id)
                    if keys_only:
                        return_data = {"doc_ID":row.id} 
                    else:
                        # Get the resource data and update  with the node timestamp data
                        # That the view  has in value['timestamp']
                        resourceData = {}
                        resourceData = row.doc
                        return_data = {"doc_ID":row.id, "resource_data_description":resourceData}
                    num_sent = num_sent + 1
                    if num_sent < len(data): 
                        yield json.dumps(return_data) + ','
                    else:
                        yield json.dumps(return_data) 
        yield '], "replyEnd":"'+str(datetime.today())+'"}'    
        
#        if __name__ == '__main__':
#            param = {START_DATE: "2011-03-10", END_DATE: "2011-05-01", IDENTITY: "NSDL 2 LR Data Pump", 'search_key': 'Arithmetic'}
#            keys(param)


    
    
    def index(self, format='html'):
        """GET /slices: All items in the collection"""
        # url('slices')
        req_params = self._get_params()
        valid = self._validate_params(req_params)
        if valid :
            params = self._parse_params(req_params)
            keys = self._get_keys(params)
            data = []
            if len(keys) > 0 : data = self._get_view('_design/learningregistry/_view/slice', keys, True)	
            return self.format_data(params[IDS_ONLY],data,keys,True)
        
        else :
            return "Bad argument"
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
        
class BadArgumentError(Exception):
    def __init__(self, msg):
        self.msg = msg
        self.datetime_now = datetime.utcnow().isoformat()
        self.path_url = request.path_url

