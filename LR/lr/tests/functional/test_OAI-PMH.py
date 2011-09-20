from StringIO import StringIO
from iso8601.iso8601 import ParseError
from lr.lib import helpers
from lr.lib.oaipmh import oaipmh
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



test_data_delete = True
nsdl_data = { "documents" : [], "ids": [] }
dc_data = { "documents" : [], "ids": [] }
sorted_dc_data = { "documents" : [], "ids": [] }
sorted_nsdl_data = { "documents" : [], "ids": [] }


class XercesValidator():
    def __init__(self):
        def is_exe(fpath):
            return os.path.exists(fpath) and os.access(fpath, os.X_OK)
        
        if "xerces-c.StdInParse" in config and is_exe(config["xerces-c.StdInParse"]):
            self.stdinparse = [config["xerces-c.StdInParse"], '-n', '-f', '-s']
            self.enabled = True
        else:
            self.enabled = False
            
    def validate(self, contents=""):
        errors = []
        if self.enabled:
            process = subprocess.Popen(self.stdinparse, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            xmlin = contents 
            (_, stderr) = process.communicate(input=xmlin.encode("utf8"))
            if stderr != None or stderr != "":
                err_lines = stderr.splitlines()
                for err in err_lines:
                    m = re.match('''.*\s+line\s+([0-9]+),\s+char\s+([0-9]+)\):\s*(.*)$''', err)
                    if m is not None:
                        errors.append({ "line": m.group(1), 'char': m.group(2), 'msg': m.group(3) })
        else:
            log.info("Xerces not available for validation.")
        return errors 



class TestOaiPmhController(TestController):

    @classmethod
    def setUpClass(self):

        schema_file = file("lr/public/schemas/OAI/2.0/OAI-PMH-LR.xsd", "r")
        schema_doc = etree.parse(schema_file)
        self.oailrschema = etree.XMLSchema(schema_doc)
        
        self.validator = XercesValidator()
        
        global test_data_delete, nsdl_data, dc_data, sorted_dc_data, sorted_nsdl_data
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
            
            
        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        
        # Force indexing in oai views 
        design_docs = self.db.view('_all_docs', **opts)
        for row in design_docs:
#            if re.match("^_design/oai-pmh-", row.key) != None and "views" in row.doc and len(row.doc["views"].keys()) > 0:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                view_name = "{0}/_view/{1}".format( row.key, row.doc["views"].keys()[0])
                log.error("Indexing: {0}".format( view_name))
                self.db.view(view_name, limit=1, descending=True)
            else:
                log.error("Not Indexing: {0}".format( row.key))
        
        
    @classmethod       
    def tearDownClass(self):
        global test_data_delete
        log.info ("Tearing Down Test")
        if test_data_delete == True:
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
    
    
    def parse_response(self, response):
        body = response.body
        xmlcontent = etree.fromstring(body)
        
        return { "raw": body, "etree": xmlcontent }
    
    def validate_lr_oai_etree(self, xmlcontent, errorExists=False, checkSchema=False, errorCodeExpected=None):
        
        error = xmlcontent.xpath("//*[local-name()='error']", namespaces=namespaces)
        if errorExists == False:
            if len(error) > 0:
                self.assertEqual(0, len(error), "validate_lr_oai_etree FAIL: Error code:{0} mesg:{1}".format(error[0].xpath("@code", namespaces=namespaces)[0], error[0].xpath("text()", namespaces=namespaces)[0]))
        elif errorExists and errorCodeExpected != None:
            codeReceived = error[0].xpath("@code", namespaces=namespaces)[0]
            if errorCodeExpected != codeReceived:
                self.assertEqual(0, len(error), "validate_lr_oai_etree FAIL: Expected:{2}, Got Error code:{0} mesg:{1}".format(error[0].xpath("@code", namespaces=namespaces)[0], error[0].xpath("text()", namespaces=namespaces)[0], errorCodeExpected))
        else:
            self.assertEqual(1, len(error), "validate_lr_oai_etree FAIL: Expected error, none found.")
        
        
        
        
    def validate_lr_oai_response(self, response, errorExists=False, checkSchema=False, errorCodeExpected=None):
        obj = self.parse_response(response)
        xmlcontent = obj["etree"]
        self.validate_lr_oai_etree(xmlcontent, errorExists, checkSchema, errorCodeExpected)

        schemaErrors = self.validator.validate(obj["raw"])
        assert len(schemaErrors) == 0, "validate_lr_oai_response: Schema validation error:\n%s" % '\n'.join(map(lambda x: "\t(line: {0}, char: {1}): {2}".format(x["line"], x["char"], x["msg"]), schemaErrors))
        
        


    def test_empty(self):
            pass
    
#    @unittest.skip("lxml/libxml can't load XMLSchema!!!")
    def test_get_oai_lr_schema(self):
        try:
#            res = urllib2.urlopen("http://www.w3.org/2001/XMLSchema.xsd")
#            xmlSchema = etree.XMLSchema(etree.parse(res))
#    #        xmlSchema = etree.XMLSchema(etree.parse(StringIO(res.read().strip())))
#            
#            res2 = self.app.get("/schemas/OAI/2.0/OAI-PMH-LR.xsd")
#            oaiLRSchema = etree.fromstring(res2.body)
            
            res2 = self.app.get("/schemas/OAI/2.0/OAI-PMH-LR.xsd")
            schemaErrors = self.validator.validate(res2.body)
            assert len(schemaErrors) == 0, "Schema validation error:\n%s" % '\n'.join(map(lambda x: "\t(line: {0}, char: {1}): {2}".format(x["line"], x["char"], x["msg"]), schemaErrors))

            
#            assert xmlSchema.validate(oaiLRSchema)
            log.info("test_get_oai_lr_schema: pass")
        except Exception as e:
            test_data_delete = False
            raise e
        
        
    def test_identify_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'Identify'})
        self.validate_lr_oai_response(response)
        log.info("test_identify_get: pass")
        
    def test_identify_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        self.validate_lr_oai_response(response)
        log.info("test_identify_post: pass")
        
    def test_identify_earliest_datestamp(self):
        '''test_identify_earliest_datestamp: 
        verify that the network node maintains a value for the earliest publication 
        time for documents harvestable from the node (earliestDatestamp)'''
        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        
        root = etree.fromstring(response.body)
        earliestDatestamp = root.xpath('/lr:OAI-PMH/lr:Identify/oai:earliestDatestamp/text()', namespaces=namespaces)
        
        assert len(earliestDatestamp) == 1, "Identify: missing earliest datestamp"
        
        try:
            earliest_datestamp = iso8601.parse_date(earliestDatestamp[0])
        except ParseError:
            self.fail("Identify: earliestDatestamp does not parse as iso8601")
        
        log.info("test_identify_earliest_datestamp: pass")
        
    def test_identify_timestamp_granularity(self):
        '''test_identify_timestamp_granularity: 
        verify that the granularity of the timestamp exists in Identify.'''

        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        
        root = etree.fromstring(response.body)
        identifyGranularity = root.xpath('/lr:OAI-PMH/lr:Identify/oai:granularity/text()', namespaces=namespaces)
        
        assert len(identifyGranularity) == 1, "Identify: missing <granularity>"
        
        log.error("test_identify_timestamp_granularity: pass")
        

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
        
        root = etree.fromstring(response.body)
        identifyGranularity = root.xpath('/lr:OAI-PMH/lr:Identify/oai:granularity/text()', namespaces=namespaces)
        
        assert len(identifyGranularity) == 1, "Identify: missing <granularity>"
        
        assert identifyGranularity[0] == granularity, "Identify: <granularity> does not match service document setting."
        
        log.info("test_identify_timestamp_granularity_service_doc: pass")
        
        
    def test_ListSets_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'ListSets'})
        self.validate_lr_oai_response(response, errorExists=True, errorCodeExpected="noSetHierarchy")
        log.info("test_ListSets_get: pass")
        
    def test_ListSets_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'ListSets'})
        self.validate_lr_oai_response(response, errorExists=True, errorCodeExpected="noSetHierarchy")
        log.info("test_ListSets_post: pass")
        
        
        
    def test_listMetadataFormats_with_doc_id_identifier_get(self):
        '''test_listMetadataFormats_with_doc_id_identifier_get: 
        verify that if an identifier is provided, the metadata formats are 
        returned only for the identified resource data description documents.'''
        global sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': 'true'})
        try:
            obj = self.parse_response(response)
            
            metadataPrefixes = obj["etree"].xpath("/lr:OAI-PMH/lr:ListMetadataFormats/oai:metadataFormat/oai:metadataPrefix/text()", namespaces=namespaces)
            assert len(metadataPrefixes) == len(randomDoc["payload_schema"]), "test_listMetadataFormats_with_doc_id_identifier_get: the count of payload_schema does not match the number of metadataPrefixes"
            
            for prefix in metadataPrefixes:
                assert prefix in randomDoc["payload_schema"], "test_listMetadataFormats_with_doc_id_identifier_get: metadataPrefix returned that does not exist in payload_schema. %s not in %s" % (prefix, ", ".join(metadataPrefixes))
                
        except Exception as e:
