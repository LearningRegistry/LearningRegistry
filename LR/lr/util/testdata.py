'''
Created on Oct 12, 2011

@author: jklo
'''


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