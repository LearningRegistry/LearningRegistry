#!/usr/bin/env python
import couchdb, sys
from util import *

def replacate_across_servers(main_url, replication_servers, database_name):
    couch = couchdb.Server(main_url)
    for replication in replication_servers:
        create_database(replication['url'],replication['db_name'])
        couch.replicate(database_name,replication['url']+ replication['db_name'])

if __name__ == '__main__':
    main_url = 'http://10.50.10.114:5984/'    
    replication_servers =  []
    db = get_database(main_url,'knownservers')
    for i in db:        
        replication_servers.append(db[i])
    database_name = 'test_oai'
    replacate_across_servers(main_url,replication_servers, database_name)