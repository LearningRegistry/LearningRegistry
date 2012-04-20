'''
Created on Oct 11, 2011

@author: jklo
'''
from uuid import uuid1
import json
import logging
from contextlib import closing
from pylons import config
import time
import urllib2
import ijson
from ijson.parse import items
import os
import urllib
import couchdb
log = logging.getLogger(__name__)

class SetFlowControl(object):
    def __init__(self,enabled,serviceDoc):
        server = couchdb.Server(config['couchdb.url'])
        self.nodeDb = server[config['couchdb.db.node']]
        self.enabled = enabled
        self.serviceDoc = serviceDoc
    def __call__(self,f):
        def set_flow_control(*args):
            serviceDoc = self.nodeDb[self.serviceDoc]
            flowControlCurrent = serviceDoc['service_data']['flow_control']
            serviceDoc['service_data']['flow_control'] = self.enabled
            idLimit = None
            if self.enabled and serviceDoc['service_data'].has_key('id_limit'):
                idLimit = serviceDoc['service_data']['id_limit']
            docLimit = None
            if self.enabled and serviceDoc['service_data'].has_key('doc_limit'):
                docLimit = serviceDoc['service_data']['doc_limit']        
            serviceDoc['service_data']['doc_limit'] = 100
            serviceDoc['service_data']['id_limit'] = 100
            self.nodeDb[self.serviceDoc] = serviceDoc
            log.debug(serviceDoc)            
            f(*args)
            serviceDoc['service_data']['flow_control'] = flowControlCurrent
            if idLimit is None:
                del serviceDoc['service_data']['id_limit']
            else:
                serviceDoc['service_data']['id_limit'] = idLimit
            if docLimit is None:
                del serviceDoc['service_data']['doc_limit']
            else:
                serviceDoc['service_data']['doc_limit'] = docLimit            
            self.nodeDb[self.serviceDoc] = serviceDoc  
            log.debug(serviceDoc)          
        return set_flow_control
def ForceCouchDBIndexing():
    json_headers = {"Content-Type": "application/json"}
    couch = {
        "url": config["couchdb.url"],
        "resource_data": config["couchdb.db.resourcedata"]
    }

    def indexTestData(obj):
        
        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        design_docs = obj.db.view('_all_docs', **opts)
        for row in design_docs:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                for view in row.doc["views"].keys():
#                    view = row.doc["views"].keys()[0]
                    view_name = "{0}/_view/{1}".format( row.key, view)
                    index_opts = { "limit": 1, "descending": 'true'}
                    if "reduce" in row.doc["views"][view]:
                        index_opts["reduce"] = 'false'
                    # log.error("Indexing: {0}".format( view_name))
                    req = urllib2.Request("{url}/{resource_data}/{view}?{opts}".format(view=view_name, opts=urllib.urlencode(index_opts), **couch), 
                                          headers=json_headers)
                    res = urllib2.urlopen(req)
#                    view_result = obj.db.view(view_name, **index_opts)
                    # log.error("Indexed: {0}, got back: {1}".format(view_name, json.dumps(res.read())))
            else:
                pass#log.error("Not Indexing: {0}".format( row.key))
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                indexTestData(self)
                fn(self, *args, **kw)
            except :
                raise
            finally:
                indexTestData(self)
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator




def PublishTestDocs(sourceData, prefix, sleep=0, force_index=True):
    
    json_headers = {"Content-Type": "application/json"}
    test_data_log = "test-data-%s.log" % prefix
    couch = {
        "url": config["couchdb.url"],
        "resource_data": config["couchdb.db.resourcedata"]
    }
    
    def writeTestData(obj):
        if not hasattr(obj, "test_data_ids"):
            obj.test_data_ids = {}
        
        obj.test_data_ids[prefix] = []
        with open(test_data_log, "w") as plog:
            for doc in sourceData:
                doc["doc_ID"] = prefix+str(uuid1())
                obj.app.post('/publish', params=json.dumps({"documents": [ doc ]}), headers=json_headers)
                plog.write(doc["doc_ID"] + os.linesep)
                obj.test_data_ids[prefix].append(doc["doc_ID"])
                if sleep > 0:
                    time.sleep(sleep)
    
    def indexTestData(obj):
        
        if force_index == False:
            return
        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        design_docs = obj.db.view('_all_docs', **opts)
        for row in design_docs:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                for view in row.doc["views"].keys():
#                    view = row.doc["views"].keys()[0]
                    view_name = "{0}/_view/{1}".format( row.key, view)
                    index_opts = { "limit": 1, "descending": 'true'}
                    if "reduce" in row.doc["views"][view]:
                        index_opts["reduce"] = 'false'
                    # log.error("Indexing: {0}".format( view_name))
                    req = urllib2.Request("{url}/{resource_data}/{view}?{opts}".format(view=view_name, opts=urllib.urlencode(index_opts), **couch), 
                                          headers=json_headers)
                    res = urllib2.urlopen(req)
#                    view_result = obj.db.view(view_name, **index_opts)
                    # log.error("Indexed: {0}, got back: {1}".format(view_name, json.dumps(res.read())))
            else:
                pass# log.error("Not Indexing: {0}".format( row.key))
    
    def cacheTestData(obj):
        req = urllib2.Request("{url}/{resource_data}/_all_docs?include_docs=true".format(**couch), 
                              data=json.dumps({"keys":obj.test_data_ids[prefix]}), 
                              headers=json_headers)
        res = urllib2.urlopen(req)
        docs = list(items(res, 'rows.item.doc'))
        
        if not hasattr(obj, "test_data_sorted"):
            obj.test_data_sorted = {}
            
        obj.test_data_sorted[prefix] = sorted(docs, key=lambda k: k['node_timestamp'])
        
        
        
    def removeTestData(obj):
        for doc_id in obj.test_data_ids[prefix]:
            try:
                del obj.db[doc_id]
            except Exception as e:
                print e.message
            try:
                del obj.db[doc_id+"-distributable"]
            except Exception as e:
                print e.message
        
        try:        
            del obj.test_data_ids[prefix]
        except Exception as e:
            print e.message
        
        try:
            del obj.test_data_ids[prefix]
        except Exception as e:
            print e.message
        
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                writeTestData(self)
                indexTestData(self)
                cacheTestData(self)
                fn(self, *args, **kw)
            except :
                raise
            finally:
                removeTestData(self)
                indexTestData(self)
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator