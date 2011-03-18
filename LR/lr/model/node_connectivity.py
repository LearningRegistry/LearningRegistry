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

SPEC_NODE_CONNECTIVITY_DESCRIPTION= appConfig['spec.models.node_connectivity_description']
DB_NODE = appConfig['couchdb.db.node']

class NodeConnectivityModel(createBaseModel(SPEC_NODE_CONNECTIVITY_DESCRIPTION, 
                                                            DB_NODE)):
    
    def __init__(self, data=None):
        super(NodeConnectivityModel, self).__init__(data)
