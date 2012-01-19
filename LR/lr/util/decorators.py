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

log = logging.getLogger(__name__)

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