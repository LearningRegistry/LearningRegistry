import logging, re
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.controllers.harvest import HarvestController
from lr.model import appConfig
from lr.lib import helpers as h, oaipmherrors
from lr.lib.base import BaseController, render
from lr.lib.oaipmh import oaipmh, OAIPMHDocumentResolver
from datetime import datetime
import json, iso8601
from couchdb.http import ResourceNotFound
from lr.lib.oaipmherrors import *
import types


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
    
    def _parseParams(self, flow_control=False, serviceid=None):
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
                if self._isTrue(req_params['by_doc_ID']) == self._isTrue(req_params['by_resource_ID']):
                    raise BadArgumentError('by_doc_ID and by_resource_ID have conflicting values.', verb)
                
            if req_params.has_key('by_doc_ID'):
                params['by_doc_ID'] = self._isTrue(req_params['by_doc_ID'])
                params['by_resource_ID'] = not params['by_doc_ID']
            else:
                params['by_doc_ID'] = False
                params['by_resource_ID'] = not params['by_doc_ID']
            
            if req_params.has_key('by_resource_ID'):
                params['by_resource_ID'] = self._isTrue(req_params['by_resource_ID'])
                params['by_doc_ID'] = not params['by_resource_ID']
        
        if verb == 'ListRecords' or verb == 'ListIdentifiers':
            if flow_control and req_params.has_key('resumptionToken'):
                from lr.lib import resumption_token
                token = req_params['resumptionToken']
                log.debug("resumptionToken: %s" % token)
                try:
                    parsed = resumption_token.parse_token(serviceid, token)
                    if 'error' in parsed:
                        raise BadResumptionTokenError(verb, msg=params['resumptionToken']['error'])  
                    params['resumptionToken'] = parsed
                    
                    if "from_date" in parsed:
                        req_params["from"] = parsed["from_date"]
                    if "until_date" in parsed:
                        req_params["until"] = parsed["until_date"]
                except Exception as e:
                    raise BadResumptionTokenError(verb, msg=e.message)
                
            
            from_date_gran = None
            until_date_gran = None
            if req_params.has_key('from') :
                try:
                    log.error("From 0: {0}".format(req_params['from']))
                    from_date = iso8601.parse_date(req_params['from'])
                    log.error("From 1: {0}".format(from_date))
                    params['from'] = h.convertToISO8601UTC(from_date)
                    log.error("From 2: {0}".format(params['from']))
                    from_date_gran = h.getISO8601Granularity(req_params['from'])
                except:
                    log.error("from: uhh ohh!")
                    raise BadArgumentError('from does not parse to ISO 8601.', verb)
            else:
                params['from'] = None
            
            if req_params.has_key('until'):
                try:
                    log.error("Until 0: {0}".format(req_params['until']))
                    until_date = iso8601.parse_date(req_params['until'])
                    log.error("Until 1: {0}".format(until_date))
                    params['until'] = h.convertToISO8601UTC(until_date)
                    log.error("Until 2: {0}".format(params['until']))
                    until_date_gran = h.getISO8601Granularity(req_params['until'])
                except:
                    raise BadArgumentError('until does not parse to ISO 8601.', verb)
            else:
                params['until'] = None
                
            if params['from'] != None and params['until'] != None:
                if params['from'] > params['until']:
                    raise BadArgumentError('until cannot preceed from.', verb)
                if from_date_gran != until_date_gran:
                    raise BadArgumentError('from and until parameters do not use the same granularity.', verb)
            
            harvestServiceGranularity = h.getOAIPMHServiceGranularity()
            
            if params['from'] != None and from_date_gran > harvestServiceGranularity:
                raise BadArgumentError('from is more granular than Harvest service permits', verb)
        
            if params['until'] != None and until_date_gran > harvestServiceGranularity:
                raise BadArgumentError('until is more granular than Harvest service permits', verb)
            
            if (from_date_gran != None and from_date_gran.granule != "day" and from_date_gran.granule != "second") or \
                (until_date_gran != None and until_date_gran.granule != "day" and until_date_gran.granule != "second"):
                formatSupport = "YYYY-MM-DD"
                if harvestServiceGranularity.granule == "second":
                    formatSupport = "YYYY-MM-DD and YYYY-MM-DDThh:mm:ssZ"
                raise BadArgumentError('from and until support {0} formats' % (formatSupport, ), verb)
            
        
        if verb in ['ListMetadataFormats', 'GetRecord']  and req_params.has_key('identifier'):
            params['identifier'] = req_params['identifier']
        elif verb == 'ListMetadataFormats':
            params['identifier'] = None
            params['by_doc_ID'] = None
            params['by_resource_ID'] = None
        
        if verb == 'GetRecord' and req_params.has_key('identifier') == False:
            raise BadArgumentError('identifier is a required parameter.', verb)
        
        return params

    def _setResponseHeaders(self):
        response.headers["Content-Type"] = "text/xml; charset=utf-8"
    
    def _returnResponse(self, body, res=None):
        if res != None:
            response = res
        response.headers["Content-Type"] = "text/xml; charset=utf-8"
        return body
            
                                 
    
    def _initRender(self, params, ctx=None, req=None):
        if ctx != None:
            c = ctx
            
        if req != None:
            request = req
            
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
            
    def _initMustache(self, args=None, req=None):
        from lr.lib import helpers as h
        
        vars = {}

        if req == None:
            req = request
            
        if args != None:
            params = args
            
        vars["response_date"] = datetime.utcnow().isoformat()
        vars["path_url"] = req.path_url
        if params.has_key("by_doc_ID"):
            vars["by_doc_ID"] = params["by_doc_ID"]
        if params.has_key("by_resource_ID"):
            vars["by_resource_ID"] = params["by_resource_ID"]
        if params.has_key("metadataPrefix"):
            vars["metadataPrefix"] = params["metadataPrefix"]
        if params.has_key("from"):
            vars["from_date"] = h.OAIPMHTimeFormat(params["from"])
        if params.has_key("until"):
            vars["until_date"] = h.OAIPMHTimeFormat(params["until"])
        if params.has_key("identifier"):
            vars["identifier"] = params["identifier"]
        return vars
        
    def _handleOAIRequest(self, format='html'):
        t_req = request._current_obj()
        t_res = response._current_obj()
        
        enable_flow_control = False
        fc_id_limit = None
        fc_doc_limit = None
        service_id = None
        serviceDoc = h.getServiceDocument(appConfig['lr.oaipmh.docid'])
        if serviceDoc != None:
            if 'service_id' in serviceDoc:
                service_id = serviceDoc['service_id']
                
            if 'service_data' in serviceDoc:
                serviceData = serviceDoc['service_data']
                if 'flow_control' in serviceData:
                    enable_flow_control = serviceData['flow_control']
                
                if enable_flow_control and 'id_limit' in serviceData:
                    fc_id_limit = serviceData['id_limit']
                elif enable_flow_control:
                    fc_id_limit = 100
                
                if enable_flow_control and 'doc_limit' in serviceData:
                    fc_doc_limit = serviceData['doc_limit']
                elif enable_flow_control:
                    fc_doc_limit = 100
        
        o = oaipmh()
        
        def GetRecord(params):
            try:
                from lr.mustache.oaipmh import GetRecord as must_GetRecord
                identifier = params["identifier"]
                if params["by_doc_ID"] == True:
                    resolver = OAIPMHDocumentResolver()
                    single_doc = o.get_record(params["identifier"])
                    if single_doc is not None: 
                        docList = [resolver.process({ "doc": single_doc })]
                    else:
                        docList = []
                else:
                    docList = o.get_records_by_resource(params["identifier"])

                doc_idx = 0
                valid_docs = 0
                mustache = must_GetRecord()
                for doc in docList:
                    if doc is not None:
                        doc_idx += 1
                        
                        if "payload_schema" in doc and params["metadataPrefix"] in doc["payload_schema"] and OAIPMHDocumentResolver.PAYLOAD_ERROR not in doc:
                            valid_docs += 1
                        
                            if valid_docs == 1:
                                part = mustache.prefix(**self._initMustache(args=params, req=t_req))
                                yield h.fixUtf8(self._returnResponse(part, res=t_res))
                                
                            part = mustache.doc(doc)
                            yield h.fixUtf8(self._returnResponse(part, res=t_res))
                        
                if doc_idx == 0:
                    raise IdDoesNotExistError(params['verb'], req=t_req)
                elif valid_docs == 0:
                    raise CannotDisseminateFormatError(params['verb'], req=t_req)
                else:
                    yield h.fixUtf8(self._returnResponse(mustache.suffix(), res=t_res))
                
            except oaipmherrors.Error as e:
                from lr.mustache.oaipmh import Error as err_stache
                err = err_stache()
                yield h.fixUtf8(self._returnResponse(err.xml(e), res=t_res))

        def ListGeneric(params, showDocs=False, record_limit=None):
            if not showDocs:
                from lr.mustache.oaipmh import ListIdentifiers as must_ListID
                mustache = must_ListID()
            else:
                from lr.mustache.oaipmh import ListRecords as must_ListRec
                mustache = must_ListRec()
                
            try:
                
                doc_index = 0
                err_count = 0
                metadataPrefix=params["metadataPrefix"]
                from_date=params["from"]
                until_date=params["until"]
                doc_err = None
                rendered_init = False
                resumptionToken = None if "resumptionToken" not in params else params['resumptionToken']
                records = o.list_identifiers_or_records(metadataPrefix,
                                                from_date=from_date, 
                                                until_date=until_date, 
                                                rt=resumptionToken, 
                                                fc_limit=record_limit, 
                                                include_docs=showDocs )
                for ident in records:
                    doc_index += 1
                    doc_err = False
                    
                    if OAIPMHDocumentResolver.PAYLOAD_ERROR in ident:
                        err_count += 1
                        doc_err = True
                        log.debug("Payload Error detected, doc_index: {0}, err_count: {1}".format(doc_index, err_count))
                    
                    if doc_index - err_count == 1:
                        rendered_init = True
                        part = mustache.prefix(**self._initMustache(args=params, req=t_req))
                        yield h.fixUtf8(self._returnResponse(part, res=t_res))

                    if doc_err is False and (record_limit is None or doc_index <= record_limit):
                        part = mustache.doc(ident)
                        yield h.fixUtf8(part)
                    elif enable_flow_control:
                        from lr.lib import resumption_token
                        if doc_index - err_count > 0 and doc_index > record_limit:
                            opts = o.list_opts(metadataPrefix, h.convertToISO8601UTC(ident["node_timestamp"]), until_date)
                            opts["startkey_docid"] = ident["doc_ID"]
                            token = resumption_token.get_token(serviceid=service_id, from_date=from_date, until_date=until_date, **opts)
                            part = mustache.resumptionToken(token)
                            yield h.fixUtf8(part)
                            break
                        elif doc_index - err_count == 0 and doc_index > record_limit:
                            opts = o.list_opts(metadataPrefix, h.convertToISO8601UTC(ident["node_timestamp"]), until_date)
                            opts["startkey_docid"] = ident["doc_ID"]
                            payload = resumption_token.get_payload(from_date=from_date, until_date=until_date, **opts)
                            records = o.list_identifiers_or_records(metadataPrefix,
                                                from_date=from_date, 
                                                until_date=until_date, 
                                                rt=payload, 
                                                fc_limit=record_limit, 
                                                include_docs=showDocs )
                            doc_index = 0
                            err_count = 0
                
                if doc_index == 0 and err_count == 0:
                    raise NoRecordsMatchError(params['verb'], req=t_req)
                elif (doc_index - err_count) == 0:
                    raise CannotDisseminateFormatError(params['verb'], req=t_req)
                else:
                    if enable_flow_control and doc_index <= record_limit:
                        yield h.fixUtf8(mustache.resumptionToken())
                    yield h.fixUtf8(mustache.suffix())
                    
            except oaipmherrors.Error as e:
                if not rendered_init:
                    from lr.mustache.oaipmh import Error as err_stache
                    err = err_stache()
                    yield h.fixUtf8(self._returnResponse(err.xml(e), res=t_res))
                else:
                    from lr.mustache.oaipmh import ErrorOnly as err_stache
                    err = err_stache()
                    yield h.fixUtf8(self._returnResponse(err.xml(e)+mustache.suffix(), res=t_res))
            except:
                log.exception("Unknown Error Occurred")

        def ListIdentifiers(params):
            return ListGeneric(params, False, fc_id_limit)
        
        def ListRecords(params):
            return ListGeneric(params, True, fc_doc_limit)
