import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.controllers.harvest import HarvestController

from lr.lib.base import BaseController, render
from lr.lib.oaipmh import oaipmh
from datetime import datetime
import json, iso8601
from couchdb.http import ResourceNotFound

log = logging.getLogger(__name__)

class Error(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        self.datetime_now = datetime.utcnow().isoformat()
        self.path_url = request.path_url

class ErrorWithVerb(Error):
    def __init__(self, code, msg, verb):
        Error.__init__(self, code, msg)
        self.verb = verb

class BadVerbError(Error):
    def __init__(self):
        Error.__init__(self, "badVerb", "Illegal OAI Verb")

class BadResumptionTokenError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "badResumptionToken", "Resumption tokens not supported.", verb)

class BadArgumentError(ErrorWithVerb):
    def __init__(self, msg, verb):
        ErrorWithVerb.__init__(self, "badArgument", msg, verb)

class CannotDisseminateFormatError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "cannotDisseminateFormat", "The metadata format identified by the value given for the metadataPrefix argument is not supported by the item or by the repository.", verb)

class IdDoesNotExistError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "idDoesNotExist", "The value of the identifier argument is unknown or illegal in this repository.", verb)

class NoRecordsMatchError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "noRecordsMatch", "The combination of the values of the from, until, and metadataPrefix arguments results in an empty list.", verb)

class NoSetHierarchyError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "noSetHierarchy", "The repository does not support sets.", verb)
        

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
        
        if verb == 'GetRecord' or verb == 'ListRecords' or verb == 'ListIdentifers':        
            if request.params.has_key('metadataPrefix') == False:
                raise BadArgumentError('metadataPrefix is a required parameter.', verb)
            params["metadataPrefix"] = metadataPrefix = request.params['metadataPrefix']
        
        if verb == 'GetRecord' or verb == 'ListMetadataFormats':
            if request.params.has_key('by_doc_ID') and request.params.has_key('by_resource_ID'):
                if _isTrue(request.params['by_doc_ID']) == _isTrue(request.params['by_resource_ID']):
                    raise BadArgumentError('by_doc_ID and by_resource_ID have conflicting values.', verb)
                
            if request.params.has_key('by_doc_ID'):
                params['by_doc_ID'] = _isTrue(request.params['by_doc_ID'])
                params['by_resource_ID'] = not params['by_doc_ID']
            else:
                params['by_doc_ID'] = False
                params['by_resource_ID'] = not params['by_doc_ID']
            
            if request.params.has_key('by_resource_ID'):
                params['by_resource_ID'] = _isTrue(request.param['by_doc_ID'])
                params['by_doc_ID'] = not params['by_resource_ID']
        
        if verb == 'ListRecords' or verb == 'ListIdentifiers':
            if request.params.has_key('from'):
                try:
                    params['from'] = iso8601.parse_date(request.params['from'])
                except:
                    raise BadArgumentError('from does not parse to ISO 8601.', verb)
            else:
                params['from'] = None
            
            if request.params.has_key('until'):
                try:
                    params['until'] = iso8601.parse_date(request.params['until'])
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
                                 

    def index(self, format='html'):
        """GET /OAI-PMH: All items in the collection"""
        o = oaipmh()
        
        def GetRecord(params):
            try:
                c.doc = o.get_record(params["identifier"])
                log.info(json.dumps(c.doc))
            except ResourceNotFound:
                raise IdDoesNotExistError(params['verb'])
            
            c.metadataPrefix = params["metadataPrefix"]
            if c.metadataPrefix not in c.doc["payload_schema"]:
                raise CannotDisseminateFormatError(params['verb'])
            
            c.datetime_now = datetime.utcnow().isoformat()
            c.path_url = request.path_url

            body = "<error/>"
            try:
                body = render("/oaipmh-GetRecord.mako")
            except:
                log.exception("Unable to render template")
            return self._returnResponse(body)
        
        def ListSets(params=None):
            c.doc = NoSetHierarchyError(verb)
            
        def NotYetSupported(params=None):
            c.doc = BadVerbError()
            
        switch = {
                  'GetRecord': GetRecord,
                  'ListRecords': NotYetSupported,
                  'ListIdentifers': NotYetSupported,
                  'Identify': NotYetSupported,
                  'ListMetadataFormats': NotYetSupported,
                  'ListSets': ListSets
                  }
        try:
            params = self._parseParams()
        except Error as e:
            c.error = e
            return self._returnResponse(render('oaipmh-Error.mako'))
        
        verb = params['verb']
        
        try:
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
