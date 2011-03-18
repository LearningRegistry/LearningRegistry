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

class OaiPmhController(HarvestController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('OAI-PMH', 'OAI-PMH')
    def _isTrue(self, value):
        return str(value).lower() in ['true', 't', '1', 'y', 'yes']
    
    def _getParams(self):
        req_params = {}
        
        if request.method == "POST":
            req_params = dict(request.params.copy(), **self._parameterizePOSTBody())
        else:
            req_params = request.params.copy()
        return req_params
    
    def _parameterizePOSTBody(self):
        from urlparse import parse_qs
        req_params = {}
        try:
            params = parse_qs(qs=request.body)
            for key in params.keys():
                req_params[key] = params[key][0]
        except:
            log.exception("Unable to parse POST.")
        return req_params
    
    def _parseParams(self):
        params = {}
        req_params = self._getParams()
        if (req_params.has_key('verb') == False) :
            raise BadVerbError()
        
        verb = params["verb"] = req_params['verb']
        
        if verb not in ["GetRecord", "ListRecords", "ListIdentifiers", "Identify", "ListMetadataFormats", "ListSets"]:
            raise BadVerbError()
        
        if verb == 'GetRecord' or verb == 'ListRecords' or verb == 'ListIdentifiers':        
            if req_params.has_key('metadataPrefix') == False:
                raise BadArgumentError('metadataPrefix is a required parameter.', verb)
            params["metadataPrefix"] = metadataPrefix = req_params['metadataPrefix']
        
        if verb == 'GetRecord' or verb == 'ListMetadataFormats':
            if req_params.has_key('by_doc_ID') and req_params.has_key('by_resource_ID'):
                if self._isTrue(request.params['by_doc_ID']) == self._isTrue(req_params['by_resource_ID']):
                    raise BadArgumentError('by_doc_ID and by_resource_ID have conflicting values.', verb)
                
            if req_params.has_key('by_doc_ID'):
                params['by_doc_ID'] = self._isTrue(req_params['by_doc_ID'])
                params['by_resource_ID'] = not params['by_doc_ID']
            else:
                params['by_doc_ID'] = False
                params['by_resource_ID'] = not params['by_doc_ID']
            
            if request.params.has_key('by_resource_ID'):
                params['by_resource_ID'] = self._isTrue(request.param['by_doc_ID'])
                params['by_doc_ID'] = not params['by_resource_ID']
        
        if verb == 'ListRecords' or verb == 'ListIdentifiers':
            if req_params.has_key('from'):
                try:
                    from_date = iso8601.parse_date(request.params['from'])
                    params['from'] = h.convertToISO8601UTC(from_date)
                except:
                    raise BadArgumentError('from does not parse to ISO 8601.', verb)
            else:
                params['from'] = None
            
            if req_params.has_key('until'):
                try:
                    until_date = iso8601.parse_date(req_params['until'])
                    params['until'] = h.convertToISO8601UTC(until_date)
                except:
                    raise BadArgumentError('until does not parse to ISO 8601.', verb)
            else:
                params['until'] = None
                
            if params['from'] != None and params['until'] != None and params['from'] > params['until']:
                raise BadArgumentError('until cannot preceed from.', verb)
        
        if verb in ['ListMetadataFormats', 'GetRecord']  and req_params.has_key('identifier'):
            params['identifier'] = req_params['identifier']
        elif verb == 'ListMetadataFormats':
            params['identifier'] = None
            params['by_doc_ID'] = None
            params['by_resource_ID'] = None
        
        if verb == 'GetRecord' and req_params.has_key('identifier') == False:
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
        if params.has_key("identifier"):
            c.identifier = params["identifier"]
        
    def _handleOAIRequest(self, format='html'):
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
        
        def ListMetadataFormats(params):
            body = ""
            try:
                self._initRender(params)
                
                fmts = o.list_metadata_formats(identity=params["identifier"], by_doc_ID=params["by_doc_ID"])
                if len(fmts) == 0:
                    raise NoMetadataFormats(params["verb"])
                c.formats = fmts
                body = render("/oaipmh-ListMetadataFormats.mako")
                return self._returnResponse(body)
            except Error as e:
                raise e
#            except Exception as e:
#                raise NoMetadataFormats(params["verb"])
                
        
        def ListSets(params=None):
            raise NoSetHierarchyError(verb)
            
        def NotYetSupported(params=None):
            raise BadVerbError()
        
            
        switch = {
                  'GetRecord': GetRecord,
                  'ListRecords': ListRecords,
                  'ListIdentifiers': ListIdentifiers,
                  'Identify': Identify,
                  'ListMetadataFormats': ListMetadataFormats,
                  'ListSets': ListSets
                  }
        try:
            params = self._parseParams()
            
            # If this is a special case where we are actually using OAI interface to serve basic harvest
            if params.has_key("metadataPrefix") and params["metadataPrefix"] == "LR_JSON_0.10.0":
                if params.has_key("identifier") == True:
                    params["request_id"] = params["identifier"]
                
                return HarvestController.harvest(self, params, request.body, params['verb'].lower())
        
            verb = params['verb']
            
            return switch[verb](params)
        except Error as e:
            c.error = e
            return self._returnResponse(render('oaipmh-Error.mako'))

        
    def index(self, format='xml'):
        """GET /OAI-PMH: All items in the collection"""
        return self._handleOAIRequest(format)
        # url('OAI-PMH')

    def create(self):
        """POST /OAI-PMH: Create a new item"""
        return self._handleOAIRequest()
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

