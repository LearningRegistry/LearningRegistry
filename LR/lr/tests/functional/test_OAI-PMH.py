from lr.tests import *
from pylons import config
import couchdb
from routes.util import url_for
import logging
import urllib2
from lxml import etree
from random import choice
import json
import uuid
import datetime
import re
from lr.lib.oaipmh import oaipmh

json_headers={'content-type': 'application/json'}

time_format = '%Y-%m-%d %H:%M:%S.%f'
log = logging.getLogger(__name__)



test_data_delete = True
nsdl_data = { "documents" : [] }
dc_data = { "documents" : [] }
class TestOaiPmhController(TestController):
    def setUp(self):

        schema_file = file("lr/public/schemas/OAI/2.0/OAI-PMH-LR.xsd", "r")
        schema_doc = etree.parse(schema_file)
        self.oailrschema = etree.XMLSchema(schema_doc)
        
        global test_data_delete, nsdl_data, dc_data
        self.o = oaipmh()
        self.server = self.o.server
        self.db = self.o.db
        
        view_data = self.db.view('oai-pmh/test-data')
        if (len(view_data) == 0):
            nsdl_data = json.load(file("lr/tests/data/nsdl_dc/data-0.json"))
            for doc in nsdl_data["documents"]:
                doc["doc_ID"] = "NSDL-TEST-DATA-"+str(uuid.uuid1())
            
            self.app.post('/publish', params=json.dumps(nsdl_data), headers=json_headers)
            
            dc_data = json.load(file("lr/tests/data/oai_dc/data-0.json"))
            for doc in dc_data["documents"]:
                doc["doc_ID"] = "OAI-DC-TEST-DATA-"+str(uuid.uuid1())
                
            self.app.post('/publish', params=json.dumps(dc_data), headers=json_headers)
            view_data = self.db.view('oai-pmh/test-data')
        
        nsdl_data = { "documents" : [] }
        dc_data = { "documents" : [] }
        for row in view_data:
            if re.search("^NSDL-TEST-DATA-", row.key) != None:
                nsdl_data["documents"].append(row.value)
            if re.search("^OAI-DC-TEST-DATA-", row.key) != None:
                dc_data["documents"].append(row.value)
        
            
    def tearDown(self):
        global test_data_delete
        
        if test_data_delete == True:
            for doc in nsdl_data["documents"]:
                del self.db[doc["_id"]]
            for doc in dc_data["documents"]:
                del self.db[doc["_id"]]
    
    def validate_lr_oai_response(self, response):
        xmlcontent = etree.fromstring(response.body)
        self.oailrschema.assertValid(xmlcontent)
        

    def test_get_oai_lr_schema(self):
        response = urllib2.urlopen("http://www.w3.org/2001/XMLSchema.xsd");
        xmlSchema = etree.XMLSchema(etree.fromstring(response.read()))
        
        response = self.app.get("/schemas/OAI/2.0/OAI-PMH-LR.xsd")
        oaiLRSchema = etree.fromstring(response.body)
        
        assert xmlSchema.validate(oaiLRSchema)
        log.info("test_get_oai_lr_schema: pass")
        
        
    def test_identify_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'Identify'})
        self.validate_lr_oai_response(response)
        log.info("test_identify_get: pass")
        
    def test_identify_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'Identify'})
        self.validate_lr_oai_response(response)
        log.info("test_identify_post: pass")
        
        
    def test_ListSets_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'ListSets'})
        self.validate_lr_oai_response(response)
        log.info("test_ListSets_get: pass")
        
    def test_ListSets_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'ListSets'})
        self.validate_lr_oai_response(response)
        log.info("test_ListSets_post: pass")
        
        
    def test_listMetadataFormats_get(self):
        response = self.app.get("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_listMetadataFormats_get: fail")
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listMetadataFormats_get: pass")
        
    def test_listMetadataFormats_post(self):
        response = self.app.post("/OAI-PMH", params={'verb': 'ListMetadataFormats'})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_listMetadataFormats_post: fail")
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listMetadataFormats_post: pass")
    

    def test_getRecord_by_doc_ID_get(self):
        global nsdl_data, dc_data
        randomDoc = choice(dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_getRecord_by_doc_ID_get: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_doc_ID_get: pass")
        
    def test_getRecord_by_doc_ID_post(self):
        global nsdl_data, dc_data
        randomDoc = choice(dc_data["documents"])
        response = self.app.post("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["doc_ID"], 'by_doc_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_getRecord_by_doc_ID_post: fail - identifier: {0}".format(randomDoc["doc_ID"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_doc_ID_post: pass")
        
    def test_getRecord_by_resource_ID_get(self):
        global nsdl_data, dc_data
        randomDoc = choice(dc_data["documents"])
        response = self.app.get("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["resource_locator"], 'by_resource_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_getRecord_by_resource_ID_get: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_resource_ID_get: pass")
        
    def test_getRecord_by_resource_ID_post(self):
        global nsdl_data, dc_data
        randomDoc = choice(dc_data["documents"])
        response = self.app.post("/OAI-PMH", params={'verb': 'GetRecord', 'metadataPrefix':'oai_dc', 'identifier': randomDoc["resource_locator"], 'by_resource_ID': True})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_getRecord_by_resource_ID_post: fail - identifier: {0}".format(randomDoc["resource_locator"]))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_getRecord_by_resource_ID_post: pass")


    def test_listRecords_post(self):
        global nsdl_data, dc_data
        doc1 = choice(nsdl_data["documents"])
        doc2 = choice(nsdl_data["documents"])
        
        if doc1["node_timestamp"] > doc2["node_timestamp"]:
            from_ =  doc1["node_timestamp"]
            until_ = doc2["node_timestamp"]
        else:
            until_ =  doc1["node_timestamp"]
            from_ = doc2["node_timestamp"]
            
        response = self.app.post("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_listRecords_post: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_post: pass")
        
    def test_listRecords_get(self):
        global nsdl_data, dc_data
        doc1 = choice(nsdl_data["documents"])
        doc2 = choice(nsdl_data["documents"])
        
        if doc1["node_timestamp"] > doc2["node_timestamp"]:
            from_ =  doc1["node_timestamp"]
            until_ = doc2["node_timestamp"]
        else:
            until_ =  doc1["node_timestamp"]
            from_ = doc2["node_timestamp"]
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListRecords', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_listRecords_get: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listRecords_get: pass")
        
        
    def test_listIdentifiers_post(self):
        global nsdl_data, dc_data
        doc1 = choice(nsdl_data["documents"])
        doc2 = choice(nsdl_data["documents"])
        
        if doc1["node_timestamp"] > doc2["node_timestamp"]:
            from_ =  doc1["node_timestamp"]
            until_ = doc2["node_timestamp"]
        else:
            until_ =  doc1["node_timestamp"]
            from_ = doc2["node_timestamp"]
            
        
        response = self.app.post("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_listIdentifiers_post: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listIdentifiers_post: pass")
        
    def test_listIdentifiers_get(self):
        global nsdl_data, dc_data
        doc1 = choice(nsdl_data["documents"])
        doc2 = choice(nsdl_data["documents"])
        
        if doc1["node_timestamp"] > doc2["node_timestamp"]:
            from_ =  doc1["node_timestamp"]
            until_ = doc2["node_timestamp"]
        else:
            until_ =  doc1["node_timestamp"]
            from_ = doc2["node_timestamp"]
            
            
        response = self.app.get("/OAI-PMH", params={'verb': 'ListIdentifiers', 'metadataPrefix': 'nsdl_dc', 'from': from_, 'until': until_})
        try:
            self.validate_lr_oai_response(response)
        except Exception as e:
            log.error("test_listIdentifiers_get: fail - from: {0} until: {1}".format(from_, until_))
            global test_data_delete
            test_data_delete = False
            raise e
        log.info("test_listIdentifiers_get: pass")


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
