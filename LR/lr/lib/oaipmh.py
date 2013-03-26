'''
Copyright 2011 SRI International

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on Mar 10, 2011

@author: jklo
'''
import logging, iso8601
import couchdb
from lr.lib.base import render
from lr.lib.harvest import harvest
from lr.lib.oaipmherrors import IdDoesNotExistError, NoMetadataFormats,\
    CannotDisseminateFormatError
import lr.lib.helpers as h
from lr.model.base_model import appConfig
import json
from lr.lib.stream import CouchDBDocProcessor
import urllib2
from contextlib import closing
from xml.sax import saxutils
from StringIO import StringIO
import sys
import re
from lr.lib import helpers
try:
    from lxml import etree
except:
    from xml.etree import ElementTree as etree

log = logging.getLogger(__name__)


def getMetadataPrefix(metadataFormat):
    return re.sub('''[^A-Za-z0-9\-_\.!~\*'\(\)]''', "_", metadataFormat)

class OAIPMHDocumentResolver(CouchDBDocProcessor):
    PAYLOAD_ERROR = "X_OAI-PMH-ERROR"
    ERR_CANNOT_DISSEMINATE_FORMAT = "Cannot Disseminate Format"

    def __init__(self):
        pass

    def _resolve(self, doc):

        ## TODO: add caching
        def get_payload(url):
            payload = None
            log.debug("Payload Locator: %s" % url)
            with closing(urllib2.urlopen(url, timeout=90)) as res:
                    payload = res.read()
            return payload

        if doc["active"]:
            if doc["payload_placement"] == "linked":
                try:
                    if "payload_locator" in doc:
                        payload = get_payload(doc["payload_locator"])
                        if payload is not None:
                            doc["resource_data"] = payload
                except:
                    log.exception("Unable to resolved linked payload")

            try:
                doc["resource_data"] = re.sub('''^<\?xml\s+version\s*=\s*(["][^"]+["]|['][^']+['])[^?]*\?>''', "", doc["resource_data"])
#                doc["resource_data"] = re.sub('''\s*<!DOCTYPE\s[^>]*>''', "", doc["resource_data"], flags=re.MULTILINE)
                expr = re.compile('''\s*<!DOCTYPE\s[^>]*>''', flags=re.MULTILINE)
                doc["resource_data"] = expr.sub("", doc["resource_data"])
                payload = etree.parse(StringIO(doc["resource_data"]))
                doc["resource_data"] = etree.tostring(payload)
            except:
                exc = sys.exc_info()
                log.debug("XML Parse Error: %s" % exc[1])
                doc[OAIPMHDocumentResolver.PAYLOAD_ERROR] = OAIPMHDocumentResolver.ERR_CANNOT_DISSEMINATE_FORMAT


    def process(self, row):
        doc = row["doc"]

        self._resolve(doc)

        return doc

class oaipmh(harvest):
    '''
    Utility class to provide OAI-PMH results from Learning Registy
    '''
    def __init__(self, server=appConfig['couchdb.url'], database="resource_data"):
        '''
        Constructor
        '''
        harvest.__init__(self, server, database)
        self.server = couchdb.Server(server)
        self.db = self.server[database]
        self.res_data_url = '/'.join([
            appConfig['couchdb.url'],
            appConfig['couchdb.db.resourcedata']
        ])

        self.service_doc = helpers.getServiceDocument(appConfig["lr.oaipmh.docid"])


    def list_opts(self, metadataPrefix, from_date=None, until_date=None):
        from datetime import datetime
        opts = {}
        if from_date != None:
            from_date_no_ms = datetime(from_date.year, from_date.month, from_date.day, from_date.hour, from_date.minute, from_date.second, 0, from_date.tzinfo)
            opts["startkey"] = [metadataPrefix, from_date_no_ms.isoformat()]
        else:
            # empty string should sort before anything else.
            opts["startkey"] = [metadataPrefix, None]

        if until_date != None:
            until_date_no_ms = datetime(until_date.year, until_date.month, until_date.day, until_date.hour, until_date.minute, until_date.second, 0, until_date.tzinfo)
            opts["endkey"] = [metadataPrefix, until_date_no_ms.isoformat()]
        else:
            # {} sorts at end of string sequence.
            opts["endkey"] = [metadataPrefix, {}]
        return opts;

