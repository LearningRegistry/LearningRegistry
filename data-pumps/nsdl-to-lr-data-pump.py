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
import os
'''
Reads OAI-PMH data and publishes to specific LR Node with envelopes that contain inline payloads.

Can work with both OAI Dublin Core and NSDL Dublin Core.

Created on Feb 11, 2011

@author: jklo
'''


from restkit.resource import Resource
import urllib2
import time
from lxml import etree
from StringIO import StringIO
import json
import logging
import sys
from urllib import urlencode
from optparse import OptionParser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

#config = {
#    "server": "http://memory.loc.gov",
#    "path": "/cgi-bin/oai2_0",
#    "verb": "ListRecords",
#    "metadataPrefix":"oai_dc",
#    "set":None,
#    "tos": "http://www.learningregistry.org/tos/cc-by-3-0/v0-5/",
#    "attribution": "The Library of Congress"
#}

config = {
    "server": "http://www.dls.ucar.edu",
    "path": "/dds_se/services/oai2-0",
    "verb": "ListRecords",
    "metadataPrefix":"nsdl_dc",
    "set":"ncs-NSDL-COLLECTION-000-003-112-016",
    "tos": "http://nsdl.org/help/?pager=termsofuse",
    "attribution": "The National Science Digital Library"
}
#config = {
#    "server": "http://hal.archives-ouvertes.fr",
#    "path": "/oai/oai.php",
#    "verb": "ListRecords",
#    "metadataPrefix":"oai_dc",
#    "set": None
#}
namespaces = {
              "oai" : "http://www.openarchives.org/OAI/2.0/",
              "oai_dc" : "http://www.openarchives.org/OAI/2.0/oai_dc/",
              "dc":"http://purl.org/dc/elements/1.1/",
              "dct":"http://purl.org/dc/terms/",
              "nsdl_dc":"http://ns.nsdl.org/nsdl_dc_v1.02/",
              "ieee":"http://www.ieee.org/xsd/LOMv1p0",
              "xsi":"http://www.w3.org/2001/XMLSchema-instance"
              }
# http://hal.archives-ouvertes.fr/oai/oai.php?verb=ListRecords&metadataPrefix=oai_dc

class Error(Exception):
    pass

def getDocTemplate():
    return { 
            "doc_type": "resource_data", 
            "doc_version": "0.11.0", 
            "resource_data_type" : "metadata",
            "active" : True,
            "submitter_type": "agent",
            "submitter": "NSDL 2 LR Data Pump",
            "TOS": {
                    "submission_TOS":    config["tos"],
                    "submission_attribution":  config["attribution"]
            },
            "resource_locator": None,
            "keys": [],
            "payload_placement": None,
            "payload_schema": [],
            "payload_schema_locator":None,
            "payload_locator": None,
            "resource_data": None
            }
    

def formatOAIDoc(record):
    doc = getDocTemplate()
    resource_locator = record.xpath("oai:metadata/oai_dc:dc/dc:identifier/text()", namespaces=namespaces)
    
    if resource_locator == None or len(resource_locator) == 0:
        return None
    
    subject = record.xpath("oai:metadata/oai_dc:dc/dc:subject/text()", namespaces=namespaces)
    language = record.xpath("oai:metadata/oai_dc:dc/dc:language/text()", namespaces=namespaces)
    payload = record.xpath("oai:metadata/oai_dc:dc", namespaces=namespaces)
    
    doc["resource_locator"] = resource_locator[0]
    
    doc["keys"].extend(subject)
    doc["keys"].extend(language)

    
    doc["payload_schema"].append("oai_dc")
    doc["payload_schema_locator"] = "http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
    
    doc["payload_placement"] = "inline"
    doc["resource_data"] = etree.tostring(payload[0])
    
    for key in doc.keys():
        if (doc[key] == None):
            del doc[key]
    
    return doc

def formatNSDLDoc(record):
    doc = getDocTemplate()
    resource_locator = record.xpath("oai:metadata/nsdl_dc:nsdl_dc/dc:identifier/text()", namespaces=namespaces)
    
    if resource_locator == None or len(resource_locator) == 0:
        return None
    
    subject = record.xpath("oai:metadata/nsdl_dc:nsdl_dc/dc:subject/text()", namespaces=namespaces)
    language = record.xpath("oai:metadata/nsdl_dc:nsdl_dc/dc:language/text()", namespaces=namespaces)
    edLevel = record.xpath("oai:metadata/nsdl_dc:nsdl_dc/dct:educationLevel/text()", namespaces=namespaces)
    payload = record.xpath("oai:metadata/nsdl_dc:nsdl_dc", namespaces=namespaces)
    
    doc["resource_locator"] = resource_locator[0]
    
    doc["keys"].extend(subject)
    doc["keys"].extend(language)
    doc["keys"].extend(edLevel)
    
    
    doc["payload_schema"].append("nsdl_dc")
    doc["payload_schema_locator"] = "http://ns.nsdl.org/nsdl_dc_v1.02/ http://ns.nsdl.org/schemas/nsdl_dc/nsdl_dc_v1.02.xsd"
    
    doc["payload_placement"] = "inline"
    doc["resource_data"] = etree.tostring(payload[0])
    
    for key in doc.keys():
        if (doc[key] == None):
            del doc[key]
    
    return doc
    