#        def ListRecords(params):
#            try:
#                from lr.mustache.oaipmh import ListRecords as must_ListRec
#                
#                doc_index = 0
#                mustache = must_ListRec()
#                for record in o.list_records(params["metadataPrefix"],from_date=params["from"], until_date=params["until"] ):
#                    doc_index += 1
#                    log.debug(json.dumps(record))
#                    if doc_index == 1:
#                        part = mustache.prefix(**self._initMustache(args=params, req=t_req))
#                        yield self._returnResponse(part, res=t_res)
#                    
#                    part = mustache.doc(record)
#                    yield self._returnResponse(part, res=t_res)
#                    
#                
#                if doc_index == 0:
#                    raise NoRecordsMatchError(params['verb'], req=t_req)
#                else:
#                    yield mustache.suffix()
#                
#            except oaipmherrors.Error as e:
#                from lr.mustache.oaipmh import Error as err_stache
#                err = err_stache()
#                yield self._returnResponse(err.xml(e), res=t_res)
#            except:
#                log.exception("Unable to render template")
        
        def Identify(params=None):
            body = ""
            try:
                self._initRender(params, ctx=c, req=t_req)
                c.identify = o.identify()
                body = render("/oaipmh-Identify.mako")
            except Exception as e:
                raise BadVerbError()
            return self._returnResponse(body, res=t_res)
        
        def ListMetadataFormats(params):
            body = ""
            try:
                self._initRender(params, ctx=c, req=t_req)
                
                fmts = o.list_metadata_formats(identity=params["identifier"], by_doc_ID=params["by_doc_ID"])
                if len(fmts) == 0:
                    raise NoMetadataFormats(params["verb"])
                c.formats = fmts
                body = render("/oaipmh-ListMetadataFormats.mako")
                return self._returnResponse(body, res=t_res)
            except Error as e:
                raise e
        
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
            params = self._parseParams(flow_control=enable_flow_control, serviceid=service_id)
            
            # If this is a special case where we are actually using OAI interface to serve basic harvest
            if params.has_key("metadataPrefix") and params["metadataPrefix"] == "LR_JSON_0.10.0":
                if params.has_key("identifier") == True:
                    params["request_id"] = params["identifier"]
                if params.has_key("from") and isinstance(params["from"], datetime):
                    params["from"] = h.convertToISO8601Zformat(params["from"])
                if params.has_key("until") and isinstance(params["until"], datetime):
                    params["until"] = h.convertToISO8601Zformat(params["until"])
                
                return HarvestController.harvest(self, params, request.body, params['verb'].lower())
        
            verb = params['verb']
            
            return switch[verb](params)
        except Error as e:
            from lr.mustache.oaipmh import Error as err_stache
            err = err_stache()
            return self._returnResponse(err.xml(e), res=t_res)

        
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

