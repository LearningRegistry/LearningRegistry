#!/usr/bin/env python
import couchdb, sys
from oaipmh.client import Client
from oaipmh.common import Identify, Metadata, Header
from oaipmh.metadata import MetadataRegistry, oai_dc_reader , MetadataReader

def get_database(url,name):
    try:
        couch = couchdb.Server(url)
        db = couch[name]
        return db;
    except:
        return None
    

def create_database(url,name):
    db = get_database(url,name)
    if db == None:
        couch = couchdb.Server(url)
        db = couch.create(name)
    return db

def index_documents(main_url, database_name, url, reader, prefix, format):
    registry = MetadataRegistry()
    registry.registerReader(prefix, reader)
    client = Client(url, registry)
    return_stuff = []
    for record in client.listRecords(metadataPrefix=prefix):
        r = record[1]
        value = format(r,record[0].identifier())
        if value != None:
            return_stuff.append(value)
        if len(return_stuff) >= 10000:
            sync_files(main_url, database_name, return_stuff)     
            return_stuff = []
    sync_files(main_url, database_name, return_stuff)                 

def save_file(db, id, data):
    try:    
        doc = db[id]
    except:
        doc = None
    if doc == None:
        db[id] = data
    else:        
        doc['identifier'] = data['identifier']        
        doc['title']= data['title']
        db[id] = doc

def sync_files(main_url, database_name, files_to_replicate):
    db = get_database(main_url,database_name)
    if db == None:
        db = create_database(main_url,database_name)
    db.update(files_to_replicate)    


