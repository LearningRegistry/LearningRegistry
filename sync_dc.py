#!/usr/bin/env python
import couchdb, sys
from oaipmh.client import Client
from oaipmh.common import Identify, Metadata, Header
from oaipmh.metadata import MetadataRegistry, oai_dc_reader , MetadataReader
from util import *                     
if __name__ == '__main__':
    main_url = 'http://wegrata:g15t15@10.10.1.56:5984/'    
    oai_url = 'http://localhost:8080/fedora/oai'
    database_name = 'test_oai'
    index_documents(oai_url,main_url,database_name,oai_dc_reader,'oai_dc')