#            log.error("test_listMetadataFormats_get: fail")
            log.exception("test_listMetadataFormats_with_doc_id_identifier_get: fail")
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listMetadataFormats_with_doc_id_identifier_get: pass")
        
    def test_listMetadataFormats_with_resource_id_identifier_get(self):
        '''test_listMetadataFormats_with_resource_id_identifier_get: 
        verify that if an identifier is provided, the metadata formats are 
        returned only for the identified resource data description documents.'''
        global sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        
        # all docs that have the same resource_locator
        opts = {"key": ["by_resource_locator", randomDoc["resource_locator"]], 
                "include_docs": "true"}
        all_matching_docs = self.db.view("oai-pmh-get-records/docs", **opts)
        schema_formats = []
        for row in all_matching_docs.rows:
            if "payload_schema" in row.doc:
                for s in row.doc["payload_schema"]:
                    if s.strip() not in schema_formats:
                        schema_formats.append(s.strip())
            
        
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats', 'identifier': randomDoc["resource_locator"], 'by_doc_ID': 'false'})
        try:
            obj = self.parse_response(response)
            
            metadataPrefixes = obj["etree"].xpath("/lr:OAI-PMH/lr:ListMetadataFormats/oai:metadataFormat/oai:metadataPrefix/text()", namespaces=namespaces)
            assert len(metadataPrefixes) == len(schema_formats), "test_listMetadataFormats_with_resource_id_identifier_get: the count of payload_schema does not match the number of metadataPrefixes"
            
            for prefix in metadataPrefixes:
                assert prefix in schema_formats, "test_listMetadataFormats_with_resource_id_identifier_get: metadataPrefix returned that does not exist in payload_schema. %s not in %s" % (prefix, ", ".join(metadataPrefixes))
                
        except Exception as e:
