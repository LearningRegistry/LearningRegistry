# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb threshold change handler class.

Created on August 31, 2011

@author: jpoyau
'''
import logging
import pprint
from lr.lib import BaseChangeHandler
from lr.model.resource_data import ResourceDataModel

_RESOURCE_DISTRIBUTABLE_TYPE = "resource_data"
_DOC_TYPE = "doc_type"
_DOC = "doc"

log = logging.getLogger(__name__)

class ResourceDataHandler(BaseChangeHandler):
    
    def _canHandle(self, change, database):
        if ((_DOC in change) and 
            (change[_DOC].get(_DOC_TYPE) ==_RESOURCE_DISTRIBUTABLE_TYPE)) :
                return True
        return False
    
    def _updateDistributableData(self, newDistributableData, distributableDocId, database):
        # Use the ResourceDataModel class to create an object that 
        # contains only a the resource_data spec data.
        currentDistributable = database[distributableDocId]
        temp = ResourceDataModel(currentDistributable)._specData
        del temp['node_timestamp']
         
        if newDistributableData != temp:
            currentDistributable.update(newDistributableData)
            log.debug("\n\nUpdate distribuatable doc:\n")
            log.debug("\n{0}\n\n".format(pprint.pformat(currentDistributable)))
            try:
                database.update([currentDistributable])
            except Exception as e:
                log.error("Failed to update existing distributable doc: {0}".format(
                                pprint.pformat(currentDistributable)))
                log.exception(e)
        
        
    def _addDistributableData(self, distributableData, distributableDocId, database):
        try:
            log.debug('Adding distributable doc %s...\n' % distributableDocId)
            database[distributableDocId] = distributableData
        except Exception as e:
            log.error("Cannot save distributable document %s\n" % distributableDocId)
            log.exception(e)

    def _handle(self, change, database):
      
        # Use the ResourceDataModel class to create an object that 
        # contains only a the resource_data spec data.
        distributableDoc = ResourceDataModel(change['doc'])._specData
        #remove the node timestamp
        del distributableDoc['node_timestamp']
        #change thet doc_type 
        distributableDoc['doc_type']='resource_data_distributable'
        distributableDocId= change['doc']['_id']+"-distributable"
       
        # Check to see if a corresponding distributatable document exist.
        # not create a new distribuation document without the 
        # node_timestamp and _id+distributable.
        if not distributableDocId in database:
            self._addDistributableData(distributableDoc, distributableDocId, database)
        else:
            self._updateDistributableData(distributableDoc, distributableDocId, database)
