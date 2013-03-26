from StringIO import StringIO
from iso8601.iso8601 import ParseError
from lr.lib import helpers
from lr.lib.oaipmh import oaipmh, getMetadataPrefix
from lr.tests import *
from lxml import etree
from pylons import config
from random import choice
from routes.util import url_for
import copy
import couchdb
import datetime
import iso8601
import json
import logging
import math
import os
import pprint
import re
import subprocess
import time
import unittest
import urllib2
import uuid
from lr.util.testdata import getDC_v1_1, getTestDataForMetadataFormats, getTestDataForEmbeddedXMLDOCTYPEHeaders
from lr.util.decorators import PublishTestDocs, ForceCouchDBIndexing, ModifiedServiceDoc, update_authz
from lr.util.validator import XercesValidator, validate_xml_content_type, validate_json_content_type, parse_response, validate_lr_oai_etree, validate_lr_oai_response

json_headers={'content-type': 'application/json'}

namespaces = {
              "oai" : "http://www.openarchives.org/OAI/2.0/",
              "lr" : "http://www.learningregistry.org/OAI/2.0/",
              "oai_dc" : "http://www.openarchives.org/OAI/2.0/oai_dc/",
              "oai_lr" : "http://www.learningregistry.org/OAI/2.0/oai_dc/",
              "dc":"http://purl.org/dc/elements/1.1/",
              "dct":"http://purl.org/dc/terms/",
              "nsdl_dc":"http://ns.nsdl.org/nsdl_dc_v1.02/",
              "ieee":"http://www.ieee.org/xsd/LOMv1p0",
              "xsi":"http://www.w3.org/2001/XMLSchema-instance"
              }

time_format = '%Y-%m-%d %H:%M:%S.%f'
log = logging.getLogger(__name__)



nsdl_data = { "documents" : [], "ids": [] }
dc_data = { "documents" : [], "ids": [] }
sorted_dc_data = { "documents" : [], "ids": [] }
sorted_nsdl_data = { "documents" : [], "ids": [] }