#            log.error("test_listMetadataFormats_get: fail")
            log.exception("test_listMetadataFormats_with_resource_id_identifier_get: fail")
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listMetadataFormats_with_resource_id_identifier_get: pass")
        
        
    def test_listMetadataFormats_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listMetadataFormats_get: fail")
            log.exception("test_listMetadataFormats_get: fail")
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listMetadataFormats_get: pass")
        
    def test_listMetadataFormats_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listMetadataFormats_post: fail")
            log.exception("test_listMetadataFormats_post: fail")
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listMetadataFormats_post: pass")
    
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
        tree = etree.fromstring(response.body)
        
        metadata = tree.xpath("//oai_dc:dc", namespaces=namespaces)
        
        if len(metadata) != 1:
            self.fail("test_namespaceDeclarations: fail - Missing Metadata")
        else:
            for meta in metadata:
                log.info("test_namespaceDeclarations medatdada: prefix:{0} name:{1}".format(meta.prefix, meta.tag))
                pat = "<oai_dc:dc[^>]*\sxmlns:{0}=".format(meta.prefix)
                self.assertTrue(str(re.match(pat, etree.tostring(meta), flags=re.MULTILINE)!=None), "test_namespaceDeclarations: fail - namespace declaration not present")
        


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
        try:
            obj = self.parse_response(response)           
            
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
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_match_requested_dissemination_get: pass")

    
    def test_getRecord_by_doc_ID_JSON_metadataPrefix_get(self):
        '''test_getRecord_by_doc_ID_JSON_metadataPrefix_get: 
        verify that if the requested dissemination format in metadataPrefix 
        matches the JSON metadataPrefix in the servcie description the service 
        behaves as the basic harvest service (returns the complete resource data 
        description document as JSON).'''
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'LR_JSON_0.10.0', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            json_obj = json.loads(response.body)
            
            assert len(json_obj["getrecord"]["record"]) == 1, "test_getRecord_by_doc_ID_JSON_metadataPrefix_get: No JSON record returned"
            assert json_obj["getrecord"]["record"][0]["resource_data"] == randomDoc, "test_getRecord_by_doc_ID_JSON_metadataPrefix_get: Returned document does not match."
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_by_doc_ID_JSON_metadataPrefix_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_doc_ID_JSON_metadataPrefix_get: pass")
        
        
    def test_getRecord_by_doc_ID_get(self):
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_doc_ID_get: pass")
        
    def test_getRecord_by_doc_ID_post(self):
        global nsdl_data, sorted_dc_data
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.post("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_post: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_getRecord_by_doc_ID_post: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_doc_ID_post: pass")
        
    def test_getRecord_by_resource_ID_get(self):
        global nsdl_data, sorted_dc_data, test_data_delete
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["resource_locator"], 'by_resource_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except AssertionError:
            log.exception("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            test_data_delete = False
            raise
        except Exception as e:
#            log.error("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            log.exception("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_resource_ID_get: pass")
        
    def test_getRecord_by_resource_ID_post(self):
        global nsdl_data, sorted_dc_data, test_data_delete
        randomDoc = choice(sorted_dc_data["documents"])
        response = self.app.post("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["resource_locator"], 'by_resource_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except AssertionError:
            log.exception("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            test_data_delete = False
            raise
        except Exception as e:
#            log.error("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            log.exception("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_resource_ID_post: pass")


    def test_listRecords_post(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.post("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listRecords_post: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_post: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_post: pass")
        
    def test_listRecords_match_requested_disseminaton_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            obj = self.parse_response(response)
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
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_match_requested_disseminaton_get: pass")

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
        try:
            obj = self.parse_response(response)
            
            errors = obj["etree"].xpath("/lr:OAI-PMH//lr:error/@code", namespaces=namespaces)
            
            assert len(errors) > 0, "test_listRecords_noRecordsMatch_get: Expected at least one error to be returned in response."
            
            noRecordsMatch = False
            for error in errors:
                if error == 'noRecordsMatch': noRecordsMatch = True
                
            assert noRecordsMatch, "test_listRecords_noRecordsMatch_get: noRecordsMatch error was not returned; instead got: %s" % ', '.join(errors)
            
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_noRecordsMatch_get: fail - from: {0}".format(from_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_noRecordsMatch_get: pass")
    
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

        try:
            json_obj = json.load(response)
            
            assert len(json_obj["listrecords"]["record"]) > 0, "test_listRecords_JSON_metadataPrefix_get: No JSON records returned"
            for record in json_obj["listrecords"]["record"]:
                try:
                    doc_idx = sorted_nsdl_data["ids"].index(record[record["doc_ID"]])
                    assert sorted_nsdl_data["documents"][doc_idx] == record, "test_listRecords_JSON_metadataPrefix_get: Returned document does not match."
                except:
                    pass # This should be okay - result may be an element not inserted by the test.
        except Exception as e:
#            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            log.exception("test_listRecords_JSON_metadataPrefix_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_JSON_metadataPrefix_get: pass")
    
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
            try:
                obj = self.parse_response(response)
                resumptionToken = obj["etree"].xpath("/lr:OAI-PMH/lr:ListRecords/oai:resumptionToken/text()", namespaces=namespaces)
                
                assert len(resumptionToken) == 1, "test_listRecords_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken)
                
                response2 = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_, 'resumptionToken': resumptionToken[0]})
                obj2 = self.parse_response(response2)
                
                resumptionToken2 = obj2["etree"].xpath("/lr:OAI-PMH/lr:ListRecords/oai:resumptionToken", namespaces=namespaces)
                
                assert len(resumptionToken2) == 1, "test_listRecords_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken2)
                assert resumptionToken2[0].text == None or resumptionToken2[0].text == "", "test_listRecords_flow_control_get: expected last resumptionToken got '%s'" % resumptionToken2[0].text
                
            except Exception as e:
    #            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
                log.exception("test_listRecords_flow_control_get: fail - from: {0} until: {1}".format(from_, until_))
                global test_data_delete
                test_data_delete = False
                raise e
            log.info("test_listRecords_flow_control_get: pass")
        finally:
            service_doc_copy = node_db[service_doc_copy.id]
            service_doc_copy["service_data"] = service_doc_org["service_data"]
            node_db[service_doc_copy.id] = service_doc_copy
    
    def test_listRecords_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_get: pass")

        
        
    def test_listIdentifiers_post(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.post("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listIdentifiers_post: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_post: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listIdentifiers_post: pass")
        
    def test_listIdentifiers_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
#            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listIdentifiers_get: pass")
        
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
            try:
                obj = self.parse_response(response)
                resumptionToken = obj["etree"].xpath("/lr:OAI-PMH/lr:ListIdentifiers/oai:resumptionToken/text()", namespaces=namespaces)
                
                assert len(resumptionToken) == 1, "test_listIdentifiers_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken)
                
                response2 = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_, 'resumptionToken': resumptionToken[0]})
                obj2 = self.parse_response(response2)
                
                resumptionToken2 = obj2["etree"].xpath("/lr:OAI-PMH/lr:ListIdentifiers/oai:resumptionToken", namespaces=namespaces)
                
                assert len(resumptionToken2) == 1, "test_listIdentifiers_flow_control_get: Expected 1 resumption token, got %s." % len(resumptionToken2)
                assert resumptionToken2[0].text == None or resumptionToken2[0].text == "", "test_listIdentifiers_flow_control_get: expected last resumptionToken got '%s'" % resumptionToken2[0].text
                
            except Exception as e:
    #            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
                log.exception("test_listIdentifiers_flow_control_get: fail - from: {0} until: {1}".format(from_, until_))
                global test_data_delete
                test_data_delete = False
                raise e
            log.info("test_listIdentifiers_flow_control_get: pass")
        finally:
            service_doc_copy = node_db[service_doc_copy.id]
            service_doc_copy["service_data"] = service_doc_org["service_data"]
            node_db[service_doc_copy.id] = service_doc_copy
        
    def test_listIdentifiers_timestamp_headers_match_response_get(self):
        global sorted_nsdl_data, dc_data
        doc1 = choice(sorted_nsdl_data["documents"])
        doc2 = choice(sorted_nsdl_data["documents"])
        
        (from_, until_) = self._get_timestamps(doc1, doc2)
        
        from_tstamp = iso8601.parse_date(from_)
        until_tstamp = iso8601.parse_date(until_)
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            obj = self.parse_response(response)
            
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
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listIdentifiers_timestamp_headers_match_response_get: pass")
        

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
        try:
            obj = self.parse_response(response)
            
            errors = obj["etree"].xpath("/lr:OAI-PMH//lr:error/@code", namespaces=namespaces)
            
            assert len(errors) > 0, "test_listIdentifiers_noRecordsMatch_get: Expected at least one error to be returned in response."
            
            noRecordsMatch = False
            for error in errors:
                if error == 'noRecordsMatch': noRecordsMatch = True
                
            assert noRecordsMatch, "test_listIdentifiers_noRecordsMatch_get: noRecordsMatch error was not returned; instead got: %s" % ', '.join(errors)
            
        except Exception as e:
