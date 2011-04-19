#    Copyright 2011 SRI International
#    
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    
#        http://www.apache.org/licenses/LICENSE-2.0
#    
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from lrnodetemplate import *

import ConfigParser, os
import couchdb
import sys
import json
import logging

log = logging.getLogger(__name__)
   
_config = ConfigParser.ConfigParser()
_config.read('../LR/development.ini')

_SERVER_URL = _config.get("app:main", "couchdb.url")
_RESOURCE_DATA = _config.get("app:main", "couchdb.db.resourcedata")
_NODE = _config.get("app:main", "couchdb.db.node")
_COMMUNITY = _config.get("app:main", "couchdb.db.community")
_NETWORK = _config.get("app:main", "couchdb.db.network")

_couchServer = couchdb.Server(url=_SERVER_URL)
stats = _couchServer.stats()
s = json.dumps(stats, sort_keys=True, indent=4)
prettyStats = '\n'.join([l.rstrip() for l in s.splitlines()])
print("Server Exists, Here are some stats: {0}".format(prettyStats))
            
def CreateDB(couchServer =_couchServer,  dblist=[], deleteDB=False):
    '''Creates a DB in Couch based upon config'''
    for db in dblist:
        if deleteDB:
            try:
                del couchServer[db]
            except couchdb.http.ResourceNotFound as rnf:
                print("DB '{0}' doesn't exist on '{1}', creating".format(db, _SERVER_URL))
        try:
            couchServer.create(db)
            print("Created DB '{0}' on '{1}'\n".format(db, _SERVER_URL))
    
        except Exception as e:
            print("Exception while creating database: {0}\n".format(e) )


def PublishDoc(dbname, name, doc_data):
    
    try:
        db = _couchServer[dbname]
        del db[name]
    except couchdb.http.ResourceNotFound as ex:
        log.exception("Exception when deleting existing config document: {0}\n".format(ex))
    db[name] = doc_data
    print("Added config document '{0}' to '{1}".format(name, dbname))
    
    
def Prompt(name="", doc_data=None, nest=0):
    if doc_data == None:
        return
    
    print "###### Configure {0}".format(name)
   
    for key in doc_data.keys():
        if isinstance(doc_data.get(key), basestring):
            input = raw_input("{2}:Enter a value for '{0}' [{1}]".format(key, doc_data.get(key), name.upper()))
            # TODO: Should probably validate this more
            if (input != None and input.strip() != ''):
                doc_data[key] = input
        elif isinstance(doc_data.get(key), dict):
            Prompt(key, doc_data.get(key), nest+1)
                

if __name__ == "__main__":
    CreateDB(dblist=[_RESOURCE_DATA, _NODE, _COMMUNITY, _NETWORK])
    Prompt('Node Setup', default_node)
    PublishDoc(_NODE,'status',default_status)
    PublishDoc(_NODE,'policy',default_policy)
    PublishDoc(_NODE,'description',default_description)
    PublishDoc(_NODE,'services',default_services)
    PublishDoc(_NODE,'filter_description',default_filter_description)

