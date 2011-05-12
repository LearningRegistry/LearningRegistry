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

log = logging.getLogger(__name__)

class oaipmh(harvest):
    '''
    Utility class to provide OAI-PMH results from Learning Registy
    '''
    def __init__(self, server="http://localhost:5984", database="resource_data"):
        '''
        Constructor
        '''
        self.server = couchdb.Server(server)
        self.db = self.server[database]
    
    
    
    def list_records(self,metadataPrefix,from_date=None, until_date=None):
        opts = {};

        if from_date != None:
            from_date = from_date.replace(tzinfo=None)
            opts["startkey"] = [metadataPrefix, from_date.isoformat(' ')]
        else:
            # empty string should sort before anything else.
            opts["startkey"] = [metadataPrefix, ""]
        
        if until_date != None:
            until_date = until_date.replace(tzinfo=None)
            opts["endkey"] = [metadataPrefix, until_date.isoformat(' ')]
        else:
            # somewhat of an hack... since I don't know the timestamp, and couch stores things
            # in alphabetical order, a string sequence with all capital Z's should always sort last.
            opts["endkey"] = [metadataPrefix, "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"];
        
        
        view_data = self.db.view('oai-pmh/list-records', **opts)
        return map(lambda row: row["value"], view_data)
    
    def list_identifiers(self,metadataPrefix,from_date=None, until_date=None ):
        opts = {};

        if from_date != None:
            opts["startkey"] = [metadataPrefix, from_date.isoformat()]
        else:
            # empty string should sort before anything else.
            opts["startkey"] = [metadataPrefix, ""]
        
        if until_date != None:
            opts["endkey"] = [metadataPrefix, until_date.isoformat()]
        else:
            # somewhat of an hack... since I don't know the timestamp, and couch stores things
            # in alphabetical order, a string sequence with all capital Z's should always sort last.
            opts["endkey"] = [metadataPrefix, "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"];
        
        
        view_data = self.db.view('oai-pmh/list-identifiers', **opts)
        return map(lambda row: { "doc_ID": row["id"], "node_timestamp": row["key"][1] }, view_data)
    
    def list_metadata_formats(self, identity=None, by_doc_ID=False, verb="ListMetadataFormats"):
        try:
            opts = {}
            if identity != None:
                if by_doc_ID == True: 
                    byID = "by_doc_ID" 
                else: 
                    byID = "by_resource_ID"
                opts["key"] = [byID, identity]
                
                view_data = self.db.view('oai-pmh/get-records', **opts)
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
                view_data = self.db.view('oai-pmh/list-metadata-formats', **opts)
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
            ident["adminEmail"] = description["node_admin_url"]
            # TODO: This should map to the deleted_data_policy from the node_policy from the
            #       network node description
            ident["deletedRecord"] = "transient"
            ident["granularity"] = "YYYY-MM-DDThh:mm:ss.sZ"
            opts = {
                    "group": True,
                    "limit": 1
                    }
            
            view_data = self.db.view('oai-pmh/identify-timestamp', **opts)
            if len(view_data) > 0:
                ident["earliestDatestamp"] = iso8601.parse_date(list(view_data)[0].key)
            else:
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