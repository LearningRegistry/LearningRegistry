#    Copyright 2011 Lockheed Martin

'''
Created on Feb 24, 2011

@author: John Poyau
'''

from lr.lib import ModelParser
from pylons import *
from uuid import uuid4
import couchdb, os, logging, datetime, re, pprint 
log = logging.getLogger(__name__)

#load all the models spec.
dataModelsDict = {}

#initialize the couchDB server
couchServer =  couchdb.Server(config['app_conf']['couchdb.url'])    

def loadModels():
    modelDir = config['app_conf']['models_spec_dir']
    for file in os.listdir(modelDir):
        try:
            filePath = os.path.join(modelDir, file)
            model = ModelParser(filePath=filePath)
        except Exception as e:
            print("Failed to parse model spec file: "+filePath+"\n"+str(e)+"\n\n")
            continue
        dataModelsDict[model.modelName] = model

#Load all the models. 
loadModels()

_DOC_ID = 'doc_ID'
_DOC_TYPE = 'doc_type'
_DOC_REV = 'doc_rev'
_ERROR = 'error'
_RESOURCE_DATA = 'resource_data'
_FILTER_DESCRIPTION = 'filter_description'
_CUSTOM_FILTER = 'custom_filter'
_FILTER = 'filter'
_KEY = 'key'
_FILTER_KEY = 'filtering_keys'
_FILTER_VALUE = 'filter_value'
_INCLUDE_EXCLUDE = 'include_exclude'
_REGEX = 'regex'

nodeFilter = None
nodeDescription = None
try:
    nodeFilter = couchServer['node'][_FILTER_DESCRIPTION]
    nodeDescription = couchServer['node']['description']
except:
    pass
    
#Compile the filters regular expression if we not using custom node filter.
if nodeFilter is not None and  nodeFilter[_CUSTOM_FILTER] == False:
    for filter in nodeFilter[_FILTER]:
        #put the actual key in 'key' for easy retrival.
        filter[_KEY] = filter.keys()[0]
        filter[_REGEX] = re.compile(filter.values()[0])
        
  
def isResourceDataFilteredOut(jsonObject):
    if nodeFilter is None:
        return False
    
    if nodeFilter[_CUSTOM_FILTER] == True:
        #Do custom the filter I supposed ... for now just resturn false.
        return [False, None]
    
    for f in nodeFilter[_FILTER]:
        # Ckeck if jsonObject object has the key if it has search 
        # for the regular expression in the filter otherwise keep looking
        if jsonObject.has_key(f[_KEY]) == False:
            continue
        
        matchResult = False
    
        if(f[_REGEX].search(str(jsonObject[f[_KEY]])) is not None):
            matchResult = True
        #Check if what matching means base on the include_exclude
        # True: the filters describe what documents to accept all others
        # are rejected
        # False: the filters describe what documents to reject
        # all others are accepted
        if nodeFilter[_INCLUDE_EXCLUDE] == True:
            if matchResult == False:
                return True, "excluded by filter: "+str(f)
        else:
            if matchResult == True:
               return True, "excluded by filter: "+str(f)
         
    return [False, None]
            
    
def processObject(jsonObject):
    
    results= {_DOC_ID:'', 'OK':False}
    
    if _DOC_TYPE not in jsonObject.keys():
        results[_ERROR] = "Document is missing doc type."
        log.error("\n"+pprint.pformat(results, indent=4)+"\n"+
                  rint.pformat(jsonObject, indent=4)+"\n\n")
        return results
    
    #If the document is resource data set the create_timpestap and 
    #update_timestamp.
    if jsonObject[_DOC_TYPE] == _RESOURCE_DATA:
        timeStamp = str(datetime.datetime.now())
        jsonObject['create_timestamp'] = timeStamp
        jsonObject['update_timestamp'] = timeStamp
        jsonObject['node_timestamp'] = timeStamp
        
        #set the publishing_node as this node.
        jsonObject['publishing_node'] = nodeDescription['node_id']
        #Check for document Id if not present generate one.
        if _DOC_ID not in jsonObject.keys() or jsonObject[_DOC_ID] is None:
            jsonObject[_DOC_ID] = uuid4().hex
        else:
            results[_DOC_ID] = jsonObject[_DOC_ID]
            
        #Now that we have the time validate the the data.
        try:
            dataModelsDict[jsonObject[_DOC_TYPE]].validate(jsonObject)
        except Exception as e:
            results[_ERROR] = "Validation Error: "+str(e)
            results['OK'] = False
            log.error("\n"+pprint.pformat(results, indent=4)+"\n"+
                      pprint.pformat(jsonObject, indent=4)+"\n\n")
            return results
        
        # If the document if of valid format now check to if passes the node
        # network filter.
      
        #Set couchdb _id field the document doc_ID
        jsonObject['_id']= jsonObject[_DOC_ID]
    
    db = couchServer[jsonObject[_DOC_TYPE]]
    isFilteredOut, reason = isResourceDataFilteredOut(jsonObject)
    
    if isFilteredOut == False:
        try:
            results[_DOC_ID], results[_DOC_REV]= doc_rev = db.save(jsonObject)
        except Exception as e:
            results[_ERROR] = "CouchDB save error:  "+str(e)
            results['OK'] = False
            log.error("\n"+pprint.pformat(results, indent=4)+"\n"+
                      pprint.pformat(jsonObject, indent=4)+"\n\n")
            return results
    else:
        log.debug("filter out document: "+reason+"\n"+
                   pprint.pformat(jsonObject, indent=4, width=80)+"\n\n")
        
    results['OK']=True    
    return results
