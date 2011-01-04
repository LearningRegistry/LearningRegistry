#!/usr/bin/env python
# update
import couchdb, sys
from oaipmh.client import Client
from oaipmh.common import Identify, Metadata, Header
from oaipmh.metadata import MetadataRegistry, oai_dc_reader , MetadataReader
from util import *
def format(doc):
    value = {'title':''.join(doc.getField('title')),'identifier':''.join(doc.getField('identifier')), 'location': ''.join(doc.getField('location'))}
    return value
if __name__ == '__main__':
    main_url = 'http://wegrata:g15t15@wegrata.couchone.com/'    
    oai_url = 'http://lrecoreprod.eun.org:6080/oaitarget/OAIHandler'
    database_name = 'testoai'
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
    index_documents(oai_url,main_url,database_name,oai_lre4_reader, prefix, format)