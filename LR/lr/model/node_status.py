#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 10, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import createBaseModel, ModelParser, defaultCouchServer, appConfig
from pylons import *
import datetime, logging

log = logging.getLogger(__name__)

SPEC_STATUS_DESCRIPTION= appConfig['spec.models.status_description']
DB_NODE = appConfig['couchdb.db.node']

class NodeStatusModel(createBaseModel(SPEC_STATUS_DESCRIPTION, DB_NODE)):
    
    def __init__(self, data=None):
        super(NodeStatus, self).__init__(data)