#    def list_records(self,metadataPrefix,from_date=None, until_date=None, rt=None, fc_limit=None, serviceid=None):
#        '''Returns the list_records as a generator based upon OAI-PMH query'''
#        opts = {
#                "include_docs": True,
#                "stale": "ok"
#                };
#
#        if rt != None and fc_limit != None:
#            opts["startkey"] = rt["startkey"]
#            opts["startkey_docid"] = rt["startkey_docid"]
#            opts["endkey"] = rt["endkey"]
#            opts["limit"] = fc_limit + 1
#
#        else:
#            opts.update(self.list_opts(metadataPrefix, from_date, until_date))
#
#        def format(row):
#            obj = row["doc"]
#            return obj
#
#        return h.getView(self.res_data_url, '_design/oai-pmh/_view/list-identifiers', method="GET", documentHandler=format, **opts)
#        view_data = self.db.view('oai-pmh/list-records', **opts)
#        return map(lambda row: row["value"], view_data)

    def get_records_by_resource(self,resource_locator):
        view_data = h.getView(database_url=self.db_url,view_name='_design/learningregistry-resource-location/_view/docs',method="POST", documentHandler=OAIPMHDocumentResolver(), include_docs=True,keys=[resource_locator], stale=appConfig['couchdb.stale.flag'])
        for doc in view_data:
            yield doc

    def list_identifiers_or_records(self,metadataPrefix,from_date=None, until_date=None, rt=None, fc_limit=None, serviceid=None, include_docs=False):
        '''Returns the list_records as a generator based upon OAI-PMH query'''
        opts = { "stale": appConfig['couchdb.stale.flag'] };
        if include_docs:
            opts["include_docs"] = True

        import logging
        log = logging.getLogger(__name__)

        if rt != None and fc_limit != None:
            opts["startkey"] = rt["startkey"]
            opts["startkey_docid"] = rt["startkey_docid"]
            opts["endkey"] = rt["endkey"]
            opts["limit"] = fc_limit + 1

        else:
            opts.update(self.list_opts(metadataPrefix, from_date, until_date))

        log.info("opts: "+ repr(opts))

        def format_ids(row):
            obj = { "doc_ID": row["id"], "node_timestamp": "%sZ" %(row["key"][1]) }
            log.debug("format: %s\n" %(json.dumps(obj)))
            return obj

        def format_docs(row):
            obj = row["doc"]
            return obj

        if include_docs:
            format = OAIPMHDocumentResolver()
        else:
            format = format_ids

        return h.getView(self.res_data_url, '_design/oai-pmh-list-identifiers/_view/docs', method="GET", documentHandler=format, **opts)
#        view_data = self.db.view('oai-pmh/list-identifiers', **opts)
#        return map(lambda row: { "doc_ID": row["id"], "node_timestamp": row["key"][1] }, view_data)

    def list_metadata_formats(self, identity=None, by_doc_ID=False, verb="ListMetadataFormats"):
        try:
            opts = { "stale": appConfig['couchdb.stale.flag'] }
            if identity != None:
                opts["include_docs"] = "true"

                if by_doc_ID == True:
                    byID = "by_doc_ID"
                else:
                    byID = "by_resource_locator"
                opts["key"] = [byID, identity]

                view_data = self.db.view('oai-pmh-get-records/docs', **opts)
                if len(view_data) == 0:
                    raise IdDoesNotExistError(verb)
                formats = []
                for res in view_data:
                    for schema in res.doc["payload_schema"]:
                        schemaLocators = []
                        if "payload_schema_locator" in res.doc:
                            schemaLocators.append(res.doc["payload_schema_locator"])
                        if {"metadataPrefix":schema, "schemas":schemaLocators} not in formats:
                            formats.append({"metadataPrefix":schema, "schemas":schemaLocators})
                return formats

            else:
                opts["group"] = True
                opts["group_level"] = 1
                view_data = self.db.view('oai-pmh-list-metadata-formats/docs', **opts)
                return map(lambda doc: {"metadataPrefix": doc.key[0], "schemas": doc.value}, view_data)

        except Exception as e:
            raise e

    def identify(self, database="node"):
        ret = None
        ident = {}
        try:
            db2 = self.server[database]
            description = db2["node_description"]

            ident["repositoryName"] = description["node_description"]
            ident["adminEmail"] = description["node_admin_identity"]
            # TODO: This should map to the deleted_data_policy from the node_policy from the
            #       network node description
            ident["deletedRecord"] = "transient"
            ident["granularity"] = h.getDatetimePrecision(self.service_doc)
            opts = {
                    "group": True,
                    "limit": 1,
                    "stale": appConfig['couchdb.stale.flag']
                    }

            view_data = self.db.view('oai-pmh-identify-timestamp/docs', **opts)
            if len(view_data) > 0:
                ident["earliestDatestamp"] = iso8601.parse_date(list(view_data)[0].key)
            else:
                from datetime import datetime
                ident["earliestDatestamp"] = datetime.utcnow()

            ret = ident
        except Exception as e:
            log.exception("Problem determining OAI Identity")

        return ret
#    def list_metadata_formats(self,identifier=None, by_doc_ID=False, by_resource_ID=True):
#        opts = {}




if __name__ == "__main__":
    from datetime import datetime
    import iso8601
    o = oaipmh()
    start = iso8601.parse_date("2011-03-14 13:37:15.096670")
    start = start.replace(tzinfo=None)
    end = iso8601.parse_date("2011-03-14 13:37:15.360254")
    end = end.replace(tzinfo=None)
    records = o.list_records("nsdl_dc", from_date=start, until_date=end)
    len(records)

    records = o.list_identifiers("nsdl_dc", from_date=start, until_date=end)
    len(records)

    pass