#            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            log.exception("test_listIdentifiers_noRecordsMatch_get: fail - from: {0}".format(from_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listIdentifiers_noRecordsMatch_get: pass")

#    def test_index(self):
#        response = self.app.get(url('OAI-PMH'))
#        # Test response...
#
#    def test_GET(self):
#        response = self.app.get(url('formatted_OAI-PMH', format='xml'))
#
#    def test_POST(self):
#        response = self.app.post(url('OAI-PMH'))

###############################

#    def test_getRecord(self):
#        tree = self._server.getRecord(
#            metadataPrefix='oai_dc', identifier='hdl:1765/315')
#        self.assert_(oaischema.validate(tree))
#        
#    def test_identify(self):
#        tree = self._server.identify()
#        self.assert_(oaischema.validate(tree))
#
#    def test_listIdentifiers(self):
#        tree = self._server.listIdentifiers(
#            from_=datetime(2003, 4, 10),
#            metadataPrefix='oai_dc')
#        self.assert_(oaischema.validate(tree))
#        
#    def test_listMetadataFormats(self):
#        tree = self._server.listMetadataFormats()
#        self.assert_(oaischema.validate(tree))
#
#    def test_listRecords(self):
#        tree = self._server.listRecords(
#            from_=datetime(2003, 4, 10),
#            metadataPrefix='oai_dc')
#        self.assert_(oaischema.validate(tree))
#
#    def test_listSets(self):
#        tree = self._server.listSets()
#        self.assert_(oaischema.validate(tree))
#
#    def test_namespaceDeclarations(self):
#        # according to the spec, all namespace used in the metadata
#        # element should be declared on the metadata element,
#        # and not on root or ancestor elements (big sigh..)
#        # this works, except for the xsi namespace which is allready declared
#        # on the root element, which means lxml will not declare it again on
#        # the metadata element
#
#        tree = self._server.getRecord(
#            metadataPrefix='oai_dc', identifier='hdl:1765/315')
#        # ugly xml manipulation, this is probably why the requirement is in
#        # the spec (yuck!)
#        xml = etree.tostring(tree)
#        xml = xml.split('<metadata>')[-1].split('</metadata>')[0]
#        first_el = xml.split('>')[0]
#        self.assertTrue(first_el.startswith('<oai_dc:dc'))
#        self.assertTrue(
#            'xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"'
#            in first_el) 
#        self.assertTrue(
#            'xmlns:dc="http://purl.org/dc/elements/1.1/"'
#            in first_el)
