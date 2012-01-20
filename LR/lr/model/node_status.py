#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 10, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import createBaseModel, ModelParser, \
                            defaultCouchServer, appConfig
from pylons import *
import datetime, logging


log = logging.getLogger(__name__)

SPEC_STATUS_DESCRIPTION= appConfig['spec.models.status_description']
DB_NODE = appConfig['couchdb.db.node']

class NodeStatusModel(createBaseModel(SPEC_STATUS_DESCRIPTION, DB_NODE)):
    
    def __init__(self, data=None):
        # Node status is model that create and   does not have any doc_version.
        # so set its doc_version to node.  This model should probably be removed,
        # alternate method should be implemented.
        self.__dict__['doc_version'] = None
        super(NodeStatusModel, self).__init__(data)
