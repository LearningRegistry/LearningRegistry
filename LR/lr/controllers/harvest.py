import logging, json
from lr.lib.harvest import harvest
import lr.lib.helpers as helpers
from urllib import unquote_plus
import iso8601
from datetime import datetime
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest
from lr.lib.base import BaseController, render
import lr.lib.helpers
import lr.lib.resumption_token as rt
log = logging.getLogger(__name__)
import ast
import string
import re
from lr.model import LRNode as sourceLRNode, \
            NodeServiceModel, ResourceDataModel, LRNodeModel, defaultCouchServer, appConfig
BASIC_HARVEST_SERVICE_DOC = appConfig['lr.harvest.docid']
class HarvestController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('harvest', 'harvest')call
    REQUESTID = "request_ID"
    def _getServiceDocment(self,full_docs):
        self.enable_flow_control = False
        self.limit = None        
        self.service_id = None
        serviceDoc = helpers.getServiceDocument(BASIC_HARVEST_SERVICE_DOC)
        if serviceDoc != None:
            if 'service_id' in serviceDoc:
                self.service_id = serviceDoc['service_id']
                
            if 'service_data' in serviceDoc:
                serviceData = serviceDoc['service_data']
                if 'flow_control' in serviceData:
                    self.enable_flow_control = serviceData['flow_control']
                limit_type = 'id_limit'
                if full_docs:
                    limit_type = "doc_limit"
                if self.enable_flow_control and limit_type in serviceData:
                    self.limit = serviceData[limit_type]
                elif self.enable_flow_control:
                    self.limit = 100
                if 'metadataformats' in serviceData:    
                    self.metadataFormats = serviceData['metadataformats']
    def __parse_date(self,date):
        last_update = helpers.convertToISO8601UTC(date)    
        last_update_date = iso8601.parse_date(date)
        return helpers.harvestTimeFormat(last_update)
    def _check_bool_param(self,params,key):
        if params.has_key(key):
            raw_value = string.lower(str(params[key]))
            if len(raw_value) > 1:
