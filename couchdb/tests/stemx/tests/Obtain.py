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