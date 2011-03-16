#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on Mar 8, 2011

Base model class for learning registry data model

@author: jpoyau
'''

from base_model import uuid4, BaseModel, ModelParser, defaultCouchServer, \
appConfig, couchdb
from pylons import *
import datetime, logging

log = logging.getLogger(__name__)

SPEC_RESOURCE_DATA = appConfig['spec.models.resource_data']
DB_RESOURCE_DATA = appConfig['couchdb.db.resourcedata']

_DESIGN_DOC = '_design/'
_DESIGN_DOC_FILTERS = 'filters'

# Javascript filter function code that will be added the design document of the 
# resource_data database. This function produce the same result that on 
# pylons filter function does for consistency.
filterFunction = """
    function (doc, req)
    {
        design_doc = "_design/";
        
        // Don't send the design document.
        if (doc_id && doc._id.substr(0, design_doc.length) == design_doc){
            return false;
        }
        // If there is no query parameters return send the document.
        if (!req){
            return true;
        }
        // Don't do anything if dealing with custom filter
       

        // Check to see the query parameter is valid  node filter description. if not
        // we can filter anything out so send it.
        if((custom_filter in req) && req.custom_filter == True){
            return true
        }
        // If there is no filter in the parameter just send the document.
        if (!req.filter){
            return true;
        }
        match = false;
        for(i in req.filter){
            filter_key = req.filter[i].filter_key;
            filter_value = req.filter[i].filter_value;
            doc_value = null
            regex_key = new RegExp(filter_key)
            
            for (var k in doc){
                if (filter_key.match(regex_key)){
                    doc_value = doc[filter_key];
                    break;
                }
            }
            
            if (!filter_key || !filter_value || !doc_value){
                    continue;
            }
            regex_value = new RegExp(filter_value);
            if (doc[filter_key].match(regex_value)){
                match = true;
                break;
            }
        }
        // If include_exclude  is T if the filters describe what documents to accept
        // all others are rejected F if the filters describe what documents to reject
        // all others are accepted optional, T if not present
        if(!('include_exclude' in req) || req.include_exclude ){
            if(match){
                return true;
            }
            else{return false;}
        }
        if(match){
            return false;
        }
        else{return true;}
    }
"""



def updateDesignFilters(db, filtersUpdate):
    if db is None or isinstance(db, couchdb.Database) == False or \
      filtersUpdate is None or isinstance(filtersUpdate, dict) ==False:
          log.debug("Cannot update design document for db: '"+str(db)+
                            "' with update '"+str(filtersUpdate))
          return
    designId = _DESIGN_DOC + db.name
    designUpdate = {}
    designDoc = db.get(designId)
    
    if designDoc is not  None:
        designUpdate.update(designDoc)
        if _DESIGN_DOC_FILTERS in designDoc:
            designUpdate[_DESIGN_DOC_FILTERS].update(filtersUpdate)
        else:
            designUpdate[_DESIGN_DOC_FILTERS]=filtersUpdate
            
    db[designId] = designUpdate
    
class ResourceDataModel(BaseModel):
    _TIME_STAMPS = ['create_timestamp', 'update_timestamp', 'node_timestamp']
    _DOC_ID = 'doc_ID'
    DEFAULT_FILTER = 'defaultFilter'
    
    _modelParser = ModelParser(SPEC_RESOURCE_DATA)
    _defaultDB = BaseModel.createDB(DB_RESOURCE_DATA)   
    
    # Add Filter function the design document that will be used to filter on replication.
    designFilter = {DEFAULT_FILTER: str(filterFunction)}
    updateDesignFilters(_defaultDB, designFilter) 

    def __init__(self,  data=None):
        
        BaseModel.__init__(self,  data)
        
        # Set the timestamps by default on creation.
        timeStamp = str(datetime.datetime.now())
        
        # Set the timestap on creation if they are not set.
        for stamp in self._TIME_STAMPS:
            if stamp not in self._specData.keys():
                self.__setattr__(stamp, timeStamp)
                
        # Set the doc is none is provided.
        if self._DOC_ID not in self._specData.keys():
            doc_id = uuid4().hex
            self.__setattr__(self._DOC_ID, doc_id)
            
    def save(self, doc_id=None, db=None):
        return BaseModel.save(self, doc_id=self.doc_ID, db=db)
    
    


