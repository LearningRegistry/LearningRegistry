#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 10, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import createBaseModel, ModelParser, defaultCouchServer, appConfig
import datetime, logging

log = logging.getLogger(__name__)

SPEC_NODE_DESCRIPTION= appConfig['spec.models.node_description']
DB_NODE = appConfig['couchdb.db.node']

class NodeModel(createBaseModel(SPEC_NODE_DESCRIPTION,DB_NODE)):

    def __init__(self, data=None):
        super(NodeModel, self).__init__(data)