class TestOaiPmhControllerSpecialData(TestController):
    @classmethod
    def setUpClass(self):
        self.o = oaipmh()
        self.server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.db =  self.server[config['couchdb.db.resourcedata']] 

    @classmethod
    def tearDownClass(self):
        pass

    @PublishTestDocs(getTestDataForEmbeddedXMLDOCTYPEHeaders(), "XML-HEADERS-AND-DOCTYPES")
    def test_documents_with_xml_header_or_doctype_declarations(self, *var, **kw):
        ''''verify that xml resource_data with embedded <?xml?> and <!DOCTYPE> declarations can be retrieved.'''

        test_docs = self.test_data_sorted["XML-HEADERS-AND-DOCTYPES"]

        assert len(test_docs) > 0, "missing test documents"

        def validateRecord(doc, record):
            try:
                ident = record.xpath("./oai:header/oai:identifier/text()", namespaces=namespaces)[0]
            except:
                ident = None

            assert ident == doc["doc_ID"], "unexpected doc_ID returned, expected {0}, got {1}".format(doc["doc_ID"], ident)

            try:
                data = record.xpath("./oai:metadata/*", namespaces=namespaces)[0]
            except:
                data = None
            
            assert data != None, "unexpected resource data in metadata field"

        def processRecord(doc):
            response = self.app.get("/OAI-PMH", params={"verb":"GetRecord", "metadataPrefix":"DC_XML_HEADERS", "identifier":doc["doc_ID"], "by_doc_ID": "true"})
            validate_xml_content_type(response)
            obj = parse_response(response)
            records = obj["etree"].xpath("/lr:OAI-PMH/lr:GetRecord/lr:record", namespaces=namespaces)
            assert len(records) == 1, "wrong number of records returned, expected 1 got {0}".format(len(records))
            validateRecord(doc, records[0])
            

        def processRecords(docs):
            response = self.app.get("/OAI-PMH", params={"verb":"ListRecords", "metadataPrefix":"DC_XML_HEADERS" })
            validate_xml_content_type(response)
            obj = parse_response(response)
            records = obj["etree"].xpath("/lr:OAI-PMH/lr:ListRecords/oai:record", namespaces=namespaces)
            assert len(records) == len(docs), "wrong number of records returned, expected {1} got {0}".format(len(records), len(docs))

        for doc in test_docs:
            processRecord(doc)

        processRecords(test_docs)
    

    @PublishTestDocs(getTestDataForMetadataFormats(1), "LMF-schema-syntax")
    def test_listMetadataFormats_schema_format_syntax(self, *var, **kw):
        '''validates that the schema format provided by the response to verb ListMetadataFormats is of the acceptable OAI-PMH format.'''
        validPrefix = '''^[A-Za-z0-9\-_\.!~\*'\(\)]+$'''
        
        doc = self.test_data_sorted["LMF-schema-syntax"][0]
        
        def checkFormats(response):
            validate_xml_content_type(response)
            obj = parse_response(response)
            metadataPrefixes = obj["etree"].xpath("/lr:OAI-PMH/lr:ListMetadataFormats/oai:metadataFormat/oai:metadataPrefix/text()", namespaces=namespaces)
            
            assert len(metadataPrefixes) > 0, "Missing payload schemas in response:\n%s" % obj["raw"]
            
            for prefix in metadataPrefixes:
                assert re.match(validPrefix, prefix) != None, "test_listMetadataFormats_schema_format_syntax: Bad metadataPrefix '%s'" % prefix
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        checkFormats(response)
        
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats', 'identifier': doc["resource_locator"], 'by_doc_ID': 'false'})
        checkFormats(response)
        
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats', 'identifier': doc["doc_ID"], 'by_doc_ID': 'true'})
        checkFormats(response)
        
    @PublishTestDocs(getTestDataForMetadataFormats(1), "GR-schema-syntax")
    def test_getRecord_schema_format_syntax(self, *var, **kw):
        '''validate that both good and bad metadataPrefixes are used when requesting GetRecord the appropriate response is returned'''
        validPrefix = '''^[A-Za-z0-9\-_\.!~\*'\(\)]+$'''
        
        doc = self.test_data_sorted["GR-schema-syntax"][0]
        
        def checkFormats(response, expectValid):
            validate_xml_content_type(response)
            obj = parse_response(response)
            if expectValid:
                identifier = obj["etree"].xpath("/lr:OAI-PMH/lr:GetRecord/lr:record/oai:header/oai:identifier/text()", namespaces=namespaces)
                assert len(identifier) > 0, "Expected a valid response, got this instead:\n%s" % obj["raw"]
            else:
                errors = obj["etree"].xpath("/lr:OAI-PMH//lr:error/@code", namespaces=namespaces)
                assert len(errors) > 0, "Expected an error, got this instead:\n%s" % obj["raw"]
        
        assert len(doc["payload_schema"]) > 0, "test_getRecord_schema_format_syntax: Test data is missing payload_schema"
        
        for schema in doc["payload_schema"]:
            if re.match(validPrefix, schema) == None:
                valid = False
                goodPrefix = getMetadataPrefix(schema)
                assert re.match(validPrefix, goodPrefix) != None, "Prefix cleaner produced an invalid prefix: '%s'" % goodPrefix
            else:
                valid = True
                goodPrefix = None
            
            response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix': schema, 'identifier': doc["doc_ID"], 'by_doc_ID': 'true'})
            checkFormats(response, valid)
            
            response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix': schema, 'identifier': doc["resource_locator"], 'by_doc_ID': 'false'})
            checkFormats(response, valid)
            
            if goodPrefix:
                response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix': goodPrefix, 'identifier': doc["doc_ID"], 'by_doc_ID': 'true'})
                checkFormats(response, True)
                
                response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix': goodPrefix, 'identifier': doc["resource_locator"], 'by_doc_ID': 'false'})
                checkFormats(response, True)
                