def bulkUpdate(list, opts):
    '''
    Save to Learning Registry
    '''
    if len(list) > 0 and opts.OUTPUT == None:
        try:
            log.info("Learning Registry Node URL: '{0}'\n".format(opts.LEARNING_REGISTRY_URL))
            res = Resource(opts.LEARNING_REGISTRY_URL)
            body = { "documents":list }
            log.info("request body: %s" % (json.dumps(body),))
            clientResponse = res.post(path="/publish", payload=json.dumps(body), headers={"Content-Type":"application/json"})
            log.info("status: {0}  message: {1}".format(clientResponse.status_int, clientResponse.body_string()))
        except Exception:
            log.exception("Caught Exception When publishing to registry")
    else:
        log.info("Nothing is being updated.")


def filenum(start=0):
    i = start
    while 1:
        yield i
        i += 1

count = filenum(0)
        
def outputFile(list, opts):
    '''
    Save to file
    '''
    if len(list) > 0 and opts.OUTPUT != None:
        if not os.path.exists(opts.OUTPUT):
            os.makedirs(opts.OUTPUT)
        
        slice_idx = 0
        slice_chunksize = 100
        try:
            while len(list[slice_idx:slice_chunksize]) > 0:
                slice = list[slice_idx:slice_chunksize]
                
                filepath = "{0}/data-{1}.json".format(opts.OUTPUT, count.next())
                with open(filepath, "w") as out:
                    out.write(json.dumps({"documents":slice}))
                    log.info("wrote: {0}".format(out.name))
                
                slice_idx += 1
        except Exception:
            log.exception("Unable to write file.")

    

def fetchRecords(conf):
    '''
    Generator to fetch all records using a resumptionToken if supplied.
    '''
    server = conf["server"]
    path = conf["path"]
    verb = conf["verb"]
    metadataPrefix = conf["metadataPrefix"]
    set = conf["set"]
    
    params = { "verb": verb, "metadataPrefix": metadataPrefix }
    if set != None:
        params["set"] = set
    
    body = makeRequest("%s%s" % (server, path), **params)
    f = StringIO(body)
    tree = etree.parse(f)
    tokenList = tree.xpath("oai:ListRecords/oai:resumptionToken/text()", namespaces=namespaces)
    yield tree.xpath("oai:ListRecords/oai:record", namespaces=namespaces)
    
    del params["metadataPrefix"]
    
    while (len(tokenList) == 1):
        try:
            params["resumptionToken"] = tokenList[0]
            body = makeRequest("%s%s" % (server, path), **params)
            f = StringIO(body)
            tree = etree.parse(f)
            yield tree.xpath("oai:ListRecords/oai:record", namespaces=namespaces)
            tokenList = tree.xpath("oai:ListRecords/oai:resumptionToken/text()", namespaces=namespaces)
        except Exception as e:
            tokenList = []
            log.error(sys.exc_info())
            log.exception("Problem trying to get next segment.")

WAIT_DEFAULT = 120 # two minutes
WAIT_MAX = 5

def makeRequest(base_url, credentials=None, **kw):
        """Actually retrieve XML from the server.
        """
        # XXX include From header?
        headers = {'User-Agent': 'pyoai'}
        if credentials is not None:
            headers['Authorization'] = 'Basic ' + credentials.strip()
        request = urllib2.Request(
            base_url, data=urlencode(kw), headers=headers)
        return retrieveFromUrlWaiting(request)
        
def retrieveFromUrlWaiting(request,
                           wait_max=WAIT_MAX, wait_default=WAIT_DEFAULT):
    """Get text from URL, handling 503 Retry-After.
    """
    for i in range(wait_max):
        try:
            f = urllib2.urlopen(request)
            text = f.read()
            f.close()
            # we successfully opened without having to wait
            break
        except urllib2.HTTPError, e:
            if e.code == 503:
                try:
                    retryAfter = int(e.hdrs.get('Retry-After'))
                except TypeError:
                    retryAfter = None
                if retryAfter is None:
                    time.sleep(wait_default)
                else:
                    time.sleep(retryAfter)
            else:
                # reraise any other HTTP error
                raise
    else:
        raise Error, "Waited too often (more than %s times)" % wait_max
    return text            
      

def connect(opts):
    for recset in fetchRecords(config):
        docList = []
        for rec in recset:
            if config["metadataPrefix"] == "oai_dc":
                doc = formatOAIDoc(rec)
                if (doc != None):
                    docList.append(doc)
            if config["metadataPrefix"] == "nsdl_dc":
                doc = formatNSDLDoc(rec)
                if (doc != None):
                    docList.append(doc)
        try:
            print(json.dumps(docList))
        except:
            log.exception("Problem w/ JSON dump")
        bulkUpdate(docList, opts)
        outputFile(docList, opts)
       

    
class Opts:
    def __init__(self):
        self.LEARNING_REGISTRY_URL = "http://localhost"
        
        parser = OptionParser()
        parser.add_option('-u', '--url', dest="registryUrl", help='URL of the registry to push the data.', default=self.LEARNING_REGISTRY_URL)
        parser.add_option('-o', '--output', dest="output", help='Output file instead of publish', default=None)
        (options, args) = parser.parse_args()
        self.LEARNING_REGISTRY_URL = options.registryUrl    
        self.OUTPUT = options.output

       

if __name__ == '__main__':
    log.info("Update Started.")
    opts = Opts()
    connect(opts)
    log.info("Done Updating.")
