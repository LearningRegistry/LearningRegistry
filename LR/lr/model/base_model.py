#    Copyright 2011 Lockheed Martin

'''
Created on Mar 4, 2011

Base model class for learning registry data model

@author: jpoyau
'''
from pylons import config
from lr.lib import ModelParser, getFileString, SpecValidationException
import couchdb, os, logging, datetime, re, pprint, json 
from uuid import uuid4
from os import path

log = logging.getLogger(__name__)


        
#initialize the couchDB server
appConfig = config['app_conf']

#Default couchdb server that use by all the models when none is provided.
defaultCouchServer =  couchdb.Server(appConfig['couchdb.url'])    

def createBaseModel( modelSpec, defaultDBName, server=defaultCouchServer):
        
    def createDB(name, server=defaultCouchServer):
        try:
            server.create(name)
        except Exception as ex:
            pass
            #log.exception(ex)
        return server[name]
    
    def getModelPasers(modelsPath):
        modelParsers = {}

        for path in modelsPath.split(','):
            parser = ModelParser(path.strip())
            modelParsers[parser.docVersion] = parser

        return modelParsers
        
    class BaseModel(object):
        """Base model class for Learning Registry data models"""
        
        _ID = '_id'
        _REV = '_rev'
        _SPEC_DATA = '_specData'
        
        _defaultDB = createDB(defaultDBName, server)
        _modelParsers = getModelPasers(modelSpec)
    
        @classmethod
        def get(cls, doc_id, db=None):
            sourcDB = db
            if db is None:
                sourceDB = cls._defaultDB
            
            return sourceDB.get(doc_id)
            
            
        @classmethod
        def getAll(cls, db= None):
            """Returns all the documents in the database. Design documents are filtered
            out"""
            sourceDB = db
            if db is None:
                sourceDB = cls._defaultDB
                
            view = sourceDB.view('_all_docs', include_docs=True)
            # filter out any design design document.
            designDocId = "_design/"
            filteredView = filter(lambda row, key=designDocId: not row.key.startswith(key), view)
            
            return [sourceDB[row.key] for row in filteredView]
            
        def __init__(self, data=None):
            
            # Use a static string for to set the spec data property to make easy to 
            # distinguish which attributes are from the spec from those that added
            # for class processing.
            self.__dict__[self._SPEC_DATA] = {}
            self.__dict__[self._ID] = None
            self.__dict__[self._REV] = None
        
            spec_data = None
            if data is not None:
                if isinstance(data, str) or isinstance(data, unicode):
                    # Check to see if the data is a file path. if so load the the file
                    if path.exists(data):
                        spec_data = json.loads(getFileString(data))
                    else:
                        spec_data = json.loads(data)
                spec_data = {}
                spec_data.update(data)
                # Remove _id an _rev in data if t there are present so that we can have
                # a clean specData for validation
                for key in [self._ID, self._REV]:
                    if key in spec_data.keys():
                        self.__dict__[key] = spec_data[key]
                        spec_data.pop(key)
                        
                self.__setattr__(self._SPEC_DATA, spec_data)
                
        def __setattr__(self, name, value):
            # First check if the attribute that is getting set is an helper class attribute
            # outside of the spec data.  We determine this  by checking the self.__dict__ to
            # see if the attribute name is in there otherwise the attribute is treated has to be
            # spec data attribute.
            if name == self._SPEC_DATA:
                self.__dict__[self._SPEC_DATA] = value
            elif self._isSpecDataFieldKey(name):
                self._validateField(name, value)
                self.__dict__[self._SPEC_DATA][name] = value
            elif name in self.__dict__.keys():
                self.__dict__[name] = value
            else:
                raise AttributeError("'"+self.__class__.__name__+
                                                 "' object has no attribute'"+name+"'")
        
        def __getattr__(self, name):
            # Check if the attribute name is a spec attribute.
            if self._isSpecDataFieldKey(name):
                # If it is a spec attribute  and  it is set in the _specData  
                # return it otherwise return None
                return self.__dict__[self._SPEC_DATA].get(name)
            elif name in self.__dict__.keys():
                return self.__dict__[name]
            else:
                raise AttributeError("'"+self.__class__.__name__+
                                                "' object has no attribute'"+name+"'")
    
        def _isSpecDataFieldKey(self, keyName):
            #look through all the models spec for field name.
            for specModel in self._modelParsers.values():
                if keyName in specModel.modelInfo:
                    return True
            return False
        
        def _validateField(self, fieldName, value):
            # Look for a parser to validate the field against.  This done by using the
            # version to look for the parser. If doc_version is not set already don't 
            # don't anything.  The filed cannot be validate if we don't know what 
            # doc_version to use
            if self.doc_version in self._modelParsers:
                self._modelParsers[self.doc_version].validateField(fieldName, value, self._specData) 
            
        def _preValidation(self):
            pass
            
        def _validate(self):
            if self.doc_version in self._modelParsers:
                self._modelParsers[self.doc_version].validate(self._specData)
            else:
                raise SpecValidationException("missing or invalid required key: 'doc_version'")
            
        def _postValidation(self):
            pass
            
        def toJSON(self):
            """Returns JSON object of the spec data"""
            
            return json.dumps(self._specData)
            
        def validate(self):
            self._preValidation()
            self._validate()
            self._postValidation()
            
        def save(self,  doc_id= None, database = None, log_exceptions=True):
            
            # Make sure the spec data conforms to the spec before saving
            # it to the database
            self.validate()
            
            # Check if we need to generate an id for the document if none is provided.
            if doc_id is None:
                doc_id = uuid4().hex
                
            db = database
            # If no database is provided use the default one.
            if db == None:
                db = self._defaultDB
            
            result = {'OK':True}   
            
            # Use a temporary variable to hold the document the be saved. The coudb
            # client code updates the dictionary with the id and revision.  We want to 
            # keep the specData clean and conforming the the spec all the time.
            document = {self._ID: doc_id}
            document.update(self._specData)
        
            try:
                db[doc_id] = document
                
                self.__dict__[self._ID]   = document[self._ID] 
                self.__dict__[self._REV] = document[self._REV]
                
            except Exception as e:
                result['OK'] = False
                result['ERROR'] = "CouchDB save error:  "+str(e)
                if log_exceptions:
                    log.exception("\n"+pprint.pformat(result, indent=4)+"\n"+
                          pprint.pformat(document, indent=4)+"\n\n")
                        
            return result
            
        def update(self, database=None, log_exceptions=True):
            db = database
            # If no database is provided use the default one.
            if db == None:
                db = self._defaultDB
            
            self.validate()
            document = self.specData
            document[self._ID] = self.__dict__[self._ID]
            document[self._REV] = self.__dict__[self._REV]
            try:
                db.update([document])
            except Exception as ex:
                if log_exceptions:
                    log.exception(ex)
                return
            self.__dict__[self._ID]   = document[self._ID] 
            self.__dict__[self._REV] = document[self._REV]
        
        def _getDescriptionDict(self):
            try:
                validKeys = set(self.__class__._DESCRIPTION_DICT_KEYS).intersection(set(self._specData.keys()))
                return dict((k, self._specData[k]) for k in  validKeys)
            except:
                return self._specData
        # Property that return the dictionary of the spec data.
        specData = property(lambda self: dict(self._specData), None, None,  None)
        id = property(lambda self: self.__getattr__(self._ID), None, None, None)
        descriptionDict = property(lambda self: self._getDescriptionDict(), None, None, None)
        
    return BaseModel

