import pdb
import logging
import json
import couchdb
from lr.model.base_model import appConfig
import lr.lib.helpers as h
from pylons import request
from pylons.controllers.util import abort
from lr.lib.base import BaseController
from datetime import datetime, timedelta
from lr.lib.oaipmherrors import *
from lr.lib import resumption_token
log = logging.getLogger(__name__)
ANY_TAGS = "any_tags"
IDENTITY = "identity"
END_DATE = 'until'
START_DATE = 'from'
#FULL_DOCS = 'full_docs'
IDS_ONLY = 'ids_only'
CALLBACK = 'callback'
RESUMPTION_TOKEN = 'resumption_token'

SLICE_SERVICE_DOC = "access:slice"
SLICE_DOCUMENT = '_design/learningregistry-slicelite'


class SliceController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    # map.resource('slice', 'slices')
    def __before__(self):
        self.enable_flow_control = False
        self.fc_id_limit = None
        self.fc_doc_limit = None

        self.serviceDoc = h.getServiceDocument(appConfig['lr.slice.docid'])
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
        if END_DATE in req_params and not START_DATE in req_params:
            abort(500, 'if an end_date is specified a start_date must also be specified')
        if IDENTITY in req_params and ANY_TAGS in req_params:
            abort(500, "Only support for either any_tags or identity not both")

    def _parse_params(self, req_params):
        params = {}
        start, end = self._get_dates(req_params)
        if start is not None:
            params[START_DATE] = start
            params[END_DATE] = end
        if IDENTITY in req_params:
            params[IDENTITY] = req_params[IDENTITY].lower()
        if ANY_TAGS in req_params:
            params[ANY_TAGS] = req_params[ANY_TAGS].lower()
        if IDS_ONLY in req_params:
            params[IDS_ONLY] = req_params[IDS_ONLY] in ['T', 't', 'True', 'true', True]
        else:
            params[IDS_ONLY] = False
        if RESUMPTION_TOKEN in params and params[RESUMPTION_TOKEN] is not None:
            params[RESUMPTION_TOKEN] = resumption_token.parse_token(self.service_id, params[RESUMPTION_TOKEN])
            if len([i for i in ["offset", "search"] if i in params[RESUMPTION_TOKEN]]) != 2:
                msg = ": Unknown Error"
                if "error" in params[RESUMPTION_TOKEN]:
                    msg = ": %s" % params[RESUMPTION_TOKEN]["error"]
                raise BadArgumentError("Bad Resumption Token%s" % msg)
        return params

    def _get_view(self, view_name, params, include_docs=False, resumptionToken=None, limit=None):
        db_url = '/'.join([appConfig['couchdb.url'], appConfig['couchdb.db.resourcedata']])
        opts = {"stale": appConfig['couchdb.stale.flag'], "reduce": False}
        if include_docs:
            opts["include_docs"] = True
        if self.enable_flow_control and resumptionToken != None:
            if resumptionToken != None:
                opts["skip"] = resumptionToken["offset"]
                opts['startkey'] = resumptionToken['startkey']
                opts['endkey'] = resumptionToken['endkey']
        else:
            opts.update(self._get_couch_opts(params))
        if limit != None:
            opts["limit"] = limit
        if 'keys' not in opts:
            view = h.getView(database_url=db_url, method="POST", view_name=view_name, **opts)
            for doc in view:
                yield doc
        else:
            keys = opts["keys"]
            del opts['keys']
            for key in keys:
                opts.update(key)
                view = h.getView(database_url=db_url, method="POST", view_name=view_name, **opts)
                for doc in view:
                    yield doc

    def _get_couch_opts(self, params):
        opts = {}
        if START_DATE in params and IDENTITY in params:
            opts['startkey'] = [params[IDENTITY], params[START_DATE]]
            opts['endkey'] = [params[IDENTITY], params[END_DATE]]
        elif START_DATE in params and ANY_TAGS in params:
            if ',' in params[ANY_TAGS]:
                tags = params[ANY_TAGS].split(',')
                keys = []
                for t in tags:
                    keys.append({"startkey": [t, params[START_DATE]], "endkey": [t, params[END_DATE]]})
                opts["keys"] = keys
            else:
                opts['startkey'] = [params[ANY_TAGS], params[START_DATE]]
                opts['endkey'] = [params[ANY_TAGS], params[END_DATE]]
        if START_DATE in params:
            params['startkey'] = params[START_DATE]
            params['endkey'] = params[END_DATE]
        return opts

    def _get_index(self, params):
        if START_DATE in params and IDENTITY in params:
            return SLICE_DOCUMENT + "/_view/identity-by-date"
        elif START_DATE in params and ANY_TAGS in params:
            return SLICE_DOCUMENT + "/_view/any-tags-by-date"
        if START_DATE in params:
            return SLICE_DOCUMENT + "/_view/by-date"

    def _get_view_total(self, view_name, params, resumptionToken=None):
        if resumptionToken and "maxResults" in resumptionToken and resumptionToken["maxResults"] != None:
            return resumptionToken["maxResults"]
        db_url = '/'.join([appConfig['couchdb.url'], appConfig['couchdb.db.resourcedata']])
        opts = {"stale": appConfig['couchdb.stale.flag'], "groub": True}
        if self.enable_flow_control and resumptionToken != None:
            if resumptionToken != None:
                opts['startkey'] = resumptionToken['startkey']
                opts['endkey'] = resumptionToken['endkey']
        else:
            opts.update(self._get_couch_opts(params))
        totalDocs = 0
        if 'keys' not in opts:
            view = h.getView(database_url=db_url, method="POST", view_name=view_name, **opts)
            for row in view:
                if "value" in row:
                    totalDocs += row["value"]
        else:
            keys = opts["keys"]
            del opts['keys']
            for key in keys:
                opts.update(key)
                print(opts)
                view = h.getView(database_url=db_url, method="POST", view_name=view_name, **opts)
                for row in view:
                    if "value" in row:
                        totalDocs += row["value"]
        return totalDocs

    def _get_dates(self, params):
        cur = h.convertDateTime(params.get(START_DATE, h.EPOCH_STRING))
        end = h.convertDateTime(params.get(END_DATE, datetime.utcnow().isoformat() + "Z"))
        return (cur, end)

    def format_data(self, keys_only, docs, params, forceUnique, maxResults, current_rt=None):
        try:
            sentIDs = []
            prefix = '{"documents":[\n'
            num_sent = 0
            doc_count = 0
            startkey_docid = None
            update_resumption_max_results = current_rt and "maxResults" in current_rt and current_rt["maxResults"] != None
            if docs is not None:
                for row in docs:
                    doc_count += 1
                    alreadySent = (row["id"] in sentIDs)
                    if not alreadySent or not forceUnique:
                        sentIDs.append(row["id"])
                        startkey_docid = row["id"]
                        if keys_only:
                            return_data = {"doc_ID": row["id"]}
                        else:
                            # Get the resource data and update with the node timestamp data
                            # That the view has in value['timestamp']
                            resourceData = {}
                            resourceData = row["doc"]
                            return_data = {"doc_ID": row["id"], "resource_data_description": resourceData}
                        yield prefix + json.dumps(return_data)
                        num_sent += 1
                        prefix = ",\n"
                    else:
                        log.debug("{0} skipping: alreadySent {1} / forceUnique {2}".format(doc_count, repr(alreadySent), forceUnique))
                        if update_resumption_max_results:
                            current_rt["maxResults"] = current_rt["maxResults"] - 1

            if doc_count == 0:
                yield prefix

            rt = " "
            if self.enable_flow_control:
                pass
                if current_rt != None and "offset" in current_rt and current_rt["offset"] is not None:
                    offset = current_rt["offset"]
                else:
                    offset = 0
                if offset + doc_count < maxResults:
                    token = resumption_token.get_token(self.service_id, maxResults=maxResults,
                                                       startkey=params.get('startkey', None), endkey=params.get('endkey', None), keys=params.get('keys', None))
                    rt = ''' "resumption_token":"{0}", '''.format(token)
            db = couchdb.Server(appConfig['couchdb.url'])[appConfig['couchdb.db.resourcedata']]
            yield '\n],' + rt + '"resultCount":' + str(maxResults) + ',"viewUpToDate":' + h.isViewUpdated(db, SLICE_DOCUMENT) + '}'
        except Exception as ex:
            print(ex)

