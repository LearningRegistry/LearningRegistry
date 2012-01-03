import logging, urllib2, json, couchdb
from lr.model.base_model import appConfig
import lr.lib.helpers as h

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from datetime import datetime, timedelta
from lr.lib.oaipmherrors import *
import types
from lr.lib import resumption_token

log = logging.getLogger(__name__)

END_DATE = 'until'
START_DATE = 'from'
IDENTITY = 'identity'
ANY_TAGS = 'any_tags'
#FULL_DOCS = 'full_docs'
IDS_ONLY = 'ids_only'
CALLBACK = 'callback'
RESUMPTION_TOKEN = 'resumption_token'

SLICE_SERVICE_DOC = "access:slice"

class SliceController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    # map.resource('slice', 'slices')
    def __before__(self):
        self.enable_flow_control = False
        self.fc_id_limit = None
        self.fc_doc_limit = None
        
        self.serviceDoc = h.getServiceDocument("access:slice")
        if self.serviceDoc != None:
            if 'service_id' in self.serviceDoc:
                self.service_id = self.serviceDoc['service_id']
                
            if 'service_data' in self.serviceDoc:
                serviceData = self.serviceDoc['service_data']
                if 'flow_control' in serviceData:
                    self.enable_flow_control = serviceData['flow_control']
                
                if self.enable_flow_control and 'id_limit' in serviceData:
                    self.fc_id_limit = serviceData['id_limit']
                elif self.enable_flow_control:
                    self.fc_id_limit = 100
                
                if self.enable_flow_control and 'doc_limit' in serviceData:
                    self.fc_doc_limit = serviceData['doc_limit']
                elif self.enable_flow_control:
                    self.fc_doc_limit = 100
    

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
        
        def _set_string_param(paramKey, setifempty=True, defaultWhenEmpty=""):
            if req_params.has_key(paramKey):
                params[paramKey] = str(req_params[paramKey])
                return True
            elif setifempty:
                params[paramKey] = defaultWhenEmpty
                return False
            else:
                return False
                
        def _set_int_param(paramKey, setifempty=True):
            if req_params.has_key(paramKey):
                params[paramKey] = int(req_params[paramKey])
                return True
            elif setifempty:
                params[paramKey] = None
                return False
            else:
                return False
            
        def _set_boolean_param(paramKey, setifempty=True):
            if req_params.has_key(paramKey):
                params[paramKey] = req_params[paramKey].lower() in ["t", "true", "y", "yes"]
                return True
            elif setifempty:
                params[paramKey] = False
                return False
            else:
                return False
        
        if _set_string_param(START_DATE) : param_count += 1
        if _set_string_param(IDENTITY) : param_count += 1
        if _set_string_param(ANY_TAGS) : param_count += 1
        _set_string_param(END_DATE)
        _set_boolean_param(IDS_ONLY)
        _set_string_param(CALLBACK, False)
        _set_string_param(RESUMPTION_TOKEN, True, None)
        
        if params[RESUMPTION_TOKEN] is not None:
            params[RESUMPTION_TOKEN] = resumption_token.parse_token(self.service_id, params[RESUMPTION_TOKEN])
            if len([i for i in ["offset", "keys"] if i in params[RESUMPTION_TOKEN]]) != 2:
                msg = ": Unknown Error"
                if "error" in params[RESUMPTION_TOKEN]:
                    msg = ": %s" % params[RESUMPTION_TOKEN]["error"]
                raise BadArgumentError("Bad Resumption Token%s" % msg)
                    
        params['param_count'] = param_count
        log.debug(json.dumps(params))
        return params

    def _get_view(self,view_name = '_design/learningregistry-slice/_view/docs',keys=[], include_docs = False, resumptionToken=None, limit=None):
        db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])
        
        opts = {"stale": "ok", "reduce": False }
        
        if include_docs:
            opts["include_docs"] = True
        
        if self.enable_flow_control and resumptionToken != None:
            if resumptionToken != None:
                opts["skip"] = resumptionToken["offset"]
                opts["keys"] = resumptionToken["keys"]
        else:
            opts["keys"] = keys

        if limit != None:
                    opts["limit"] = limit
        
        if len(opts["keys"]) > 0:
            view = h.getView(database_url=db_url, method="POST", view_name=view_name, **opts)#,stale='ok'):
        else:
            view = h.getView(database_url=db_url,view_name=view_name, **opts)#,stale='ok'):
        return view
    
    def _get_view_total(self,view_name = '_design/learningregistry-slice/_view/docs',keys=[], resumptionToken=None):
        db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])
        
        opts = {"stale": appConfig['couchdb.stale.flag'], "reduce": True, "group": True }
        
        if self.enable_flow_control and resumptionToken != None:
            opts["keys"] = resumptionToken["keys"]
        else:
            opts["keys"] = keys
            
        if len(opts["keys"]) > 0:
            view = h.getView(database_url=db_url, method="POST", view_name=view_name, **opts)#,stale='ok'):
        else:
            view = h.getView(database_url=db_url,view_name=view_name, **opts)#,stale='ok'):
            
        totalDocs = 0
        for row in view:
            if "value" in row:
                totalDocs += row["value"]
        return totalDocs
    
    def _get_keys(self, params):
        log.debug("gettingslicekeys")
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
            wrapped_any_tag_list = []
            for tag in any_tag_list:
                try:
                    #tag = "{\"tag\":\""+tag+"\"}"
                    tag = {"tag":tag}
                    wrapped_any_tag_list.append(tag)
                    print("wrapped tag: " + str(tag))
                except:
                    print("failed to wrap tag: " + str(tag))
                    pass
            any_tag_list = wrapped_any_tag_list
        if(identity != ""):
            try:
                #identity = "{\"tag\":\""+identity+"\"}"
                identity = {"id":identity}
                print("wrapped identity: " + str(identity))
            except:
            	pass
        
        wrapped_dates = []
        for date in dates:
            try:
                #date = "{\"tag\":\""+date+"\"}"
                date = {"date":date}
                wrapped_dates.append(date)
                print("wrapped date: " + str(date))
            except:
                print("failed to wrap date: " + str(date))
                pass
        dates = wrapped_dates
        
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
                        log.debug("slicegotdateandtag: " + str([date, tag]))
                        keys.append([date, tag])
            elif any_tags == "" :
                for date in dates:
                    keys.append([date, identity])
        elif param_count == 3:
            for tag in any_tag_list:
                for date in dates:
                    keys.append([date, identity, tag])
         
        print("final slice keys: " + str(keys))
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
        log.debug(repr(dates))
        return dates
        
        
    def format_data(self,keys_only,docs, keys, forceUnique, current_rt=None):
        sentIDs = []
        prefix = '{"documents":[\n'
        num_sent = 0
        doc_count = 0
        if docs is not None:
            for row in docs:
                doc_count += 1
                alreadySent = (row["id"] in sentIDs)
                if not alreadySent or not forceUnique:
                    sentIDs.append(row["id"])
                    if keys_only:
                        return_data = {"doc_ID":row["id"]}
                    else:
                        # Get the resource data and update with the node timestamp data
                        # That the view has in value['timestamp']
                        resourceData = {}
                        resourceData = row["doc"]
                        return_data = {"doc_ID":row["id"], "resource_data_description":resourceData}
                    yield prefix + json.dumps(return_data)
                    num_sent += 1
                    prefix = ",\n"
                else:
                    log.debug("{0} skipping: alreadySent {1} / forceUnique {2}".format(doc_count, repr(alreadySent), forceUnique))
        
        if doc_count == 0:
            yield prefix
        
        maxResults = self._get_view_total(keys=keys,resumptionToken=current_rt)
        
        rt = " "
        if self.enable_flow_control:
            if current_rt != None and "offset" in current_rt and current_rt["offset"] is not None:
                offset = current_rt["offset"]
            else:
                offset = 0
                
            if offset+doc_count < maxResults:
                rt = ''' "resumption_token":"{0}", '''.format(resumption_token.get_offset_token(self.service_id, offset=offset+doc_count, keys=keys))

        

        yield '\n],'+rt+'"resultCount":'+str(maxResults) +'}'
        
