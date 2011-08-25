#!/usr/bin/python


#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on August 19, 2011

@author: jpoyau
'''
import urllib2
import logging
from lr.lib.couch_change import *
from resource_data import ResourceDataModel
from node import NodeModel
import threading
import multiprocessing
import ctypes
import pprint
import atexit
import json
from datetime import timedelta
from pylons import config
appConfig = config['app_conf']

log = logging.getLogger(__name__)

def _resourceDataPredicate(change):
    try:
      return "doc" in change and change["doc"]["doc_type"] == "resource_data"
    except:
        return False

def _distributableDataPredicate(change):
    try:
      return "doc" in change and change["doc"]["doc_type"] == "resource_data_distributable"
    except:
        return False

def _updateDatabaseViews():
    try:
        database = ResourceDataModel._defaultDB
        designDocs = database.view('_all_docs',include_docs=True,
                                                        startkey='_design%2F',endkey='_design0')
        for designDoc in designDocs:
            if designDoc.doc.has_key('views') and len(designDoc.doc['views']) > 0:
                viewName = "{0}/_view/{1}".format(designDoc.id,designDoc.doc['views'].keys()[0])
                log.debug('start view update %s' % viewName)
                log.debug(len(db.view(viewName))) 
    except Exception as e:
        log.error(e)

def _doDistribute():
    
    log.debug('start distribute')
    data = json.dumps({"dist":"dist"})
    request = urllib2.Request(appConfig['lr.distribute.url'],data,{'Content-Type':'application/json; charset=utf-8'})
    log.debug(pprint.pformat(request))
    response = urllib2.urlopen(request)   
    log.debug('end distribute')


class RecordDistributableChange(DatabaseChangeHandler):
    def __init__(self, database):
        self._database = database
        
    def _canHandle(self, change):
        return _distributableDataPredicate(change)
    
    def _getResourceDataDoc(self, docID):
        # There exist already a resource_data document for the distributable
        # get it and see if it needs to be updated.
        try:
            return  ResourceDataModel(self._database[docID])._specData
        except Exception as e:
            log.error("\n\nCannot find existing resource_data doc for distributable: \n{0}".format(
                            docID))
            log.exception(e)
            return None
    
    def _updateResourceData(self, newResourceData):
        currentResourceData = self._getResourceDataDoc(newResourceData['doc_ID'])
        if currentResourceData == None:
            return 
            
        # Now delete the node_timestamp field on both document before comparing them.
        temp = {}
        temp.update(currentResourceData)
        del temp['node_timestamp']
        del newResourceData['node_timestamp']
        
        if temp != newResourceData:
            currentResourceDoc.update(newResourceData)
            try:
                log.info("\nUpdate existing resource data from distributable\n")
                db.update([currentResourceData])
            except Exception as e:
                log.error("\n\nFailed to udpate existing resource_data doc:\n{0}".format(
                                pprint.pformat(currentResourceData)))
                log.exception(e)

    def _addResourceData(self, resourceDataCopy):
        # If corresponding resource_data type document is not already in the database
        # for the distributable document, create a local resource_data document and
        # add it the database
        try:
            log.info("Adding new resource_data for distributable")
            self._database[resourceDataCopy['doc_ID']] = resourceDataCopy
        except Exception as e:
            log.error("\n\nCannot get current document:  {0}".format(
                            pprint.pformat(resourceDataCopy)))
            log.exception(e)
    

    def _handle(self, change):
        # The resource data copy is what the corresponding resource data document
        #  for this distributable document should look like.
        resourceDataCopy = ResourceDataModel(change['doc'])._specData
        resourceDataCopy['doc_type'] = 'resource_data'

        # Add the corresponding resource data document to database 
        # if not already in the database.  Otherwise try to update. 
        if not resourceDataCopy['doc_ID'] in self._database:
            self._addResourceData(resourceDataCopy )
        else:
            self._updateResourceData(resourceDataCopy)

class RecordResourceDataChange(DatabaseChangeHandler):
    def __init__(self, database):
        self._database = database
        
    def _canHandle(self, change):
        return _resourceDataPredicate(change)
    
    def _updateDistributableData(self, newDistributableData):
        # Use the ResourceDataModel class to create an object that 
        # contains only a the resource_data spec data.
        currentDistributable = self._database[newDistributableData['_id']]
        temp = ResourceDataModel(currentDistributable)._specData
        del temp['node_timestamp']
         
        if newDistributableData != temp:
            currentDistributable.update(newDistributableData)
            log.info("\n\nUpdate distribuatable doc:\n")
            log.debug("\n{0}\n\n".format(pprint.pformat(currentDistributable)))
            try:
                self._database.update([currentDistributable])
            except Exception as e:
                log.error("Failed to update existing distributable doc: {0}".format(
                                pprint.pformat(currentDistributable)))
                log.exception(e)
        
        
    def _addDistributableData(self, distributableData):
        try:
            log.info('Adding distributable doc %s...\n' % distributableData['_id'])
            self._database[distributableData['_id']] = distributableData
        except Exception as e:
            log.error("Cannot save distributable document %s\n" % distributableData['_id'] )
            log.exception(e)

    def _handle(self, change):
      
        # Use the ResourceDataModel class to create an object that 
        # contains only a the resource_data spec data.
        distributableDoc = ResourceDataModel(change['doc'])._specData
        #remove the node timestamp
        del distributableDoc['node_timestamp']
        #change thet doc_type 
        distributableDoc['doc_type']='resource_data_distributable'
        distributableDoc['_id'] = change['doc']['_id']+"-distributable"
       
        # Check to see if a corresponding distributatable document exist.
        # not create a new distribuation document without the 
        # node_timestamp and _id+distributable.
        if not distributableDoc['_id'] in self._database:
            self._addDistributableData(distributableDoc)
        else:
            self._updateDistributableData(distributableDoc)


# Create an handler to simply track the process change sequence in database.
# We cannot use the one for the change monitor because it is running on different
# processess.
class TrackLastSequence(DatabaseChangeThresholdHandler):
    _LAST_CHANGE_SEQ = "sequence_number"
    def __init__(self, database, docID, changeSaveThreshold=25):
        DatabaseChangeThresholdHandler.__init__(self,
                                                                             None, 
                                                                             None, 
                                                                             changeSaveThreshold, 
                                                                             timedelta(seconds=5))
        self._database = database
        self._docID = docID
        self._lastSavedSequence = self.getLastSequence()
       
    
    def getLastSequence(self):
        if self._docID in self._database:
            return self._database[self._docID][self._LAST_CHANGE_SEQ]
        else:
             return -1
    
    def _saveSequence(self, sequence):
        log.info("Last process change sequence: {0}".format(sequence))
        doc ={"_id":self._docID,
                    self._LAST_CHANGE_SEQ : sequence}
        try: 
            if self._docID in self._database:
                del self._database[self._docID] 
            self._database[self._docID] = doc
        except Exception as e:
            log.error("\n\nError while saving {0} for dabase{1} \n".format(
                    self._docID,  str(self._database)))
            log.exception(e)
        
    def _canHandle(self, change):
        return (('doc' in change) and not self._docID in change['doc'])
         
    def _handle(self, change):
         if 'seq' in change:
             # Save the sequence before the last to ensure that all the change before
             # the save sequence number has been already processed.
             self._changeCount = self._changeCount + 1
             if self._shouldTakeAction():
                 self._saveSequence(change['seq'] )
                 self._resetChangeToThreshold()
            
    

_RESOURCE_DATA_CHANGE_ID =  "Resource Data Last Processed Change Sequence"
changeTracker = TrackLastSequence(ResourceDataModel._defaultDB, _RESOURCE_DATA_CHANGE_ID)

_RESOURCE_DATA_CHANGE_HANDLERS=[
    RecordDistributableChange(ResourceDataModel._defaultDB),
    RecordResourceDataChange(ResourceDataModel._defaultDB),
    DatabaseChangeThresholdHandler( _resourceDataPredicate,
                                                              _updateDatabaseViews,
                                                              appConfig['couchdb.threshold.viewupdate']),
                                                              
    DatabaseChangeThresholdHandler(_resourceDataPredicate,
                                                            _doDistribute,
                                                             appConfig['couchdb.threshold.distributes']),
    changeTracker
    ]

def monitorResourceDataChanges():
    options = {'since':changeTracker.getLastSequence()}
    log.info("\n\n-----"+pprint.pformat(options)+"------\n\n")
    changeMonitor = MonitorDatabaseChanges(ResourceDataModel._defaultDB,
                                                                           _RESOURCE_DATA_CHANGE_HANDLERS,
                                                                            options)
    changeMonitor.start()
    #changeMonitor.start(threading.current_thread())
    def atExitHandler():
        changeMonitor.terminate()
     
    atexit.register(atExitHandler)
    
if __name__ == "__main__":
    logging.basicConfig()
    monitorResourceDataChanges()
