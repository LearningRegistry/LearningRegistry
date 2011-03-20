#!/usr/bin/python
'''
Created on Mar 15, 2011

@author: jklo
'''
import logging
import unittest
from lxml import etree
import urllib2
json_headers = {
                "Content-Type" : "application/json"
                }
xml_headers = {
                "Content-Type" : "text/xml"
                }


logging.basicConfig()
log = logging.getLogger(__name__)

class Test(unittest.TestCase):

    def setUp(self):
        
        self._parser = etree.XMLParser(resolve_entities=True)
        
        self._postServiceUrl = "http://localhost/OAI-PMH"
        self._queryServiceUrl = self._postServiceUrl+"?{0}"
        
        schema_file = file("../schemas/OAI/2.0/OAI-PMH.xsd", "r")
        schema_doc = etree.parse(schema_file)
        self._oaischema = etree.XMLSchema(schema_doc)

        schema_file = file("../schemas/OAI/2.0/OAI-PMH-LR.xsd", "r")
        schema_doc = etree.parse(schema_file)
        self._lrschema = etree.XMLSchema(schema_doc)
        
 #   @unittest.skip("Skip, can't validate nested schemas quite yet")
    def testGetRecordByDocID(self):
        query = self._queryServiceUrl.format("verb=GetRecord&by_doc_ID=true&metadataPrefix=nsdl_dc&identifier=5c1070a1c5cb4eda8d460cf9b004c22a")
        request = urllib2.Request(query, headers=xml_headers)
        response = urllib2.urlopen(request)
        body = response.read()
        response_doc = etree.fromstring(body, parser=self._parser)
        
        try:
            self._lrschema.assertValid(response_doc)
        except etree.DocumentInvalid as e:
            line = 1;
            for i in body.split("\n"):
                print "{0}\t{1}".format(line, i)
                line += 1
            self.fail(e.message)
    
#    @unittest.skip("Skip, can't validate nested schemas quite yet")
    def testGetRecordByResourceID(self):
        query = self._queryServiceUrl.format("verb=GetRecord&by_doc_ID=false&metadataPrefix=nsdl_dc&identifier=http://www.purplemath.com/modules/ratio.htm")
        request = urllib2.Request(query, headers=xml_headers)
        response = urllib2.urlopen(request)
        body = response.read()
        response_doc = etree.fromstring(body)
        
        try:
            self._lrschema.assertValid(response_doc)
        except etree.DocumentInvalid as e:
            line = 1;
            for i in body.split("\n"):
                print "{0}\t{1}".format(line, i)
                line += 1
            self.fail(query+'\n'+e.message)

#    @unittest.skip("Skip, can't validate nested schemas quite yet")
    def testListIdentifiers(self):
        query = self._queryServiceUrl.format("verb=ListIdentifiers&metadataPrefix=nsdl_dc")
        request = urllib2.Request(query, headers=xml_headers)
        try:
            response = urllib2.urlopen(request)
        except Exception as e:
            log.exception("Unable to open url: {0}".format(query))
            self.fail(e.message)
            
        body = response.read()
        response_doc = etree.fromstring(body)
        
        try:
            self._lrschema.assertValid(response_doc)
        except etree.DocumentInvalid as e:
            line = 1;
            for i in body.split("\n"):
                print "{0}\t{1}".format(line, i)
                line += 1
            self.fail(e.message)
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetRecordList']
    unittest.main()
