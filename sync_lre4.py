#!/usr/bin/env python
# update
import couchdb, sys
from oaipmh.client import Client
from oaipmh.common import Identify, Metadata, Header
from oaipmh.metadata import MetadataRegistry, oai_dc_reader , MetadataReader
from util import *
def format(doc, identifier):
    value = {
               'envelope_type': 'learning resource',
               'resource_title':''.join(doc.getField('title')),
               'resource_locator': ''.join(doc.getField('location')),
               'resource_metadata-locator':'http://lrecoreprod.eun.org:6080/oaitarget/OAIHandler?verb=GetRecord&metadataPrefix=oai_lre4&identifier='.join(identifier),
               'envelope_date-created':'',
               'envelope_date-received':'',
               'envelope_creator':'github@learningregistry.org',
               'resource_usage_rights_hint':'FreeToUseOrShare',
               'set':'commercial',
               'resource_license_url':'',
               'resource_descriptor':'',
               'envelope_resource_subject-area_hints':'',
               'accept_terms_of_service':True,
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