#                print string.capitalize(raw_value)
                return ast.literal_eval(string.capitalize(raw_value))
            elif len(raw_value) == 1:
                if raw_value == 't':
                    return True
                elif raw_value == 'f':
                    return False                
        return False
    def harvest(self, params, body, verb):
        h = harvest()
        def getrecord():
          data = self.get_base_response(verb,body)
          by_doc_ID = self._check_bool_param(params,'by_doc_ID')
          by_resource_ID = self._check_bool_param(params,'by_resource_ID') 
          if not params.has_key(self.REQUESTID) and not params.has_key(self.REQUESTID.lower()):
            data['OK'] = False
            data['error'] = 'badArgument'
            return json.dumps(data)
          if by_doc_ID and by_resource_ID:
            data['OK'] = False
            data['error'] = 'badArgument'
            return json.dumps(data)          
          if params.has_key(self.REQUESTID):
            request_id = params[self.REQUESTID]
          elif params.has_key(self.REQUESTID.lower()):
            request_id = params[self.REQUESTID.lower()]
          if by_doc_ID:
            document = h.get_record(request_id)
            if document is not None:
                records = map(lambda doc: {"header":{'identifier':doc['_id'], 'datestamp':helpers.convertToISO8601Zformat(datetime.today()),'status':'active'},'resource_data':doc},[document])
            else:
                records = []
          else:
            request_id = unquote_plus(request_id)
            records = map(lambda doc: {"header":{'identifier':doc['_id'], 'datestamp':helpers.convertToISO8601Zformat(datetime.today()),'status':'active'},'resource_data':doc},h.get_records_by_resource(request_id))
          if len(records) == 0:
            data['OK'] = False
            data['error'] = 'idDoesNotExist'
            return json.dumps(data)            
          data['getrecord'] ={
            'record': records
          }
          data['request']['identifier']  = request_id
          data['request']['by_doc_ID'] = by_doc_ID
          data['request']['by_resource_ID'] = by_resource_ID
          return json.dumps(data)
        def listidentifiers():
            return self.listGeneral(h,body,params,False,verb)            
        def listrecords():            
            return self.listGeneral(h,body,params,True,verb)
        def identify():
            data = self.get_base_response(verb,body)
            serviceDoc = helpers.getServiceDocument(BASIC_HARVEST_SERVICE_DOC)
            data['identify']={
                "node_id":sourceLRNode.nodeDescription.node_name,
                "repositoryName":sourceLRNode.communityDescription.community_name,
                "baseURL":serviceDoc['service_endpoint'],
                "protocolVersion":"2.0",
                "service_version":serviceDoc['service_version'],
                "earliestDatestamp":h.earliestDate(),
                "deletedRecord":sourceLRNode.nodeDescription.node_policy['deleted_data_policy'],
                "granularity":helpers.getDatetimePrecision(serviceDoc),
                "adminEmail":sourceLRNode.nodeDescription.node_admin_identity
            }
            return json.dumps(data)
        def listmetadataformats():
            def formatFromDesignDoc(doc):
                if type(doc['metadataFormat']) == str:
                    prefix = doc['metadataFormat']
                else:
                    prefix = doc['metadataFormat']['metadataPrefix']
                return {'metadataformat':{"metadataPrefix":prefix}}
            self._getServiceDocment(False)
            data = self.get_base_response(verb,body)
            data['listmetadataformats']=map(formatFromDesignDoc,self.metadataFormats)
            return json.dumps(data)
        def listsets():
            data = self.get_base_response(verb,body)
            data['OK']=False
            data['error']='noSetHierarchy'
            return json.dumps(data)
        switch = {
                    'getrecord':getrecord,
                    'listrecords':listrecords,
                    'listidentifiers':listidentifiers,
                    'identify': identify,
                    'listmetadataformats': listmetadataformats,                   
                    'listsets': listsets
                 }
        if switch.has_key(verb):
            return switch[verb]()
        else:
            abort(500,"Invalid Verb")
    def _test_time_params(self, params):
        
        if not params.has_key('from') or (params.has_key('from') and params['from'] is None):
            from_date = self.__parse_date('1990-10-10 12:12:12.0')
        else:
            r = re.compile('.[0-9]+Z')
            from_date = re.sub(r,"",self.__parse_date(params['from']))
        if not params.has_key('until') or (params.has_key('until') and params['until'] is None):
            until_date = self.__parse_date(datetime.utcnow().isoformat() + "Z")
        else:
            until_date = self.__parse_date(params['until'])
        return from_date,until_date         
    def listGeneral(self, h , body , params, includeDocs,verb = 'GET'):                        
        data = self.get_base_response(verb,body)
        try:
            from_date, until_date = self._test_time_params(params)
        except Exception as ex:
            log.error(ex)
            data['OK'] = False
            data['error'] = 'badArgument'
            yield json.dumps(data)
            return
        data['request']['from'] = from_date
        data['request']['until'] = until_date         
        if from_date > until_date:
          data['OK'] = False
          data['error'] = 'badArgument'
          yield json.dumps(data)
        else:
            self._getServiceDocment(includeDocs)        
            resumption_token = None
            count = 0
            lastID = None
            lastKey = None
            if self.enable_flow_control and params.has_key('resumption_token'):
                resumption_token = rt.parse_token(self.service_id,params['resumption_token'])                                    
            if includeDocs:       
                data['listrecords'] =  []   
                viewResults = h.list_records(from_date,until_date,resumption_token=resumption_token, limit=self.limit)                
                debug_map = lambda doc: {'record':{"header":{'identifier':doc['id'], 'datestamp':doc['key']+"Z",'status':'active'},'resource_data':doc['doc']}}                
            else:
                data['listidentifiers'] =  []   
                viewResults = h.list_identifiers(from_date,until_date,resumption_token=resumption_token, limit=self.limit)
                debug_map = lambda doc:{"header":{'identifier':doc['id'], 'datestamp':doc['key']+"Z",'status':'active'}}                
            base_response =  json.dumps(data).split('[')            
            yield base_response[0] +'['
            first = True
            for data in viewResults:                        
                lastID = data['id']
                lastKey = data['key']
                count += 1
                if not first:
                    yield ',\n'
                first = False
                yield json.dumps(debug_map(data))
            if self.enable_flow_control and self.limit <= count:
                token = rt.get_token(serviceid=self.service_id,startkey=lastKey,endkey=helpers.convertToISO8601Zformat(until_date),startkey_docid=lastID,from_date=helpers.convertToISO8601Zformat(from_date),until_date=helpers.convertToISO8601Zformat(until_date))
                resp = base_response[1]
                yield resp[:-1] +(',"resumption_token":"%s"' %token) +resp[-1:]
            elif self.limit > count:
                resp = base_response[1]
                yield resp[:-1] +(',"resumption_token":"%s"' %'null') +resp[-1:]    
            else:
                yield base_response[1]
        

    def get_base_response(self, verb, body):
      return {
               'OK':True,
               'error':'',
               'responseDate':helpers.convertToISO8601Zformat(datetime.today()),
               'request':{
                 'verb':verb,
                 'HTTP_request': body
                 }    
              }


    def index(self, format='html'):
        """GET /harvest: All items in the collection"""
        abort(405,'Method not allowed')

    def create(self):
        """POST /harvest: Create a new item"""
        abort(405,'Method not allowed')

    def new(self, format='html'):
        """GET /harvest/new: Form to create a new item"""
        abort(405,'Method not allowed')
        # url('new_harvest')

    def update(self, id):
        """PUT /harvest/id: Update an existing item"""
        abort(405,'Method not allowed')
    def delete(self, id):
        """DELETE /harvest/id: Delete an existing item"""
        abort(405,'Method not allowed')
    def show(self, id, format='html'):
        """GET /harvest/id: Show a specific item"""
        callBackKey = 'callback'
        if request.params.has_key(callBackKey):
            def jsonp(callback,params,body):
                yield '{0}('.format(callback)
                for i in self.harvest(params,body,id):
                    yield i
                yield ')'
            return jsonp(request.params[callBackKey],request.params,request.body)
        else:
            return self.harvest(request.params,request.body,id)
    def edit(self, id, format='html'):
        """GET /harvest/id/edit: Form to edit an existing item"""
        abort(405,'Method not allowed')

    #code below is to allow posting to /harvest/VERB
    #as REST uses POST only for creating, posting to an existing doc isn't allowed
    @rest.dispatch_on(POST='create_getrecord')
    def getrecord(self):
       """getrecord"""
    def create_getrecord(self):     
        post_data = json.loads(request.body)      
        return self.harvest(post_data,request.body,'getrecord')

    @rest.dispatch_on(POST='create_listrecords')
    def listrecords(self):
       """listrecords"""
       log.debug('test')
    def create_listrecords(self):
       params = json.loads(request.body)       
       return self.harvest(params,request.body,'listrecords')

    @rest.dispatch_on(POST='create_listidentifiers')
    def listidentifiers(self):
       """listidentifiers"""
       log.debug('test')
    def create_listidentifiers(self):
       params = json.loads(request.body)       
       return self.harvest(params,request.body,'listidentifiers')

    @rest.dispatch_on(POST='create_identify')
    def identify(self):
       """identify"""
       log.debug('test')
    def create_identify(self):       
       return self.harvest(None,request.body,'identify')

    @rest.dispatch_on(POST='create_listmetadataformats')
    def listmetadataformats(self):
       """listmetadataformats"""
    def create_listmetadataformats(self):      
       return self.harvest(None,request.body,'listmetadataformats')

    @rest.dispatch_on(POST='create_listsets')
    def listsets(self):
        """listsets"""
    def create_listsets(self):
       return self.harvest(None,request.body,'listsets')

