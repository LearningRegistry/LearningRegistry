'''
Created on Feb 23, 2011

@author: jklo
'''
import unittest
import logging
from stemx.tests import Publish



class ObtainTest(Publish):
    def __init__(self):
        self._log = logging.getLogger("ObtainTest");
        self._server = None
        pass

    def setUp(self):
       super(ObtainTest, self).setUp() 

        


    def tearDown(self):
        super(ObtainTest, self).tearDown()


    def testObtain(self):
        doc_ID = self.test_goodPublish()
        self._res


if __name__ == "__main__":
    logging.basicConfig()
    #import sys;sys.argv = ['', 'ObtainTest.testObtain']
    unittest.main()