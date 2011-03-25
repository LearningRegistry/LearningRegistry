import logging, json
from lr.lib.harvest import harvest
from datetime import datetime
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest
from lr.lib.base import BaseController, render
log = logging.getLogger(__name__)
time_format = '%Y-%m-%d %H:%M:%S.%f'
import ast
class HarvestController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('harvest', 'harvest')
    def harvest(self, params, body, verb):
        h = harvest()
        def getrecord():
          data = self.get_base_response(verb,body)
          by_doc_ID = params.has_key('by_doc_ID') and ast.literal_eval(str(params['by_doc_ID']))
          by_resource_ID = params.has_key('by_resource_ID') and ast.literal_eval(str(params['by_resource_ID']))
          if not params.has_key('request_id'):
            data['OK'] = False
            data['error'] = 'badArgument'
            return json.dumps(data)
          if by_doc_ID and by_resource_ID:
            data['OK'] = False
            data['error'] = 'badArgument'
            return json.dumps(data)

          request_id = params['request_id']          
          if by_doc_ID:
            records = map(lambda doc: {'record':{"header":{'identifier':doc.id, 'datestamp':datetime.today().strftime(time_format),'status':'active'}},'resource_data':doc},[h.get_record(request_id)])
          else:
            records = map(lambda doc: {'record':{"header":{'identifier':doc.id, 'datestamp':datetime.today().strftime(time_format),'status':'active'}},'resource_data':doc},h.get_records_by_resource(request_id))
          data['getrecord'] ={
            'record': records
            }
          return json.dumps(data)
        def listidentifiers():
            from_date = datetime.strptime(params['from'],time_format)
            until_date = datetime.strptime(params['until'],time_format)
            return self.list_identifiers(from_date,until_date,h,body,params,verb)            
        def listrecords():
            from_date = datetime.strptime(params['from'],time_format)
            until_date = datetime.strptime(params['until'],time_format)
            return self.list_records(from_date,until_date,h,body,params,verb)
        def identify():
            data = self.get_base_response(verb,body)
            data['identify']={
                                    'node_id':        'string',
                                    'repositoryName':    'string',
                                    'baseURL':        'string',
                                    'protocolVersion':    '2.0',
                                    'service_version':    'string',
                                    'earliestDatestamp':    'string',
                                    'deletedRecord':    'string',
                                    'granularity':        'string',
                                    'adminEmail':        'string'
                                 }
            return json.dumps(data)
        def listmetadataformats():
            data = self.get_base_response(verb,body)
            data['listmetadataformats']=h.list_metadata_formats()
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
        return switch[verb]()
    def list_records(self,from_date, until_date, h , body , params, verb = 'GET' ):
        data = self.get_base_response(verb,body)
        data['request']['from'] = params['from']
        data['request']['until'] = params['until']
        def debug_map(doc):
            data ={'record':{"header":{'identifier':doc.id, 'datestamp':datetime.today().strftime(time_format),'status':'active'},'resource_data':doc}}
            return data
        if from_date > until_date:
          data['OK'] = False
          data['error'] = 'badArgument'
        else:
          data['listrecords'] =   map(debug_map,h.list_records(from_date,until_date))
        return json.dumps(data)

    def list_identifiers(self,from_date, until_date,h,body ,params, verb = 'GET'):
        data = self.get_base_response(verb,body)
        data['request']['from'] = params['from']
        data['request']['until'] = params['until']
        data['listidentifiers'] =  map(lambda doc: {"header":{'identifier':doc, 'datestamp':datetime.today().strftime(time_format),'status':'active'}},h.list_identifiers(from_date,until_date))
        return json.dumps(data)

    def get_base_response(self, verb, body):
      return {
               'OK':True,
               'error':'',
               'responseDate':datetime.today().strftime(time_format),
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

