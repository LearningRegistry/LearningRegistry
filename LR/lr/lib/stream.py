'''
Copyright 2011 SRI International

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on Aug 12, 2011

@author: jklo
'''
import abc
import json
import logging
import types

log = logging.getLogger(__name__)

class CouchDBDocProcessor():
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def process(self, doc):
        """Process a single CouchDB document"""
        return

class StreamingCouchDBDocHandler():
    def __init__(self, documentHandler=None):
        self.docHandler = documentHandler
    
    def parse(self, instream):
        from ijson import items
        
        docs = items(instream, 'rows.item')
        count = 0
        for doc in docs:
            count += 1
            if self.docHandler != None and isinstance(self.docHandler, types.FunctionType):
                self.docHandler(doc)
            elif self.docHandler != None and isinstance(self.docHandler, CouchDBDocProcessor):
                self.docHandler.process(doc)
    
            log.debug("DOC: %s" %(json.dumps(doc)))
        
        return count
