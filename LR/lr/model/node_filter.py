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

SPEC_FILTER_DESCRIPTION= appConfig['spec.models.filter_description']
DB_NODE = appConfig['couchdb.db.node']


class NodeFilterModel(createBaseModel(SPEC_FILTER_DESCRIPTION, DB_NODE)):
    _DESCRIPTION_DICT_KEYS = ["filter_name",
                                                    "custom_filter",
                                                    "include_exclude",
                                                    "filter"
                                                    ]
    def __init__(self, data=None):
        super(NodeFilterModel,self).__init__(data)
        
