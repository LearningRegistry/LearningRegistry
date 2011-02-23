from lr.lib import ModelParser
from pylons import *
import couchdb, os, logging, datetime 
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


def processObject(jsonObject):
    results= {_DOC_ID:''}
    if _DOC_TYPE not in jsonObject.keys():
        results[_ERROR] = "Document is missing doc type."
        return results
    
    #If the document is resource data set the create_timpestap and 
    #update_timestamp.
    if jsonObject[_DOC_TYPE] == _RESOURCE_DATA:
        jsonObject['create_timestamp'] = str(datetime.datetime.now())
        jsonObject['update_timestamp'] = str(datetime.datetime.now())
        #Now that we have the time validate the the data.
        try:
            dataModelsDict[jsonObject[_DOC_TYPE]].validate(jsonObject)
        except Exception as e:
            results[_ERROR] = str(e)
            return results
        
        
    db = couchServer[jsonObject[_DOC_TYPE]]
    results[_DOC_ID], results[_DOC_REV]= doc_rev = db.save(jsonObject)
    return results