# if __name__ == '__main__':
# param = {START_DATE: "2011-03-10", END_DATE: "2011-05-01", IDENTITY: "NSDL 2 LR Data Pump", 'search_key': 'Arithmetic'}
# keys(param)


    
    
    def index(self, format='html'):
        """GET /slices: All items in the collection"""
        # url('slices')
        
        def getResponse(keys, params):
            if len(keys) > 0 :
                limit = None
                if self.enable_flow_control:
                    if params[IDS_ONLY]:
                        limit = self.fc_id_limit
                    else:
                        limit = self.fc_doc_limit 

                if CALLBACK in params:
                    yield "{0}(".format(params[CALLBACK])
                docs = self._get_view('_design/learningregistry-slice/_view/docs', keys, not params[IDS_ONLY], params[RESUMPTION_TOKEN], limit)
                for i in self.format_data(params[IDS_ONLY],docs,keys,True,params[RESUMPTION_TOKEN]):
                    yield i
                if CALLBACK in params:
                    yield ");"
        try:
            req_params = self._get_params()
            valid = self._validate_params(req_params)
            if valid :
                params = self._parse_params(req_params)
                keys = self._get_keys(params)
                return getResponse(keys, params)
    
            else :
                raise BadArgumentError()
        except BadArgumentError as bae:
            return '{ "error": "{0}" }'.format(bae.msg)
        except Exception as e:
            log.error(e.message)
            return '{ "error": "Unknown Error, check log." }'
        #return params["start_date"] + " " + params["identity"] + " " + params["search_key"] + "\n" + str(self.format_data(False,data))
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
        # <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        # h.form(url('slice', id=ID),
        # method='put')
        # url('slice', id=ID)

    def delete(self, id):
        """DELETE /slices/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        # <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        # h.form(url('slice', id=ID),
        # method='delete')
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
