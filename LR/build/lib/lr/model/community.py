#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 11, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import createBaseModel, ModelParser, defaultCouchServer, appConfig
from pylons import *
import datetime, logging

log = logging.getLogger(__name__)

SPEC_COMMUNITY_DESCRIPTION= appConfig['spec.models.community_description']
DB_COMMUNITY = appConfig['couchdb.db.community']

class CommunityModel(createBaseModel(SPEC_COMMUNITY_DESCRIPTION,
                                                                    DB_COMMUNITY)):
    _DESCRIPTION_DICT_KEYS = ["community_name",
                                                    "community_id",
                                                    "community_description",
                                                    "community_key",
                                                    "social_community",
                                                    "community_admin_identity"]
    def __init__(self, data=None):
        super(CommunityModel, self).__init__(data)
        
