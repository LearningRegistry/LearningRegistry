#!/usr/bin/env python
# update
import couchdb, sys
from oaipmh.client import Client
from oaipmh.common import Identify, Metadata, Header
from oaipmh.metadata import MetadataRegistry, oai_dc_reader , MetadataReader
from util import *
def format(doc, identifier):
    value = {
               'doc_type': 'resource_data',
               'doc_version':'0.10.0',
               'resource_data_type':'',
               'frbr_level':'work',
               'submitter_type':'anonymous',
               'submitter':'',
               'submitter_timestamp':'',
               'submitter_TTL':'',
               'publishing_node':'',
               'update_timestamp',
               'node_timestamp':'',
               'create_timestamp':'',
               'submission_TOS':'',
               'filtering_keys':[''.join(doc.getField('title'))],
               'resource_locator': ''.join(doc.getField('location')),
               'resource_owner':'',
               'resource_data_owner':'',
               'resource_TTL':'',
               'resource_subject':'',
               'resource_title':''.join(doc.getField('title')),
               'resource_desctiption':''.join(doc.getField('title')),
               'payload_placement':'linked',
               'payload_schema':'lre4',
               'payload_locator':'http://lrecoreprod.eun.org:6080/oaitarget/OAIHandler?verb=GetRecord&metadataPrefix=oai_lre4&identifier='.join(identifier)
            }
    return value
if __name__ == '__main__':
    main_url = 'http://localhost:5984/'    
    oai_url = 'http://lrecoreprod.eun.org:6080/oaitarget/OAIHandler'
    database_name = 'resource_data'
    oai_lre4_reader = MetadataReader(
    fields={        
    'title'      :  ('textList', 'ims:expression/ims:description/ims:metadata/lom:lom/lom:general/lom:title/lom:string/text()'),
    'identifier' :  ('textList', 'ims:expression/ims:identifier/ims:entry/text()'),
    'location'   :  ('textList', 'ims:expression/ims:manifestation/ims:item/ims:location/ims:uri/text()'),
    },
    namespaces={
    'oai' : 'http://www.openarchives.org/OAI/2.0/',
    'ims' : 'http://www.imsglobal.org/xsd/imslorsltitm_v1p0',
    'lom' : 'http://ltsc.ieee.org/xsd/LOM'}
    )
    prefix = 'oai_lre4'
    index_documents(main_url,database_name,oai_url,oai_lre4_reader,prefix,format)
