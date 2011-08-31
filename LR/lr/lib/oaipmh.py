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
from lr.lib.oaipmherrors import IdDoesNotExistError, NoMetadataFormats
import lr.lib.helpers as h
from lr.model.base_model import appConfig
import json
from lr.lib.stream import CouchDBDocProcessor
import urllib2
from contextlib import closing
from xml.sax import saxutils

log = logging.getLogger(__name__)

class OAIPMHDocumentResolver(CouchDBDocProcessor):
    def __init__(self):
        pass
    
    def _resolve(self, doc):
        if doc["active"] and doc["payload_placement"] == "linked":
            try:
                if "payload_locator" in doc:
                    payload = None
                    log.debug("Paylod Locator: %s" % doc["payload_locator"])
                    with closing(urllib2.urlopen(doc["payload_locator"], timeout=90)) as res:
                            payload = res.read()
                    if payload is not None:
                        doc["resource_data"] = saxutils.escape(payload)
            except:
                log.exception("Unable to resolved linked payload")
                
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
      
    
    def list_opts(self, metadataPrefix, from_date=None, until_date=None):
        opts = {}
        if from_date != None:
            opts["startkey"] = [metadataPrefix, from_date.isoformat()]
        else:
            # empty string should sort before anything else.
            opts["startkey"] = [metadataPrefix, None]
        
        if until_date != None:
            opts["endkey"] = [metadataPrefix, until_date.isoformat()]
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
        view_data = h.getView(database_url=self.db_url,view_name='_design/learningregistry-resource-location/_view/docs',method="POST", documentHandler=OAIPMHDocumentResolver(), include_docs=True,keys=[resource_locator], stale='ok')
        for doc in view_data:
            yield doc  
    
    def list_identifiers_or_records(self,metadataPrefix,from_date=None, until_date=None, rt=None, fc_limit=None, serviceid=None, include_docs=False):
        '''Returns the list_records as a generator based upon OAI-PMH query'''
        opts = { "stale": "ok" };
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
            opts = { "stale": "ok" }
            if identity != None:
                if by_doc_ID == True: 
                    byID = "by_doc_ID" 
                else: 
                    byID = "by_resource_ID"
                opts["key"] = [byID, identity]
                
                view_data = self.db.view('oai-pmh-get-records/docs', **opts)
                if len(view_data) == 0:
                    raise IdDoesNotExistError(verb)
                formats = [];
                for res in view_data:
                    for schema in res.value["payload_schema"]:
                        formats.append({"metadataPrefix":schema, "schemas":[res.value["payload_schema_locator"]]})
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
            ident["granularity"] = h.getDatetimePrecision()
            opts = {
                    "group": True,
                    "limit": 1,
                    "stale": "ok"
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