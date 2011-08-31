'''
Created on Apr 1, 2011

@author: jklo
'''


import urllib, urllib2, json, hashlib, logging
from lxml import etree
from optparse import OptionParser
from mwlib.uparser import simpleparse
from mwlib.parser.nodes import *
from restkit.resource import Resource

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

namespaces = {
              "mw": "http://www.mediawiki.org/xml/export-0.4/"
            }


template = """<?xml version="1.0" encoding="UTF-8"?> 
<commParadata xsi:schemaLocation="http://ns.nsdl.org/ncs/comm_para http://ns.nsdl.org/ncs/comm_para/1.00/schemas/comm_para.xsd" xmlns="http://ns.nsdl.org/ncs/comm_para" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> 
    <recordId>{0}</recordId> 
    <paradataTitle>{1}</paradataTitle> 
    <usageDataReferenceURL>{2}</usageDataReferenceURL> 
    <usageDataResourceURL>{3}</usageDataResourceURL> 
    <usageDataSummary> 
        <integer type="recommended">{4}</integer> 
   </usageDataSummary> 
</commParadata>"""


class Opts:
    def __init__(self):
        self.LEARNING_REGISTRY_URL = "http://lrdev2.learningregistry.org"
        
        parser = OptionParser()
        parser.add_option('-u', '--url', dest="registryUrl", help='URL of the registry to push the data.', default=self.LEARNING_REGISTRY_URL)
        parser.add_option('-o', '--output', dest="output", help='Output file instead of publish', default=None)
        parser.add_option('-w', '--wiki', dest="wikiUrl", help='MediaWiki URL', default="http://heabiowiki.leeds.ac.uk/oerbital/")
        (options, args) = parser.parse_args()
        self.LEARNING_REGISTRY_URL = options.registryUrl    
        self.OUTPUT = options.output
        self.WIKI = options.wikiUrl

def getEnvelope(recordId, url, tstamp, attribution, paradata):
    return { 
            "doc_type": "resource_data", 
            "doc_version": "0.11.0", 
            "resource_data_type" : "paradata",
            "active" : True,
            "submitter_type": "agent",
            "submitter": "OERbital",
            "submitter_timestamp": tstamp,
            "TOS": {
                    "submission_TOS":    "http://creativecommons.org/licenses/by-nc-sa/2.0/uk/",
                    "submission_attribution":  attribution
            },
            "resource_locator": url,
            "keys": [ recordId ],
            "payload_placement": "inline",
            "payload_schema": [ "comm_para" ],
            "payload_schema_locator":"http://ns.nsdl.org/ncs/comm_para http://ns.nsdl.org/ncs/comm_para/1.00/schemas/comm_para.xsd",
#            "payload_locator": None,
            "resource_data": paradata
            }

def fetchUrls(parent):
    url = {}
    if parent != None:
        for child in parent.children:
            if isinstance(child, URL) or isinstance(child, NamedURL):
                if url.has_key(child.caption):
                    url[child.caption] += 1
                else:
                    url[child.caption] = 1
                
            childUrls = fetchUrls(child)
            for key in childUrls.keys():
                if url.has_key(key):
                    url[key] += childUrls[key]
                else:
                    url[key] = childUrls[key]
    return url

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


def exportUrl(pages="", opts=Opts()):
    req = urllib2.Request(opts.WIKI +"index.php", data="title=Special:Export&pages={0}".format(pages)) 
    res = urllib2.urlopen(req);
    body = res.read()
    
    doc = etree.fromstring(body)
    pagetitle = doc.xpath("//mw:mediawiki/mw:page/mw:title/text()", namespaces=namespaces)[0]
    revisions = doc.xpath("//mw:mediawiki/*/mw:revision", namespaces=namespaces)
    for rev in revisions:
        version = rev.xpath("mw:id/text()", namespaces=namespaces)[0]
        tstamp = rev.xpath("mw:timestamp/text()", namespaces=namespaces)[0]
        content = rev.xpath("mw:text/text()", namespaces=namespaces)[0]
        contrib = rev.xpath("mw:contributor/mw:username/text()", namespaces=namespaces)[0]
        
        struct = simpleparse(content)
        
        articleUrls = fetchUrls(struct)
        
        envelopeList = []
        for url in articleUrls.keys():
            recordId = "{0}-{1}".format(version, hashlib.sha1(url).hexdigest()) 
            refUrl = "{0}index.php/{1}".format(opts.WIKI, pages)
            paradata = template.format(recordId, pagetitle, refUrl, url, articleUrls[url])
            envelope = getEnvelope(recordId, url, tstamp, contrib, paradata)
            #print "{0} count: {1} sha: {2}\n".format(url, articleUrls[url], recordId)
            print json.dumps(envelope)
            envelopeList.append(envelope)
            
            
        
        
        bulkUpdate(envelopeList, opts)
        #print struct
        
def getAllPages(opts=Opts()):
    baseUrl = opts.WIKI + "api.php?action=query&list=allpages&format=json"
    
    query_dictionary = {
              'action': 'query',
              'list': 'allpages',
              'format': 'json'
    }
    
    cont = True
    while cont == True:
        query_string = '&'.join([k+'='+urllib.quote(str(v)) for (k,v) in query_dictionary.items()])
        req = urllib2.Request(opts.WIKI +"api.php", data=query_string) 
        res = urllib2.urlopen(req);
        wiki = json.load(res)
        for page in wiki["query"]["allpages"]:
            exportUrl(page["title"], opts)
        
        if wiki.has_key("query-continue"):
            query_dictionary["apfrom"] = wiki["query-continue"]["all-pages"]["apfrom"]
            cont = True
        else:
            cont = False
    
            
        

if __name__ == '__main__':
    getAllPages()
#    exportUrl("Marine_Biology")