#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 10, 2011

Base model class for learning registry data model

@author: jpoyau
'''


from base_model import BaseModel, ModelParser, defaultCouchServer, appConfig
import datetime, logging

log = logging.getLogger(__name__)

SPEC_NODE_DESCRIPTION= appConfig['spec.models.node_description']
DB_NODE = appConfig['couchdb.db.node']
NODE_DESCRIPTION_DOC = appConfig['couchdb.db.node.description']

class NodeModel(BaseModel):

    # Initialize the model 
    _modelParser = ModelParser(SPEC_NODE_DESCRIPTION)
    _defaultDB = BaseModel.createDB(DB_NODE)
    
    def __init__(self, data=None):
        BaseModel.__init__(self, data)
        
    def save(self, db=None):
        nodeDB = self._defaultDB
        if db is not None:
            nodeDB = db
            
        #Check if the description is already in the database before removing it.
        if NODE_DESCRIPTION_DOC in nodeDB:
            try:
                # Remove the current node and replace with the new description.
                del nodeDB[NODE_DESCRIPTION_DOC]
                pass
            except Exception as ex:
                log.exception("Couch DB node deletion error")
                return {'OK':False}
            
        return BaseModel.save(self, db=nodeDB,  doc_id=NODE_DESCRIPTION_DOC)

