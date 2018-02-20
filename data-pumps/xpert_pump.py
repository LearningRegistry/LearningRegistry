#!/usr/bin/python


from restkit.resource import Resource
import urllib2
import time
from StringIO import StringIO
import json
import logging
import sys
from urllib import urlencode
from optparse import OptionParser
from urlparse import urljoin

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

def getDocTemplate():
    return {
            "doc_type": "resource_data",
            "doc_version": "0.11.0",
            "resource_data_type" : "metadata",
            "active" : True,
            "submitter_type": "agent",
            "submitter": "Nottingham Xpert",
            "TOS": {"submission_TOS": "https://www.learningregistry.org/tos/cc-by-3-0/v0-5/"},
            "resource_locator": None,
            "keys": [],
            "payload_placement": None,
            "payload_schema": [],
            "payload_schema_locator":None,
            "payload_locator": None,
            "resource_data": None
            }

def cleanDoc(doc):
    for key in doc.keys():
        if (doc[key] is None):
            del doc[key]

def getKeywords():
    f = open("/usr/share/dict/words")
    keywords = []
    while(f.readline()):
        w = f.readline()
        if w.strip() != '':
            keywords.append(w.strip())
    f.close()
    return keywords

def getData(sourceUrl, keyword=None):
    f = urllib2.urlopen(sourceUrl)
    data = f.read()
    f.close()
    jsonList = json.loads(str(data).replace("\r", " "))

    resourceDataList = []
    for r in jsonList:
        doc = getDocTemplate()
        doc['resource_locator'] = r['link']
        doc["payload_placement"] = "inline"
        doc["resource_data"] = r
        doc['doc_ID'] = r['xpert_id']
        if keyword is not None:
            doc['keys'].append(keyword)
        cleanDoc(doc)
        resourceDataList.append(doc)
    return resourceDataList

def getByAllKeyWords(baseUrl):
    keywords = getKeywords()
    # Use a dictionary to store the data to avoid duplicate data from the different
    # keywords
    dataDict = {}
    for k in keywords:
        url = urljoin(baseUrl, k)
        log.info("Keywork: %s" %(k))
        data = []
        try:
            data = getData(url, k)
        except Exception as e:
            log.exception(e)
            continue
        log.info("\t %s: %d\n" %(k, len(data)))
        for doc in data:
            if doc['doc_ID'] in dataDict.keys():
                dataDict['doc_ID']['keys'].append(k)
            else:
                dataDict[doc['doc_ID']] = doc
    return [dataDict.values]

def bulkUpdate(resourceList, destinationUrl):
    '''
    Save to Learning Registry
    '''
    if resourceList > 0 :
        try:
            log.info("Learning Registry Node URL: '{0}'\n".format(destinationUrl))
            res = Resource(destinationUrl)
            body = { "documents":resourceList }
            log.info("request body: %s" % (json.dumps(body),))
            clientResponse = res.post(path="/publish", payload=json.dumps(body), headers={"Content-Type":"application/json"})
            log.info("status: {0}  message: {1}".format(clientResponse.status_int, clientResponse.body_string()))
        except Exception:
            log.exception("Caught Exception When publishing to registry")
    else:
        log.info("Nothing is being updated.")

def parseCommand():

    parser = OptionParser()
    parser.add_option('-u', '--url', dest="registryUrl", help='URL of the registry to push the data.', default="http://localhost")
    parser.add_option('-o', '--output', dest="output", help='Output file instead of publish', default=None)
    parser.add_option('-s', '--source-url', dest="sourceUrl", help="The source url where to pull the data from")
    parser.add_option('-b', '--base-source-url', dest="baseSourceUrl", default=None, help="Base source url, keywords will be append to it")

    (options, args) = parser.parse_args()
    docList =[]

    if options.baseSourceUrl is not None:
        docList = getByAllKeyWords(options.baseSourceUrl)
    else:
        docList = getData(options.sourceUrl)

    print ("Number of collected  data: %d " %(len(docList)))

    if options.output is None:
        bulkUpdate(docList, options.registryUrl)
    else:
        for d in docList:
            print d



if __name__ == '__main__':
    log.info("Update Started.")
    parseCommand()