class TestOaiPmhController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "OAI-PMH"
    @classmethod
    @ModifiedServiceDoc(config['lr.publish.docid'], update_authz())
    def setUpClass(self):
        self.test_data_delete = True
        schema_file = file("lr/public/schemas/OAI/2.0/OAI-PMH-LR.xsd", "r")
        schema_doc = etree.parse(schema_file)
        self.oailrschema = etree.XMLSchema(schema_doc)
        
        self.validator = XercesValidator()
        
        global nsdl_data, dc_data, sorted_dc_data, sorted_nsdl_data
        self.o = oaipmh()
        self.server = self.o.server
        self.db = self.o.db
        
        view_data = self.db.view('oai-pmh-test-data/docs')
    
        dropData = False
        if "oaipmh.drop_data_on_launch" in config:
            dropData =  config["oaipmh.drop_data_on_launch"] in ["true", "True"]
        
        if len(view_data) > 0 and dropData:
            for data in view_data:
                try:
                    del self.db[data.id+"-distributable"]
                    log.debug("Deleting id: %s" % data.id+"-distributable")
                except:
                    pass
                try:
                    del self.db[data.id]
                    log.debug("Deleting id: %s" % data.id)
                except:
                    pass
            view_data = self.db.view('oai-pmh-test-data/docs')
        
        if (len(view_data) == 0):
            
            if hasattr(self, "attr"):
                app = self.app
            else:
                controller =  TestOaiPmhController(methodName="test_empty")
                app = controller.app
            
            nsdl_data = json.load(file("lr/tests/data/nsdl_dc/data-000000000.json"))
            for doc in nsdl_data["documents"]:
                doc["doc_ID"] = "NSDL-TEST-DATA-"+str(uuid.uuid1())
                app.post('/publish', params=json.dumps({"documents": [ doc ]}), headers=json_headers)
                log.debug("Published ID: %s" % doc["doc_ID"])
                time.sleep(1)
            
            dc_data = json.load(file("lr/tests/data/oai_dc/data-000000000.json"))
            for doc in dc_data["documents"]:
                doc["doc_ID"] = "OAI-DC-TEST-DATA-"+str(uuid.uuid1())
                app.post('/publish', params=json.dumps({"documents": [ doc ]}), headers=json_headers)
                log.debug("Published ID: %s" % doc["doc_ID"])
                time.sleep(1)
 
            view_data = self.db.view('oai-pmh-test-data/docs')
        
        nsdl_data = { "documents" : [], "ids": [] }
        dc_data = { "documents" : [], "ids": [] }
        for row in view_data:
            if re.search("^NSDL-TEST-DATA-", row.key) != None and re.search("-distributable$", row.key) == None:
                nsdl_data["documents"].append(row.value)
                nsdl_data["ids"].append(row.id)
            if re.search("^OAI-DC-TEST-DATA-", row.key) != None and re.search("-distributable$", row.key) == None:
                dc_data["documents"].append(row.value)
                dc_data["ids"].append(row.id)
                
        sorted_dc_data = {
                          "documents": sorted(dc_data["documents"], key=lambda k: k['node_timestamp']),
                          "ids": []
                          } 
        
        for sort in sorted_dc_data["documents"]:
            sorted_dc_data["ids"].append(sort["doc_ID"])
            
        sorted_nsdl_data = {
                          "documents": sorted(nsdl_data["documents"], key=lambda k: k['node_timestamp']),
                          "ids": []
                          } 
        
        for sort in sorted_nsdl_data["documents"]:
            sorted_nsdl_data["ids"].append(sort["doc_ID"])
            
        
    @classmethod       
    def tearDownClass(self):
       
        log.info ("Tearing Down Test")
        if TestOaiPmhController.test_data_delete == True:
            for doc in nsdl_data["documents"]:
                try:
                    del self.db[doc["_id"]]
                    log.debug("Deleted ID: %s" % doc["_id"])
                except:
                    pass
                try:
                    del self.db["{0}-distributable".format(doc["_id"])]
                    log.debug("Deleted ID: %s" % "{0}-distributable".format(doc["_id"]))
                except:
                    pass
            for doc in dc_data["documents"]:
                try:
                    del self.db[doc["_id"]]
                    log.debug("Deleted ID: %s" % doc["_id"])
                except:
                    pass
                try:
                    del self.db["{0}-distributable".format(doc["_id"])]
                    log.debug("Deleted ID: %s" % "{0}-distributable".format(doc["_id"]))
                except:
                    pass
        else:
            log.error("Not deleting test data!!!")
        log.info ("Tearing Down Test Complete")
                
                
    def _is_test_data(self, identifier):
        try:
            if re.search("^NSDL-TEST-DATA-", identifier) != None and re.search("-distributable$",identifier) == None and nsdl_data["ids"].index(identifier) >= 0:
                return True
            elif re.search("^OAI-DC-DATA-", identifier) != None and re.search("-distributable$",identifier) == None and nsdl_data["ids"].index(identifier) >= 0:
                return True
            else:
                return False
        except:
            return False
    
    def _sanitize_timestamp(self, tstamp):
        fix =  re.sub("\.[0-9]+Z$", "Z", tstamp)
        return fix

    def _get_timestamps(self, doc1, doc2):
        if doc1["node_timestamp"] < doc2["node_timestamp"]:
            from_ =  doc1["node_timestamp"]
            until_ = doc2["node_timestamp"]
        else:
            until_ =  doc1["node_timestamp"]
            from_ = doc2["node_timestamp"]
        
        from_ = re.sub("\.[0-9]+Z", "Z", from_)
        until_ = re.sub("\.[0-9]+Z", "Z", until_)
        
        return (from_, until_)
    
        
    def validate_lr_oai_response(self, response, errorExists=False, checkSchema=False, errorCodeExpected=None):
        validate_xml_content_type(response)
        
        obj = parse_response(response)
        xmlcontent = obj["etree"]
        validate_lr_oai_etree(xmlcontent, errorExists, checkSchema, errorCodeExpected)

        schemaErrors = self.validator.validate(obj["raw"])
        assert len(schemaErrors) == 0, "validate_lr_oai_response: Schema validation error:\n%s" % '\n'.join(map(lambda x: "\t(line: {0}, char: {1}): {2}".format(x["line"], x["char"], x["msg"]), schemaErrors))
        
        


    def test_empty(self):
            pass
    
    def test_get_oai_lr_schema(self):
        try:
            res2 = self.app.get("/schemas/OAI/2.0/OAI-PMH-LR.xsd")
            schemaErrors = self.validator.validate(res2.body)
            assert len(schemaErrors) == 0, "Schema validation error:\n%s" % '\n'.join(map(lambda x: "\t(line: {0}, char: {1}): {2}".format(x["line"], x["char"], x["msg"]), schemaErrors))

            log.info("test_get_oai_lr_schema: pass")
        except Exception as e:
            raise e
        
    @ForceCouchDBIndexing()    
    def test_identify_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'Identify'})
        validate_lr_oai_response(response)
        log.info("test_identify_get: pass")
   
    @ForceCouchDBIndexing()    
    def test_identify_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        validate_lr_oai_response(response)
        log.info("test_identify_post: pass")
    
    @ForceCouchDBIndexing()    
    def test_identify_earliest_datestamp(self):
        '''test_identify_earliest_datestamp: 
        verify that the network node maintains a value for the earliest publication 
        time for documents harvestable from the node (earliestDatestamp)'''
        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        validate_xml_content_type(response)
        root = etree.fromstring(response.body)
        earliestDatestamp = root.xpath('/lr:OAI-PMH/lr:Identify/oai:earliestDatestamp/text()', namespaces=namespaces)
        
        assert len(earliestDatestamp) == 1, "Identify: missing earliest datestamp"
        
        try:
            earliest_datestamp = iso8601.parse_date(earliestDatestamp[0])
        except ParseError:
            self.fail("Identify: earliestDatestamp does not parse as iso8601")
        
        log.info("test_identify_earliest_datestamp: pass")
    
    @ForceCouchDBIndexing()    
    def test_identify_timestamp_granularity(self):
        '''test_identify_timestamp_granularity: 
        verify that the granularity of the timestamp exists in Identify.'''

        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        validate_xml_content_type(response)
        root = etree.fromstring(response.body)
        identifyGranularity = root.xpath('/lr:OAI-PMH/lr:Identify/oai:granularity/text()', namespaces=namespaces)
        
        assert len(identifyGranularity) == 1, "Identify: missing <granularity>"
        
        log.error("test_identify_timestamp_granularity: pass")
        
    @ForceCouchDBIndexing()
    def test_identify_timestamp_granularity_service_doc(self):
        '''test_identify_timestamp_granularity_service_doc: 
        verify that the granularity of the timestamp is stored in the service 
        description document.'''
        serviceDoc = helpers.getServiceDocument(config["lr.oaipmh.docid"])
        assert serviceDoc is not None, "Service document '%s' is missing." % config["lr.oaipmh.docid"]
        
        try:
            granularity = serviceDoc["service_data"]["granularity"]
        except:
            self.fail("%s: granularity setting missing from service document." % config["lr.oaipmh.docid"])
            
        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        validate_xml_content_type(response)
        root = etree.fromstring(response.body)
        identifyGranularity = root.xpath('/lr:OAI-PMH/lr:Identify/oai:granularity/text()', namespaces=namespaces)
        
        assert len(identifyGranularity) == 1, "Identify: missing <granularity>"
        
        assert identifyGranularity[0] == granularity, "Identify: <granularity> does not match service document setting."
        
        log.info("test_identify_timestamp_granularity_service_doc: pass")
        
        
    def test_ListSets_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'ListSets'})
        validate_lr_oai_response(response, errorExists=True, errorCodeExpected="noSetHierarchy")
        log.info("test_ListSets_get: pass")
        
    def test_ListSets_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'ListSets'})
        validate_lr_oai_response(response, errorExists=True, errorCodeExpected="noSetHierarchy")
        log.info("test_ListSets_post: pass")
        
        
    @ForceCouchDBIndexing()    
    def test_listMetadataFormats_with_doc_id_identifier_get(self):
        '''test_listMetadataFormats_with_doc_id_identifier_get: 
        verify that if an identifier is provided, the metadata formats are 
        returned only for the identified resource data description documents.'''
        global sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': 'true'})
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)
            
            metadataPrefixes = obj["etree"].xpath("/lr:OAI-PMH/lr:ListMetadataFormats/oai:metadataFormat/oai:metadataPrefix/text()", namespaces=namespaces)
            assert len(metadataPrefixes) == len(randomDoc["payload_schema"]), "test_listMetadataFormats_with_doc_id_identifier_get: the count of payload_schema does not match the number of metadataPrefixes"
            
            for prefix in metadataPrefixes:
                assert prefix in randomDoc["payload_schema"], "test_listMetadataFormats_with_doc_id_identifier_get: metadataPrefix returned that does not exist in payload_schema. %s not in %s" % (prefix, ", ".join(metadataPrefixes))
                
        except Exception as e:
