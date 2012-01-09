'''
Created on Jun 12, 2011

@author: jklo
'''
import unittest
import argparse
import sys
import json, urllib2


doc_ID = None
resource_ID = None
gpgbin = None
node_URL = None


class Test(unittest.TestCase):
    def __init__(self, testName):
        super(Test, self).__init__(testName)

    def setUp(self):
        assert doc_ID is not None, "doc_ID must be specified"
        assert resource_ID is not None, "resource_ID must be specified"


    def tearDown(self):
        pass

    def test_getrecord_validate_digital_signature(self):        
        request = urllib2.Request("{0}/harvest/getrecord?by_doc_ID=True&request_id={1}".format(node_URL, doc_ID), headers={'content-type': 'application/json; charset=utf-8'})
        response = urllib2.urlopen(request)
#        response = self.app.get(url('harvest', id='getrecord',request_id=doc_ID, by_doc_ID=True))
        data = self.validate_getrecord_response_base(response)
        for doc in data['getrecord']['record']:
            assert doc.has_key('resource_data')
            assert doc['resource_data']['_id'] == doc_ID
            print json.dumps(doc, indent=4, sort_keys=True)
            self.validate_digital_signature(doc['resource_data'])
    
    def validate_getrecord_response_base(self, response):
        data = json.loads(response.read())   
        assert data.has_key('OK') and data['OK']
        assert data.has_key('request')
        assert data['request'].has_key('verb') and data['request']['verb'] == 'getrecord'
        assert data.has_key('getrecord')
        return data
            
    def validate_digital_signature(self, doc):
        from LRSignature.verify.Verify import Verify_0_21
        from LRSignature import util
        from LRSignature import errors
        
        verifytool = Verify_0_21(gpgbin=gpgbin)
        try:
            verified = verifytool.verify(doc)
            
            assert verified == True, "Signature did not validate for document."
        except errors.MissingPublicKey:
            
            locations = doc['digital_signature']['key_location']
            numImported = 0
            for location in locations:
                rawKeys = util.fetchkeys(location)
                for rawKey in rawKeys:
                    numImported += util.storekey(self.sampleKey, gpgbin=gpgbin)
                if numImported > 0:
                    break
                
            assert numImported > 0, "No new public keys were imported, but were needed"
            
            try:
                verified = verifytool.verify(doc)
            
                assert verified == True, "Signature did not validate for document."
            
            except errors.MissingPublicKey:
                raise AssertionError("No public key available that can be retrieved to validate doc")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    
    parser = argparse.ArgumentParser(description="Test digital signatures upon harvest")
    parser.add_argument("--doc_ID", help="Envelope document ID for harvesting", default=None)
    parser.add_argument("--resource_ID", help="Resource locator url for harvesting", default=None)
    parser.add_argument("--gpgbin", help="Resource locator url for harvesting", default="gpg")
    parser.add_argument("--node_URL", help="URL of LR Node", default="http://localhost")
    args = parser.parse_args()
    
    
    doc_ID = args.doc_ID
    resource_ID = args.resource_ID
    gpgbin = args.gpgbin
    node_URL = args.node_URL
    
    suite = unittest.TestSuite()
    suite.addTest(Test("test_getrecord_validate_digital_signature"))
    
    unittest.TextTestRunner().run(suite)
#    unittest.main()