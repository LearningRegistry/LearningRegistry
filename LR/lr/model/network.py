#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 11, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import BaseModel, ModelParser, defaultCouchServer, appConfig
from pylons import *
import datetime, logging

log = logging.getLogger(__name__)

SPEC_NETWORK_DESCRIPTION= appConfig['spec.models.network_description']
DB_NETWORK = appConfig['couchdb.db.network']

class NetworkModel(BaseModel):
    _modelParser = ModelParser(SPEC_NETWORK_DESCRIPTION)
    _defaultDB = BaseModel.createDB(DB_NETWORK)
    
    def __init__(self, data=None):
        BaseModel.__init__(self, data)
        