#            log.error("test_listMetadataFormats_get: fail")
            log.exception("test_listMetadataFormats_with_doc_id_identifier_get: fail")
            raise e
        log.info("test_listMetadataFormats_with_doc_id_identifier_get: pass")
    
    @ForceCouchDBIndexing()    
    def test_listMetadataFormats_with_resource_id_identifier_get(self):
        '''test_listMetadataFormats_with_resource_id_identifier_get: 
        verify that if an identifier is provided, the metadata formats are 
        returned only for the identified resource data description documents.'''
        global sorted_dc_data
        
        # There are 2 documents with this same URL with the same format
        resource_locator = "http://hdl.loc.gov/loc.gdc/collgdc.gc000019"
        
        # all docs that have the same resource_locator
        opts = {"key": ["by_resource_locator", resource_locator], 
                "include_docs": "true"}
        all_matching_docs = self.db.view("oai-pmh-get-records/docs", **opts)
        schema_formats = []
        for row in all_matching_docs.rows:
            if "payload_schema" in row.doc:
                for s in row.doc["payload_schema"]:
                    if s.strip() not in schema_formats:
                        schema_formats.append(s.strip())
            
        
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats', 'identifier': resource_locator, 'by_doc_ID': 'false'})
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)
            
            metadataPrefixes = obj["etree"].xpath("/lr:OAI-PMH/lr:ListMetadataFormats/oai:metadataFormat/oai:metadataPrefix/text()", namespaces=namespaces)
            assert len(metadataPrefixes) == len(schema_formats), "test_listMetadataFormats_with_resource_id_identifier_get: the count of payload_schema does not match the number of metadataPrefixes"
            
            for prefix in metadataPrefixes:
                assert prefix in schema_formats, "test_listMetadataFormats_with_resource_id_identifier_get: metadataPrefix returned that does not exist in payload_schema. %s not in %s" % (prefix, ", ".join(metadataPrefixes))
                
        except Exception as e:
