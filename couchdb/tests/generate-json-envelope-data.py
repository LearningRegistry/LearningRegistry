'''
simple generator to build some sample envelopes for testing publish

Created on Feb 2, 2011

@author: jklo
'''

from __future__ import print_function
import datetime
import json

class DocumentRequest:
    def __init__(self, **kwargs):
        self.documents = kwargs.get('documents')
    
    def json(self):
        return json.dumps( { "documents": self.documents } )
    
    @property
    def documents(self):
        return self._documents
    
    @documents.setter
    def documents(self, docs):
        self._documents = docs
    
    @documents.deleter
    def documents(self):
        del self._documents
    
class Document:
    def __init__(self, kwargs={}):
        self._props = dict()
        self._props["envelope_ID"] = kwargs["ID"]
        self._props["envelope_resource_metadata_url"] = kwargs["metadata-url"]
        self._props["envelope_date_created"] = kwargs["date-created"]
        self._props["envelope_creator"] = kwargs["creator"]
        self._props["envelope_TTL"] = kwargs["TTL"]
        self._props["terms_of_service"] = kwargs["terms-of-service"]
        self._props["terms_of_service"] = kwargs["terms-of-service-url"]
        
    def json(self):
        return json.dumps(self._props)
    
    def document(self):
        return self._props
            
        

def main():
    
    import uuid
    
    docRequest = DocumentRequest()
    documents = []
    for i in range(25):
        uidstr = str(uuid.uuid1())
        doc = Document({"ID": "%d-%s" % (i, uidstr), 
                        "metadata-url": "http://example.com/uid/%d/%s" % (i, uidstr),
                        "date-created": str(datetime.datetime.now()),
                        "creator": "Jim Klo",
                        "TTL": 30,
                        "terms-of-service": False,
                        "terms-of-service-url": ""})
        print(doc.json())
        documents.append(doc.document())
    docRequest.documents = documents
    outfile = open('sample-envelope.json', 'w')
    jsonStr = docRequest.json()
    print(docRequest.json(), file=outfile, end='')
    outfile.close()
        
    


if __name__ == '__main__': main()