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

SPEC_NETWORK_POLICY_DESCRIPTION= appConfig['spec.models.network_policy_description']
DB_NETWORK = appConfig['couchdb.db.network']

class NetworkPolicyModel(createBaseModel(SPEC_NETWORK_POLICY_DESCRIPTION, 
                                                            DB_NETWORK)):
    _DESCRIPTION_DICT_KEYS = [ 'policy_id',
                                                     'policy_version',
                                                     'network_id']
                                                     
    def __init__(self, data=None):
        super(NetworkPolicyModel, self).__init__(data)
