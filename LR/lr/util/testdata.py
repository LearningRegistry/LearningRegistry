'''
Created on Oct 12, 2011

@author: jklo
'''

import socket, uuid


def getDC_v1_1(resource_url="http://www.learningregistry.org/test-data"):
    blob = '''<metadata
  xmlns="http://www.learningregistry.org/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://example.org/myapp/ http://example.org/myapp/schema.xsd"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>
    DC 1.1 Test Data
  </dc:title>
  <dc:description>
    This is a metadata document that is used for testing linked data consumption for OAI-PMH service
  </dc:description>
  <dc:publisher>
    The Learning Registry
  </dc:publisher>
  <dc:identifier>{identifier}</dc:identifier>
</metadata>'''.format(identifier=resource_url)
    return blob

def buildTestDoc(submitter, keys, type, schemas, data, locator, schema_locator):
  testDoc = {
             "resource_data": data,
             "keys": keys, 
             "TOS":{
                  "submission_attribution":"My Attribution",
                  "submission_TOS":"My TOS"
              },
             "payload_placement":"inline",
             "active": True,
             "resource_locator": locator,
             "doc_type":"resource_data",
             "resource_data_type": type,
             "payload_schema": schemas,
             "payload_schema_locator": schema_locator,
             "doc_version":"0.23.0",
             "identity":{
                         "submitter":submitter,
                         "submitter_type":"agent"
                         }
             }
  return testDoc

def gen_doc_id(scope="nosetest"):
  base_doc_id = 'urn:{domain}:{scope}:{uuid}'.format(domain=socket.gethostname(), scope=scope, uuid=uuid.uuid1())
  rev = 0
  while True:
    yield "%s-%d" % (base_doc_id, rev)
    rev += 1

def buildReplacementTestDoc(doc_ID):
  base_rd3 = {
    'doc_ID': doc_ID,
    'TOS': {
        'submission_attribution': 'Example', 
        'submission_TOS': 'http://example.com/terms'
    }, 
    'payload_placement': 'inline', 
    'active': True, 
    'identity': {
        'submitter': 'Test Agent', 
        'submitter_type': 'agent'
    }, 
    'resource_locator': 'http://example.com', 
    'doc_type': 'resource_data', 
    'resource_data': {
        "testing":"data", 
        "version":0
    },
    'resource_data_type': 'metadata', 
    'payload_schema_locator': 'http://example.com/schema/locator', 
    'payload_schema': ['example'], 
    'doc_version': '0.49.0'
  }
  return base_rd3

def getTestDataForMultipleResourceLocator(locator_count=2, scope="nosetest"):
  doc_id = gen_doc_id()
  doc = buildReplacementTestDoc(doc_ID=doc_id.next())
  locator_tmpl = doc["resource_locator"] + "/" + doc["doc_ID"] + "/{0}"
  doc["resource_locator"] = []
  for i in range(locator_count):
    doc["resource_locator"].append(locator_tmpl.format(i))

  return [doc]

def getTestDataForReplacement(count=2, delete_last=False, scope="nosetest"):
  data = []
  doc_id = gen_doc_id()
  for i in range(count):
    data.append(buildReplacementTestDoc(doc_ID=doc_id.next()))
    if i > 0:
      data[-1].update({
          "replaces": [ data[-2]["doc_ID"] ]
        })
      data[-1]["resource_data"].update({
          "version": data[-2]["resource_data"]["version"]+1
        })

  if delete_last == True:
    data[-1].update({
      "payload_placement": "none"
      })
    del data[-1]["resource_locator"]
    del data[-1]["resource_data"]
    del data[-1]["payload_schema_locator"]
    del data[-1]["payload_schema"]

  return data

def getTestDataForMetadataFormats(count=1):
  args = {
          "submitter": "OAI-PMH Test Harness",
          "keys": ["lr-test-data"],
          "type": "metadata",
          "locator": "http://www.learningregistry.org/test-metadata-formats",
          "data": getDC_v1_1("http://www.learningregistry.org/test-metadata-formats"),
          "schemas": [
                      "0valid_ABCDEFGHIJKLMNOPQRSTUVWXYZ_schema",
                      "1valid_abcdefghijklmnopqrstuvwxyz_schema",
                      "2valid_0123456789_schema",
                      "3valid_-_.!~*'()_schema",
                      "4invalid_ `@#$%^&+={}[]:;\"<>,?/\\|schema",
                      ],
          "schema_locator": "http://example.org/myapp/ http://example.org/myapp/schema.xsd"
          }
  data = []
  for _ in range(count):
      data.append(buildTestDoc(**args))
  return data

def getTestDataForEmbeddedXMLDOCTYPEHeaders():
  args = {
        "submitter": "OAI-PMH Test Harness",
        "keys": ["lr-test-data"],
        "type": "metadata",
        "locator": "http://www.learningregistry.org/test-metadata-formats",
        "schema_locator": "http://example.org/myapp/ http://example.org/myapp/schema.xsd"
        }

  data =[]

  def push(elem={}):
    elem.update(args)
    data.append(buildTestDoc(**elem))

  push({
      "schemas":["DC_WITH_XML_DECLARATION","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_ML","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
      ''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_DOCTYPE","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?><!DOCTYPE rdf:RDF SYSTEM "http://dublincore.org/documents/2001/04/11/dcmes-xml/dcmes-xml-dtd.dtd">''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_DOCTYPE_ML1","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
      <!DOCTYPE rdf:RDF SYSTEM "http://dublincore.org/documents/2001/04/11/dcmes-xml/dcmes-xml-dtd.dtd">''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_DOCTYPE_ML2","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
      <!DOCTYPE rdf:RDF SYSTEM "http://dublincore.org/documents/2001/04/11/dcmes-xml/dcmes-xml-dtd.dtd">''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_DOCTYPE_ML3","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
      <!DOCTYPE rdf:RDF SYSTEM "http://dublincore.org/documents/2001/04/11/dcmes-xml/dcmes-xml-dtd.dtd">
      ''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_DOCTYPE_ML4","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
      <!DOCTYPE rdf:RDF 
      SYSTEM "http://dublincore.org/documents/2001/04/11/dcmes-xml/dcmes-xml-dtd.dtd">
      ''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })

  push({
      "schemas":["DC_WITH_XML_DECLARATION_DOCTYPE_ML4","DC_XML_HEADERS"],
      "data": '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
      <!DOCTYPE rdf:RDF SYSTEM 
      "http://dublincore.org/documents/2001/04/11/dcmes-xml/dcmes-xml-dtd.dtd">
      ''' + getDC_v1_1("http://www.learningregistry.org/test-metadata-formats")
  })
 
  return data