import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.controllers.harvest import HarvestController

from lr.lib.base import BaseController, render
from lr.lib.oaipmh import oaipmh
from datetime import datetime
import json, iso8601
from couchdb.http import ResourceNotFound
from lr.lib.oaipmherrors import *

log = logging.getLogger(__name__)

class OaiPmhController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('OAI-PMH', 'OAI-PMH')
    def _isTrue(self, value):
        return str(value).lower() in ['true', 't', '1', 'y', 'yes']
    
    def _parseParams(self):
        params = {}
        if (request.params.has_key('verb') == False) :
            raise BadVerbError()
        
        verb = params["verb"] = request.params['verb']
        
        if verb not in ["GetRecord", "ListRecords", "ListIdentifiers", "Identify", "ListMetadataFormats", "ListSets"]:
            raise BadVerbError()
        
        if verb == 'GetRecord' or verb == 'ListRecords' or verb == 'ListIdentifiers':        
            if request.params.has_key('metadataPrefix') == False:
                raise BadArgumentError('metadataPrefix is a required parameter.', verb)
            params["metadataPrefix"] = metadataPrefix = request.params['metadataPrefix']
        
        if verb == 'GetRecord' or verb == 'ListMetadataFormats':
            if request.params.has_key('by_doc_ID') and request.params.has_key('by_resource_ID'):
                if self._isTrue(request.params['by_doc_ID']) == self._isTrue(request.params['by_resource_ID']):
                    raise BadArgumentError('by_doc_ID and by_resource_ID have conflicting values.', verb)
                
            if request.params.has_key('by_doc_ID'):
                params['by_doc_ID'] = self._isTrue(request.params['by_doc_ID'])
                params['by_resource_ID'] = not params['by_doc_ID']
            else:
                params['by_doc_ID'] = False
                params['by_resource_ID'] = not params['by_doc_ID']
            
            if request.params.has_key('by_resource_ID'):
                params['by_resource_ID'] = self._isTrue(request.param['by_doc_ID'])
                params['by_doc_ID'] = not params['by_resource_ID']
        
        if verb == 'ListRecords' or verb == 'ListIdentifiers':
            if request.params.has_key('from'):
                try:
                    from_date = iso8601.parse_date(request.params['from'])
                    params['from'] = h.convertToISO8601UTC(from_date)
                except:
                    raise BadArgumentError('from does not parse to ISO 8601.', verb)
            else:
                params['from'] = None
            
            if request.params.has_key('until'):
                try:
                    until_date = iso8601.parse_date(request.params['until'])
                    params['until'] = h.convertToISO8601UTC(until_date)
                except:
                    raise BadArgumentError('until does not parse to ISO 8601.', verb)
            else:
                params['until'] = None
                
            if params['from'] != None and params['until'] != None and params['from'] > params['until']:
                raise BadArgumentError('until cannot preceed from.', verb)
        
        if verb in ['ListMetadataFormats', 'GetRecord']  and request.params.has_key('identifier'):
            params['identifier'] = request.params['identifier']
        
        if verb == 'GetRecord' and params.has_key('identifier') == False:
            raise BadArgumentError('identifier is a required parameter.', verb)
        
        return params

    def _returnResponse(self, body):
        response.headers["Content-Type"] = "text/xml; charset=utf-8"
        return body
                                 
    
    def _initRender(self,params):
        c.datetime_now = datetime.utcnow().isoformat()
        c.path_url = request.path_url
        if params.has_key("by_doc_ID"):
            c.by_doc_ID = params["by_doc_ID"]
        if params.has_key("by_resource_ID"):
            c.by_resource_ID = params["by_resource_ID"]
        if params.has_key("metadataPrefix"):
            c.metadataPrefix = params["metadataPrefix"]
        if params.has_key("from"):
            c.from_date = params["from"]
        if params.has_key("until"):
            c.until_date = params["until"]
        

    def index(self, format='html'):
        """GET /OAI-PMH: All items in the collection"""
        o = oaipmh()
        
        def GetRecord(params):
            try:
                c.identifier = params["identifier"]
                if params["by_doc_ID"]  == True:
                    c.docList = [o.get_record(params["identifier"])]
                else:
                    c.docList = o.get_records_by_resource(params["identifier"])
                    if len(c.docList) == 0:
                        raise IdDoesNotExistError(params['verb'])
            except ResourceNotFound:
                raise IdDoesNotExistError(params['verb'])
            
            self._initRender(params)
            
            if c.docList != None:
                for doc in c.docList:
                    if c.metadataPrefix not in doc["payload_schema"]:
                        raise CannotDisseminateFormatError(params['verb'])

            body = "<error/>"
            try:
                body = render("/oaipmh-GetRecord.mako")
            except:
                log.exception("Unable to render template")
            return self._returnResponse(body)
        
        
        def ListIdentifiers(params):
            body = ""
            try:
                c.identifiers = o.list_identifiers(params["metadataPrefix"],from_date=params["from"], until_date=params["until"] )
                
                if len(c.identifiers) == 0:
                    raise NoRecordsMatchError(params['verb'])
                
                self._initRender(params)
                body = render("/oaipmh-ListIdentifiers.mako")
            except NoRecordsMatchError as e:
                raise e
            except:
                log.exception("Unable to render template")
            return self._returnResponse(body)
        
        def ListRecords(params):
            body = ""
            try:
                c.records = o.list_records(params["metadataPrefix"],from_date=params["from"], until_date=params["until"] )
                
                if len(c.records) == 0:
                    raise NoRecordsMatchError(params['verb'])
                
                self._initRender(params)
                body = render("/oaipmh-ListRecords.mako")
            except NoRecordsMatchError as e:
                raise e
            except:
                log.exception("Unable to render template")
            return self._returnResponse(body)
        
        def Identify(params=None):
            body = ""
            try:
                self._initRender(params)
                c.identify = o.identify()
                body = render("/oaipmh-Identify.mako")
            except:
                raise BadVerbError()
            return self._returnResponse(body)
        
        def ListSets(params=None):
            raise NoSetHierarchyError(verb)
            
        def NotYetSupported(params=None):
            raise BadVerbError()
            
        switch = {
                  'GetRecord': GetRecord,
                  'ListRecords': ListRecords,
                  'ListIdentifiers': ListIdentifiers,
                  'Identify': Identify,
                  'ListMetadataFormats': NotYetSupported,
                  'ListSets': ListSets
                  }
        try:
            params = self._parseParams()
        
            verb = params['verb']
            
            return switch[verb](params)
        except Error as e:
            c.error = e
            return self._returnResponse(render('oaipmh-Error.mako'))
        # url('OAI-PMH')

    def create(self):
        """POST /OAI-PMH: Create a new item"""
        # url('OAI-PMH')

    def new(self, format='html'):
        """GET /OAI-PMH/new: Form to create a new item"""
        # url('new_OAI-PMH')

    def update(self, id):
        """PUT /OAI-PMH/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('OAI-PMH', id=ID),
        #           method='put')
        # url('OAI-PMH', id=ID)

    def delete(self, id):
        """DELETE /OAI-PMH/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('OAI-PMH', id=ID),
        #           method='delete')
        # url('OAI-PMH', id=ID)

    def show(self, id, format='html'):
        """GET /OAI-PMH/id: Show a specific item"""
        # url('OAI-PMH', id=ID)

    def edit(self, id, format='html'):
        """GET /OAI-PMH/id/edit: Form to edit an existing item"""
        # url('edit_OAI-PMH', id=ID)