# if __name__ == '__main__':
# param = {START_DATE: "2011-03-10", END_DATE: "2011-05-01", IDENTITY: "NSDL 2 LR Data Pump", 'search_key': 'Arithmetic'}
# keys(param)

    def index(self, format='html'):
        """GET /slices: All items in the collection"""
        # url('slices')

        def getResponse(params):
            limit = None
            if self.enable_flow_control:
                if params[IDS_ONLY]:
                    limit = self.fc_id_limit
                else:
                    limit = self.fc_doc_limit
            if CALLBACK in params:
                yield "{0}(".format(params[CALLBACK])
            current_rt = params.get(RESUMPTION_TOKEN, None)
            docs = self._get_view(self._get_index(params), params, not params[IDS_ONLY], current_rt, limit)
            maxResults = self._get_view_total(self._get_index(params), params, resumptionToken=current_rt)
            for i in self.format_data(params[IDS_ONLY], docs, params, True, maxResults, params.get(RESUMPTION_TOKEN, None)):
                yield i
            if CALLBACK in params:
                yield ");"
        # try:
        req_params = self._get_params()
        self._validate_params(req_params)
        params = self._parse_params(req_params)
        return getResponse(params)
        # except BadArgumentError as bae:
        #     return '{ "error": "{0}" }'.format(bae.msg)
        # except Exception as e:
        #     log.error(e)
        #     return '{ "error": "Unknown Error, check log." }'
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