#            log.error("test_listMetadataFormats_get: fail")
            log.exception("test_listMetadataFormats_with_resource_id_identifier_get: fail")
            raise e
        log.info("test_listMetadataFormats_with_resource_id_identifier_get: pass")        

    @ForceCouchDBIndexing()    
    def test_listMetadataFormats_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listMetadataFormats_get: fail")
            log.exception("test_listMetadataFormats_get: fail")
            raise e
        log.info("test_listMetadataFormats_get: pass")
    
    @ForceCouchDBIndexing()    
    def test_listMetadataFormats_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listMetadataFormats_post: fail")
            log.exception("test_listMetadataFormats_post: fail")
            raise e
        log.info("test_listMetadataFormats_post: pass")
    
    @ForceCouchDBIndexing()
    def test_namespaceDeclarations(self):
        # according to the spec, all namespace used in the metadata
        # element should be declared on the metadata element,
        # and not on root or ancestor elements (big sigh..)
        # this works, except for the xsi namespace which is allready declared
        # on the root element, which means lxml will not declare it again on
        # the metadata element
        global sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        validate_xml_content_type(response)
        tree = etree.fromstring(response.body)
        
        metadata = tree.xpath("//oai_dc:dc", namespaces=namespaces)
        
        if len(metadata) != 1:
            self.fail("test_namespaceDeclarations: fail - Missing Metadata")
        else:
            for meta in metadata:
                log.info("test_namespaceDeclarations medatdada: prefix:{0} name:{1}".format(meta.prefix, meta.tag))
                pat = "<oai_dc:dc[^>]*\sxmlns:{0}=".format(meta.prefix)
                self.assertTrue(str(re.match(pat, etree.tostring(meta), flags=re.MULTILINE)!=None), "test_namespaceDeclarations: fail - namespace declaration not present")
        

    @ForceCouchDBIndexing()
    def test_getRecord_by_doc_ID_match_requested_dissemination_get(self):
        '''test_getRecord_by_doc_ID_match_requested_dissemination_get: 
        verify that the returned resource data matches the requested dissemination 
        format for the specified  resource data description document ID or resource ID'''
        
        '''test_getRecord_by_doc_ID_match_requested_dissemination_get: 
        verify that if the request ID is a resource data description document 
        ID, the service returns the metadata dissemination for the single resource 
        data description document that matches the ID'''
        
        '''test_getRecord_by_doc_ID_match_requested_dissemination_get: 
        verify that the return of any resource_data that matches the requested 
        dissemination format associated with the requested resource data document 
        (any payload where the payload_schema matches the requested dissemination 
        format) is supported.'''
        
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)           
            
            assert len(randomDoc["payload_schema"]) > 0, "test_getRecord_match_requested_dissemination_get: Test document missing payload_schema"
            
            hasSchema = False
            for schema in randomDoc["payload_schema"]: 
                if schema == "oai_dc":
                    hasSchema = True
                    continue
            
            assert hasSchema, "test_getRecord_match_requested_dissemination_get: Test document does not have a matching payload_schema"
            
            identifier = obj["etree"].xpath("/lr:OAI-PMH/lr:GetRecord/lr:record/oai:header/oai:identifier/text()", namespaces=namespaces)
            
            assert len(identifier) == 1 and identifier[0] == randomDoc["doc_ID"], "test_getRecord_match_requested_dissemination_get: Requested document does not match."
            
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_match_requested_dissemination_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            raise e
        log.info("test_getRecord_match_requested_dissemination_get: pass")

    @ForceCouchDBIndexing()
    def test_getRecord_by_doc_ID_JSON_metadataPrefix_get(self):
        '''test_getRecord_by_doc_ID_JSON_metadataPrefix_get: 
        verify that if the requested dissemination format in metadataPrefix 
        matches the JSON metadataPrefix in the servcie description the service 
        behaves as the basic harvest service (returns the complete resource data 
        description document as JSON).'''
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'LR_JSON_0.10.0', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        validate_json_content_type(response)
        try:
            json_obj = json.loads(response.body)
            
            assert len(json_obj["getrecord"]["record"]) == 1, "test_getRecord_by_doc_ID_JSON_metadataPrefix_get: No JSON record returned"
            assert json_obj["getrecord"]["record"][0]["resource_data"] == randomDoc, "test_getRecord_by_doc_ID_JSON_metadataPrefix_get: Returned document does not match."
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_by_doc_ID_JSON_metadataPrefix_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))

            raise e
        log.info("test_getRecord_by_doc_ID_JSON_metadataPrefix_get: pass")
    
    @ForceCouchDBIndexing()    
    def test_getRecord_by_doc_ID_get(self):
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            raise e
        log.info("test_getRecord_by_doc_ID_get: pass")
    
    @ForceCouchDBIndexing()    
    def test_getRecord_by_doc_ID_post(self):
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.post("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_post: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_by_doc_ID_post: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            raise e
        log.info("test_getRecord_by_doc_ID_post: pass")
    
    @ForceCouchDBIndexing()
    def test_getRecord_by_resource_ID_get(self):
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["resource_locator"], 'by_resource_ID': True})
        try:
            validate_lr_oai_response(response)
        except AssertionError:
            log.exception("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            raise
        except Exception as e:
#            log.error("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            log.exception("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            raise e
        log.info("test_getRecord_by_resource_ID_get: pass")
    
    @ForceCouchDBIndexing()    
    def test_getRecord_by_resource_ID_post(self):
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.post("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["resource_locator"], 'by_resource_ID': True})
        try:
            validate_lr_oai_response(response)
        except AssertionError:
            log.exception("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            raise
        except Exception as e:
#            log.error("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            log.exception("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            raise e
        log.info("test_getRecord_by_resource_ID_post: pass")

    @ForceCouchDBIndexing()
    def test_listRecords_post(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.post("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listRecords_post: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_post: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listRecords_post: pass")
    
    @ForceCouchDBIndexing()    
    def test_listRecords_match_requested_disseminaton_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)
            oaipmh_root = obj["etree"]
            
            response_ids = oaipmh_root.xpath("./lr:ListRecords/oai:record/oai:header/oai:identifier/text()", namespaces=namespaces)
            assert len(response_ids) > 0, "test_listRecords_match_requested_disseminaton_get: Unable to locate identifiers in response"
            
            for identifier in response_ids:
                '''need to weed out any non-known test data since this is based upon a range'''
                if self._is_test_data(identifier):
                    try: 
                        assert sorted_nsdl_data["ids"].index(identifier) >= 0, "Unexpected test identifier returned in result"
                    except:
                        self.fail("Identifier %s should have existed within result and did not" % identifier)
            
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_match_requested_disseminaton_get: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listRecords_match_requested_disseminaton_get: pass")

    @ForceCouchDBIndexing()
    def test_listRecords_noRecordsMatch_get(self):
        '''test_listRecords_noRecordsMatch_get:
        verify that if no records match the requested metadata dissemination 
        format, the error code noRecordsMatch is displayed.'''
        global nsdl_data, dc_data, sorted_dc_data
        last_doc = sorted_dc_data["documents"][-1]
        
        
        last_time = iso8601.parse_date(last_doc["node_timestamp"], default_timezone=iso8601.iso8601.UTC)
        time_after = last_time + datetime.timedelta(0,5)
        from_ = helpers.convertToISO8601Zformat(time_after)
        from_ = self._sanitize_timestamp(from_)
        
        log.info("Sleeping for 10 seconds... so we don't accidently use a from time in the future.")
        time.sleep(10)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'oai_dc', 'from': from_ })
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)
            
            errors = obj["etree"].xpath("/lr:OAI-PMH//lr:error/@code", namespaces=namespaces)
            
            assert len(errors) > 0, "test_listRecords_noRecordsMatch_get: Expected at least one error to be returned in response."
            
            noRecordsMatch = False
            for error in errors:
                if error == 'noRecordsMatch': noRecordsMatch = True
                
            assert noRecordsMatch, "test_listRecords_noRecordsMatch_get: noRecordsMatch error was not returned; instead got: %s" % ', '.join(errors)
            
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_noRecordsMatch_get: fail - from: {0}".format(from_))
            raise e
        log.info("test_listRecords_noRecordsMatch_get: pass")
    
    @ForceCouchDBIndexing()
    def test_listRecords_JSON_metadataPrefix_get(self):
        '''test_listRecords_JSON_metadataPrefix_get:
        verify that if the requested dissemination format in metadataPrefix 
        matches the JSON metadataPrefix in the service description the service 
        behaves as the basic harvest service (returns the complete resource data 
        description document as JSON).'''
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'LR_JSON_0.10.0', 'from': from_, 'until': until_})
        validate_json_content_type(response)
        try:
            json_obj = json.loads(response.body)
            
            assert len(json_obj["listrecords"]) > 0, "test_listRecords_JSON_metadataPrefix_get: No JSON records returned"
            for entry in json_obj["listrecords"]:
                try:
                    resource_data = entry["record"]["resource_data"]
                except:
                    self.fail("test_listRecords_JSON_metadataPrefix_get: result missing expected resource data.")
                
                try:
                    doc_idx = sorted_nsdl_data["ids"].index(resource_data["doc_ID"])
                    assert sorted_nsdl_data["documents"][doc_idx] == resource_data, "test_listRecords_JSON_metadataPrefix_get: Returned document does not match."
                except:
                    pass # This should be okay - result may be an element not inserted by the test.
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_listRecords_JSON_metadataPrefix_get: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listRecords_JSON_metadataPrefix_get: pass")
    
    @ForceCouchDBIndexing()
    def test_listRecords_flow_control_get(self):
        global nsdl_data, dc_data, sorted_nsdl_data
        doc1 = sorted_nsdl_data["documents"][0]
        doc2 = sorted_nsdl_data["documents"][-1]
        
        item_limit = int(math.ceil(len(sorted_nsdl_data["documents"]) * (2.0/3.0)))
        
        node_db = self.server[config["couchdb.db.node"]]
        service_doc_org = node_db[config["lr.oaipmh.docid"]] 
        
        service_doc_copy = copy.deepcopy(service_doc_org)
        service_doc_copy["service_data"]["flow_control"] = True
        service_doc_copy["service_data"]["doc_limit"] = item_limit
        
        node_db[service_doc_copy.id] = service_doc_copy
        
        try:
            (from_, until_) = self._get_timestamps(doc1, doc2)
             
            response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
            validate_xml_content_type(response)
            try:
                obj = parse_response(response)
                resumptionToken = obj["etree"].xpath("/lr:OAI-PMH/lr:ListRecords/oai:resumptionToken/text()", namespaces=namespaces)
                
                assert len(resumptionToken) == 1, "test_listRecords_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken)
                
                response2 = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_, 'resumptionToken': resumptionToken[0]})
                validate_xml_content_type(response2)
                obj2 = parse_response(response2)
                
                resumptionToken2 = obj2["etree"].xpath("/lr:OAI-PMH/lr:ListRecords/oai:resumptionToken", namespaces=namespaces)
                
                assert len(resumptionToken2) == 1, "test_listRecords_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken2)
                assert resumptionToken2[0].text == None or resumptionToken2[0].text == "", "test_listRecords_flow_control_get: expected last resumptionToken got '%s'" % resumptionToken2[0].text
                
            except Exception as e:
    #            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
                log.exception("test_listRecords_flow_control_get: fail - from: {0} until: {1}".format(from_, until_))
                raise e
            log.info("test_listRecords_flow_control_get: pass")
        finally:
            service_doc_copy = node_db[service_doc_copy.id]
            service_doc_copy["service_data"] = service_doc_org["service_data"]
            node_db[service_doc_copy.id] = service_doc_copy
    
    @ForceCouchDBIndexing()
    def test_listRecords_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listRecords_get: pass")

        
    @ForceCouchDBIndexing()    
    def test_listIdentifiers_post(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.post("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listIdentifiers_post: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_post: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listIdentifiers_post: pass")
    
    @ForceCouchDBIndexing()    
    def test_listIdentifiers_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listIdentifiers_get: pass")
    
    @ForceCouchDBIndexing()    
    def test_listIdentifiers_flow_control_get(self):
        global nsdl_data, dc_data, sorted_nsdl_data
        doc1 = sorted_nsdl_data["documents"][0]
        doc2 = sorted_nsdl_data["documents"][-1]
        
        item_limit = int(math.ceil(len(sorted_nsdl_data["documents"]) * (2.0/3.0)))
        
        node_db = self.server[config["couchdb.db.node"]]
        service_doc_org = node_db[config["lr.oaipmh.docid"]] 
        
        service_doc_copy = copy.deepcopy(service_doc_org)
        service_doc_copy["service_data"]["flow_control"] = True
        service_doc_copy["service_data"]["id_limit"] = item_limit
        
        node_db[service_doc_copy.id] = service_doc_copy
        
        try:
            (from_, until_) = self._get_timestamps(doc1, doc2)
                
            response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
            validate_xml_content_type(response)
            try:
                obj = parse_response(response)
                resumptionToken = obj["etree"].xpath("/lr:OAI-PMH/lr:ListIdentifiers/oai:resumptionToken/text()", namespaces=namespaces)
                
                assert len(resumptionToken) == 1, "test_listIdentifiers_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken)
                
                response2 = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_, 'resumptionToken': resumptionToken[0]})
                validate_xml_content_type(response2)
                obj2 = parse_response(response2)
                
                resumptionToken2 = obj2["etree"].xpath("/lr:OAI-PMH/lr:ListIdentifiers/oai:resumptionToken", namespaces=namespaces)
                
                assert len(resumptionToken2) == 1, "test_listIdentifiers_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken2)
                assert resumptionToken2[0].text == None or resumptionToken2[0].text == "", "test_listIdentifiers_flow_control_get: expected last resumptionToken got '%s'" % resumptionToken2[0].text
                
            except Exception as e:
    #            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
                log.exception("test_listIdentifiers_flow_control_get: fail - from: {0} until: {1}".format(from_, until_))
                raise e
            log.info("test_listIdentifiers_flow_control_get: pass")
        finally:
            service_doc_copy = node_db[service_doc_copy.id]
            service_doc_copy["service_data"] = service_doc_org["service_data"]
            node_db[service_doc_copy.id] = service_doc_copy
    
    @ForceCouchDBIndexing()    
    def test_listIdentifiers_timestamp_headers_match_response_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
        
        from_tstamp = iso8601.parse_date(from_)
        until_tstamp = iso8601.parse_date(until_)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)
            
            req = obj["etree"].xpath("/lr:OAI-PMH/lr:request", namespaces=namespaces)
            
            assert len(req) == 1, "test_listIdentifiers_timestamp_headers_match_response_get: There should be exactly 1 <request/> element in the response, got %s." % len(req)
            
            assert "from" in req[0].keys() and req[0].get("from") is not None, "test_listIdentifiers_timestamp_headers_match_response_get: missing 'from' attribute"
            assert "until" in req[0].keys() and req[0].get("until") is not None, "test_listIdentifiers_timestamp_headers_match_response_get: missing 'until' attribute"
            
            record_tstamps = obj["etree"].xpath("/lr:OAI-PMH/lr:ListIdentifiers/oai:header/oai:datestamp/text()", namespaces=namespaces)
            
            assert len(record_tstamps) > 0, "test_listIdentifiers_timestamp_headers_match_response_get: at least 1 record should be returned."
            
            for tstamp in record_tstamps:
                assert from_ <= tstamp and until_ >= tstamp, "test_listIdentifiers_timestamp_headers_match_response_get: result not within range: %s <= %s <= %s" % (from_, tstamp, until_)
            
        except Exception as e:
