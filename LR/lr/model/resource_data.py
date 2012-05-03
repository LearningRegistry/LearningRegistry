#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 8, 2011

Base model class for learning registry data model

@author: jpoyau
'''

from base_model import uuid4, createBaseModel, ModelParser, defaultCouchServer, \
appConfig, couchdb
from pylons import *
from lr.lib import helpers as h
import datetime, logging
import pprint
log = logging.getLogger(__name__)

SPEC_RESOURCE_DATA = appConfig['spec.models.resource_data']
DB_RESOURCE_DATA = appConfig['couchdb.db.resourcedata']

BaseModel = createBaseModel(SPEC_RESOURCE_DATA, DB_RESOURCE_DATA)
class ResourceDataModel(BaseModel):
    _TIME_STAMPS = ['create_timestamp', 'update_timestamp', 'node_timestamp']
    _DOC_ID = 'doc_ID'
    REPLICATION_FILTER = "filtered-replication/replication_filter"
 
    def __init__(self,  data=None):
        
        super(ResourceDataModel, self).__init__(data)
        
        # Set the timestamps by default on creation use utc.
        timeStamp = h. nowToISO8601Zformat()
        
        # Set the timestap on creation if they are not set.
        for stamp in self._TIME_STAMPS:
            if stamp not in self._specData.keys():
                self.__setattr__(stamp, timeStamp)
                
        # Set the doc is none is provided.
        if self._DOC_ID not in self._specData.keys():
            doc_id = uuid4().hex
            self.__setattr__(self._DOC_ID, doc_id)

    def save(self, doc_id=None, db=None, log_exceptions=True):
        return BaseModel.save(self, self.doc_ID, db, log_exceptions)





