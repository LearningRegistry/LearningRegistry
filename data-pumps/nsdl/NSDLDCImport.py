'''
Created on Feb 4, 2011

@author: jklo
'''

import nsdl
import sys
from oaipmh.client import Client
#from oaipmh.common import Identify, Metadata, Header
from oaipmh.metadata import MetadataRegistry, MetadataReader

class NSDLDCImport(object):
    '''
    Class exports the required fields from the UCAR OAI-PMH data repository using NSDL_DC.
    '''


    def __init__(self, url, prefix=nsdl.LR_NSDL_PREFIX, reader=None, fields=None, namespaces=None, fieldMap=None):
        '''
        Constructor
        '''
        
        if fields == None:
            self._fields = nsdl.LR_NSDL_DC_FIELDS
        else:
            self._fields = fields
        
        if fieldMap == None:
            self._fieldMap = nsdl.NSDL_TO_LR_MAP
        else:
            self._fieldMap = fieldMap
        
        if namespaces == None:
            self._namespaces = nsdl.LR_NSDL_DC_NAMESPACES
        else:
            self._namespaces = namespaces
            
        if reader == None:
            reader = MetadataReader(fields = self._fields, namespaces = self._namespaces)
        
        self._url = url
        self._registry = MetadataRegistry()
        self._prefix = prefix
        self._registry.registerReader(prefix, reader)
        self._client = Client(url, self._registry)
    
    def _format(self, doc):
        value = {}
        # merge all the fields
        for (fieldname, fieldconfig) in self._fieldMap.items():
            if fieldconfig["type"] == "const" and "const" in fieldconfig:
                value[fieldname] = fieldconfig["const"]
            elif fieldconfig["type"] == "[string]" and len(fieldconfig["fields"]) > 0:
                value[fieldname] = []
                for field in fieldconfig["fields"]:
                    value[fieldname].extend(doc.getField(field))
            elif fieldconfig["type"] == "string" and len(fieldconfig["fields"]) > 0:
                value[fieldname] = ""
                for field in fieldconfig["fields"]:
                    value[fieldname] += ", ".join(doc.getField(field))
            elif fieldconfig["type"] == "boolean" and len(fieldconfig["fields"]) > 0:
                value[fieldname] = True
                for field in fieldconfig["fields"]:
                    value[fieldname] &= doc.getField(field)
        return value
    
    def fetch_documents(self, range=10000):
        
        return_stuff = []
        for record in self._client.listRecords(metadataPrefix=self._prefix):
            r = record[1]
            value = self._format(r)
            if value != None:
                return_stuff.append(value)
            if len(return_stuff) >= range:
                yield return_stuff     
                return_stuff = []
    
    

if __name__ == "__main__" :
    import json
    try:
        reader = MetadataReader(fields = nsdl.LR_NSDL_DC_FIELDS, namespaces = nsdl.LR_NSDL_DC_NAMESPACES)
        myImport = NSDLDCImport(nsdl.ALL_METADATA_URL_NSDL_DC, nsdl.LR_NSDL_PREFIX)
       
        for (mult, list) in enumerate(myImport.fetch_documents(range=100)):
            for (idx, item) in enumerate(list):
                print("%d: %s" % (idx, json.dumps(item)))
            list = myImport.fetch_documents(range=100)
    except:
        print(sys.exc_info())    