#            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_timestamp_headers_match_response_get: fail - from: {0} until: {1}".format(from_, until_))
            raise e
        log.info("test_listIdentifiers_timestamp_headers_match_response_get: pass")
        
    @ForceCouchDBIndexing()
    def test_listIdentifiers_noRecordsMatch_get(self):
        '''test_listIdentifiers_noRecordsMatch_get:
        verify that if no records match the requested metadata dissemination 
        format, the error code noRecordsMatch is displayed.'''
        global nsdl_data, dc_data, sorted_dc_data
        last_doc = sorted_dc_data["documents"][-1]
        
        
        last_time = iso8601.parse_date(last_doc["node_timestamp"], default_timezone=iso8601.iso8601.UTC)
        time_after = last_time + datetime.timedelta(0,5)
        from_ = helpers.convertToISO8601Zformat(time_after)
        from_ = self._sanitize_timestamp(from_)
        
        log.info("Sleeping for 10 seconds... so we don't accidently use a from time in the future.")
        time.sleep(10)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'from': from_ })
        validate_xml_content_type(response)
        try:
            obj = parse_response(response)
            
            errors = obj["etree"].xpath("/lr:OAI-PMH//lr:error/@code", namespaces=namespaces)
            
            assert len(errors) > 0, "test_listIdentifiers_noRecordsMatch_get: Expected at least one error to be returned in response."
            
            noRecordsMatch = False
            for error in errors:
                if error == 'noRecordsMatch': noRecordsMatch = True
                
            assert noRecordsMatch, "test_listIdentifiers_noRecordsMatch_get: noRecordsMatch error was not returned; instead got: %s" % ', '.join(errors)
            
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_noRecordsMatch_get: fail - from: {0}".format(from_))
            raise e
        log.info("test_listIdentifiers_noRecordsMatch_get: pass")

        
