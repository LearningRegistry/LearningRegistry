#    Copyright 2011 SRI International
#    
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    
#        http://www.apache.org/licenses/LICENSE-2.0
#    
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
'''
Created on Feb 23, 2011

@author: jklo
'''

import unittest
import json
from restkit.resource import Resource
import logging

class PublishTest(unittest.TestCase):


    def setUp(self):
        self._log = logging.getLogger("PublishTest")
        self._nodeURL = 'http://learningregistry.couchdb:5984'
        self._sampleGoodRDDDM = '{"doc_type":"resource_data","resource_data":"<nsdl_dc:nsdl_dc xmlns:dc=\\"http://purl.org/dc/elements/1.1/\\" xmlns:dct=\\"http://purl.org/dc/terms/\\" xmlns:ieee=\\"http://www.ieee.org/xsd/LOMv1p0\\" xmlns:nsdl_dc=\\"http://ns.nsdl.org/nsdl_dc_v1.02/\\" xmlns:xsi=\\"http://www.w3.org/2001/XMLSchema-instance\\" xmlns=\\"http://www.openarchives.org/OAI/2.0/\\" schemaVersion=\\"1.02.020\\" xsi:schemaLocation=\\"http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd\\">\\n    <dc:identifier xsi:type=\\"dct:URI\\">http://www.instructorweb.com/docs/pdf/convdistance.pdf</dc:identifier>\\n    <dc:title>Measurement: Converting Distances</dc:title>\\n    <dc:description>This lesson helps students understand and practice converting measurements in both English and metric systems. The 8-page pdf begins with a brief introduction to measuring length, English measurement systems, and metric measurement. Students then learn to convert measurements within each system. At the end of the lesson, there are 18 review problems for students to convert measurements on their own. Answers are provided.</dc:description>\\n    <dc:subject>convert, conversion</dc:subject>\\n    <dc:subject>Measurement</dc:subject>\\n    <dc:subject>Measurement</dc:subject>\\n    <dc:subject>Systems of measurement</dc:subject>\\n    <dc:subject>Measurement</dc:subject>\\n    <dc:subject>Systems of measurement</dc:subject>\\n    <dc:subject>English</dc:subject>\\n    <dc:subject>Measurement</dc:subject>\\n    <dc:subject>Systems of measurement</dc:subject>\\n    <dc:subject>Metric</dc:subject>\\n    <dc:language>en-US</dc:language>\\n    <dct:educationLevel xsi:type=\\"nsdl_dc:NSDLEdLevel\\">Elementary School</dct:educationLevel>\\n    <dct:educationLevel xsi:type=\\"nsdl_dc:NSDLEdLevel\\">Upper Elementary</dct:educationLevel>\\n    <dct:educationLevel xsi:type=\\"nsdl_dc:NSDLEdLevel\\">Grade 4</dct:educationLevel>\\n    <dc:type xsi:type=\\"nsdl_dc:NSDLType\\">Instructional Material</dc:type>\\n    <dc:type xsi:type=\\"nsdl_dc:NSDLType\\">Lesson/Lesson Plan</dc:type>\\n    <dc:type xsi:type=\\"nsdl_dc:NSDLType\\">Problem Set</dc:type>\\n    <dc:type xsi:type=\\"nsdl_dc:NSDLType\\">Student Guide</dc:type>\\n    <dct:audience xsi:type=\\"nsdl_dc:NSDLAudience\\">Learner</dct:audience>\\n    <dct:conformsTo>4.MD.1</dct:conformsTo>\\n    <dct:conformsTo>5.MD.1</dct:conformsTo>\\n    <dc:publisher>InstructorWeb</dc:publisher>\\n    <dc:rights>Copyright 2006 InstructorWeb</dc:rights>\\n    <dc:rights xsi:type=\\"dct:URI\\">http://www.instructorweb.com/terms.asp</dc:rights>\\n    <dct:accessRights xsi:type=\\"nsdl_dc:NSDLAccess\\">Free access with registration</dct:accessRights>\\n    <dc:format>application</dc:format>\\n    <dc:format>application/pdf</dc:format>\\n    <dc:date>2006</dc:date>\\n</nsdl_dc:nsdl_dc>\\n \\n    ","submitter_type":"agent","resource_data_type":"metadata","payload_schema_locator":["http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd"],"payload_placement":"inline","submitter":"NSDL 2 LR Data Pump","payload_schema":["NSDL DC 1.02.020"],"doc_version":"0.10.0","filtering_keys":["convert, conversion","Measurement","Measurement","Systems of measurement","Measurement","Systems of measurement","English","Measurement","Systems of measurement","Metric","en-US","Elementary School","Upper Elementary","Grade 4"],"active":true,"resource_locator":["http://www.instructorweb.com/docs/pdf/convdistance.pdf"],"submission_TOS":"Yes"}'
        
        self._res = Resource(uri=self._nodeURL)
        self._jsonHeaders = { "Content-Type": "application/json" }     
                 

    def tearDown(self):
        pass

 
    def test_goodPublish(self):
        
        jpay = json.loads(self._sampleGoodRDDDM, encoding="utf_8")
        docPayload = {"documents": [jpay]}
        
        self.assertNotEqual(None, docPayload, "No Document Payload")
        
        
        clientResponse = self._res.post(path="/publish", payload=json.dumps(docPayload), headers=self._jsonHeaders)
        
        self.assertNotEqual(None, clientResponse, "No Client Response")
        
        self.assertEqual(200, clientResponse.status_int, "Publish failed with an incorrect status code")
        
        bodyContent = clientResponse.body_string()
        
        self._log.info(type(bodyContent))
        self.assertNotEqual("",bodyContent, "Publish failed with an empty body response")
        
        docsPublished = json.loads(bodyContent)
        
        self.assertDictContainsSubset({ "OK": True }, docsPublished, "Global doc response of OK not True")
        self.assertTrue(docsPublished.has_key("document_results"), "document_results is missing")
        self.assertEqual(1, len(docsPublished["document_results"]), "unexpected number of results returned.")
        docRes = docsPublished["document_results"][0]
        self.assertEqual(True, (docRes.has_key("doc_ID") | docRes.has_key("OK")), "document missing required parameters")
        
        return docRes["doc_ID"]


if __name__ == "__main__":
    logging.basicConfig()
    #import sys;sys.argv = ['', 'PublishTest.test_goodPublish']
    unittest.main()