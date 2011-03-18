#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 17, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import createBaseModel, ModelParser, defaultCouchServer, appConfig
from pylons import *
import datetime, logging

log = logging.getLogger(__name__)

SPEC_SERVICE_DESCRIPTION= appConfig['spec.models.node_service_description']
DB_NODE = appConfig['couchdb.db.node']

class NodeServiceModel(createBaseModel(SPEC_SERVICE_DESCRIPTION, DB_NODE)):
    
    PUBLISH='publish'
    ACCESS = 'access'
    BROKER = 'broker'
    DISTRIBUTE = 'distribute'
    ADMINISTRATIVE='administrative'
    
    def __init__(self, data=None):
        super(NodeServiceModel,self).__init__(data)
        
