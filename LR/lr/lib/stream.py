'''
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
