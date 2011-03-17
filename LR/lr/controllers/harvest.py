import logging, json
from lr.lib.harvest import harvest
from datetime import datetime
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)
time_format = '%Y-%m-%d %H:%M:%S.%f'

class HarvestController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('harvest', 'harvest')

    def index(self, format='html'):
        """GET /harvest: All items in the collection"""
        # url('harvest')

    def create(self):
        """POST /harvest: Create a new item"""
        # url('harvest')

    def new(self, format='html'):
        """GET /harvest/new: Form to create a new item"""
        # url('new_harvest')

    def update(self, id):
        """PUT /harvest/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('harvest', id=ID),
        #           method='put')
        # url('harvest', id=ID)
        post_data = json.loads(request.body)      
        from_date = datetime.strptime(post_data['from'],time_format)
        until_date = datetime.strptime(post_data['until'],time_format)
        def listidentifiers():
            return self.list_identifiers(from_date,until_date,'POST')            
        def listrecords():
            return self.list_records(from_date,until_date,'POST')
        switch = {
                    'listrecords':listrecords,
                    'listidentifiers':listidentifiers,
                 }
        return switch[id]()
    def delete(self, id):
        """DELETE /harvest/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('harvest', id=ID),
        #           method='delete')
        # url('harvest', id=ID)
    def list_records(self,from_date, until_date,h, verb = 'GET'):
        data = self.get_base_response(verb)
        data['request']['from'] = request.params['from']
        data['request']['until'] = request.params['until']
        data['listrecords'] =   map(lambda doc: {'record':{"header":{'identifier':doc.id, 'datestamp':datetime.today().strftime(time_format),'status':'active'}},'resource_data':doc},h.list_records(from_date,until_date))
        return json.dumps(data)
    def list_identifiers(self,from_date, until_date,h, verb = 'GET'):
        data = self.get_base_response(verb)
        data['request']['from'] = request.params['from']
        data['request']['until'] = request.params['until']
        data['listidentifiers'] =  map(lambda doc: {"header":{'identifier':doc, 'datestamp':datetime.today().strftime(time_format),'status':'active'}},h.list_identifiers(from_date,until_date))
        return json.dumps(data)
    def get_base_response(self, verb):
      return {
               'OK':True,
               'error':'',
               'responseDate':datetime.today().strftime(time_format),
               'request':{
                 'verb':verb,
                 'HTTP_request': request.body
                 }    
              }
    def show(self, id, format='html'):
        """GET /harvest/id: Show a specific item"""
        h = harvest()
        def getrecord():
          by_doc_ID =request.params.has_key('by_doc_ID') and request.params['by_doc_ID']
          request_id = request.params['request_id']
          if by_doc_ID:
            return json.dumps(h.get_record(request_id))
          else:
            return json.dumps(h.get_records_by_resource(request_id))
        def listidentifiers():
            from_date = datetime.strptime(request.params['from'],time_format)
            until_date = datetime.strptime(request.params['until'],time_format)
            return self.list_identifiers(from_date,until_date,h)            
        def listrecords():
            from_date = datetime.strptime(request.params['from'],time_format)
            until_date = datetime.strptime(request.params['until'],time_format)
            return self.list_records(from_date,until_date,h)
        def identify():
            data = self.get_base_response("GET")
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
            data = self.get_base_response("GET")
            data['metadataFormat']=h.list_metadata_formats()
            return json.dumps(data)
        def listsets():
            data = self.get_base_response("GET")
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
        return switch[id]()
        # url('harvest', id=ID)

    def edit(self, id, format='html'):
        """GET /harvest/id/edit: Form to edit an existing item"""
        # url('edit_harvest', id=ID)
