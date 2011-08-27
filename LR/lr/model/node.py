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
    _DESCRIPTION_DICT_KEYS= ['active', 
                                                  'node_id',  
                                                  'node_description',
                                                  'node_name',
                                                  'node_key',
                                                  'node_admin_identity' ,
                                                  'open_connect_source',
                                                  'open_connect_dest',
                                                  'gateway_node']
    _NODE_POLICY_DESCRIPTION_DICT = ['sync_frequency',
                                                                  'deleted_data_policy',
                                                                  'accepted_version',
                                                                  'accepted_TOS',
                                                                  'accepts_anon',
                                                                  'accepts_unsigned',
                                                                  'validates_signature',
                                                                  'check_trust'
                                                                  ]
    def __init__(self, data=None):
        super(NodeModel, self).__init__(data)
    
    def _getDescriptionDict(self):
      #Call the parent factory generate class to get the first level description
        nodeDescriptionDict= NodeModel.__bases__[0]._getDescriptionDict(self) 
        if 'node_policy' in self._specData:
            validKeys = set(self.node_policy.keys()).intersection(self._NODE_POLICY_DESCRIPTION_DICT)
            nodeDescriptionDict["node_policy"] =  dict((k, self.node_policy[k]) for k in validKeys)
        return nodeDescriptionDict
        
