'''
Using oaipmh python library to fetch data and insert as envelope.

*** OBSOLETE ***
    oaipmh library disposes of the raw xml. hence there's no way to create an inline envelope efficiently without requerying the OAI feed repeatedly.
    see: nsdl-to-lr-data-pump.py for updated version which does this without oaipmh library.

Created on Feb 4, 2011

@author: jklo
'''
import logging
from oaipmh.metadata import MetadataReader

from restkit.resource import Resource
from nsdl.NSDLDCImport import NSDLDCImport
import nsdl

if __name__ == '__main__':
    import json
    logging.basicConfig()
    log = logging.getLogger("main")
    reader = MetadataReader(fields = nsdl.LR_NSDL_DC_FIELDS, namespaces = nsdl.LR_NSDL_DC_NAMESPACES)
    myImport = NSDLDCImport(nsdl.ALL_METADATA_URL_NSDL_DC, nsdl.LR_NSDL_PREFIX)
   
    for (mult, list) in enumerate(myImport.fetch_documents(range=100)):
        # Just print this
#        for (idx, item) in enumerate(list):
#            print("%d: %s" % (idx, json.dumps(item)))
            
        #need to post to learning registry
        try:
            res = Resource("http://learningregistry.couchdb:5984")
            body = { "documents":list }
            log.info("request body: %s" % (json.dumps(body),))
            clientResponse = res.post(path="/publish", payload=json.dumps(body), headers={"Content-Type":"application/json"})
            log.info("status: {0}  message: {1}".format(clientResponse.status_int, clientResponse.body_string))
        except Exception as e:
            log.exception("Caught Exception")
        list = myImport.fetch_documents(range=100)