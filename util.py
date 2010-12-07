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
def get_documents(url, reader, prefix):
    registry = MetadataRegistry()
    registry.registerReader(prefix, reader)
    client = Client(url, registry)
    return_stuff = []
    for record in client.listRecords(metadataPrefix=prefix):
        r = record[1]
        if not ''.join(r.getField('identifier')).startswith('fedora'):
          try:
            value = {'title':''.join(r.getField('title')),'identifier':''.join(r.getField('identifier')), 'location': ''.join(r.getField('location'))}
          except KeyError:
            value = {'title':''.join(r.getField('title')),'identifier':''.join(r.getField('identifier')), 'location': ''}
          return_stuff.append(value)
    return return_stuff

def save_file(db, id, data):
    print id
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

def index_documents(oai_url,main_url,database_name, reader, prefix):
   
    files_to_replicate = get_documents(oai_url, reader,prefix)
    db = get_database(main_url,database_name)
    if db == None:
        db = create_database(main_url,database_name)
    for file in files_to_replicate:
        save_file(db,file['identifier'],file)
