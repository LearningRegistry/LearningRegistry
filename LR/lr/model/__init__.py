#    Copyright 2011 Lockheed Martin

'''
Created on Feb 24, 2011

@author: John Poyau
'''

from pylons import *
from lr.lib import ModelParser, helpers as h
from uuid import uuid4
import couchdb, os, logging, datetime, re, pprint 
log = logging.getLogger(__name__)

from resource_data import ResourceDataModel, appConfig
from node import NodeModel
from node_filter import NodeFilterModel
from community import CommunityModel
from network import NetworkModel
from node_connectivity import NodeConnectivityModel
from node_service import NodeServiceModel
from network_policy import NetworkPolicyModel
from  node_config import LRNodeModel
from base_model import defaultCouchServer


_ERROR = 'error'
_OK = "OK"

def _getNodeDocument(docModel, docType, numType=None, isRequired=True):
    
    docs = docModel.getAll()
    docModels = filter(lambda row :'doc_type' in row and row['doc_type']==docType, docs)
    numModelDocs = len(docModels)
    
    if numType is not None and isRequired and numModelDocs != numType:
            raise(Exception("Error {0} of type '{1}' is required in database '{2}'".
                    format(numType, docType, docModel._defaultDB.name)))
    elif numModelDocs == 1 and numType is not None:
        model= docModel(docModels[0])
        model.validate()
        return model.specData
    elif numType ==1 and numModelDocs == 0:
        return {}
    else:
        results = []
        for d in docModels: 
            model = docModel(d)
            model.validate()
            results.append(model.specData)
        return results


def getNodeConfig():
    """Function that get the node configuration from couchDB"""
    #get community desciption.
    docs = CommunityModel.getAll()
    nodeConfig = {}
    
    nodeConfig['community_description']=_getNodeDocument(CommunityModel,
                                                                                'community_description', 1)
    nodeConfig['network_description'] = _getNodeDocument(NetworkModel, 
                                                                                'network_description', 1)
    nodeConfig['network_policy_description'] = _getNodeDocument(NetworkPolicyModel,
                                                                                'policy_description', 1)
    nodeConfig['node_description'] = _getNodeDocument(NodeModel, 
                                                                                "node_description", 1)
    nodeConfig['node_filter_description'] = _getNodeDocument(NodeFilterModel,
                                                                                "filter_description", 1, False)
    nodeConfig['node_services'] =_getNodeDocument(NodeServiceModel, 
                                                                                    "service_description",None)
    nodeConfig['node_connectivity'] = _getNodeDocument(NodeConnectivityModel,
                                                                                "connection_description", None)
    return nodeConfig
    
LRNode = LRNodeModel(getNodeConfig())

def isResourceDataFilteredOut(resourceData):
    
    if (LRNode.filterDescription is None or
        LRNode.filterDescription.filter is None or 
        LRNode.filterDescription.custom_filter == True):
        #Do custom the filter I supposed ... for now just resturn false.
        return [False, None]
    
    matchResult = False
    envelopFilter = ""
    for f in LRNode.filterDescription.filter:
        log.info("\n"+str(f)+"\n")
        # Ckeck if jsonObject object has the key if it has search 
        # for the regular expression in the filter otherwise keep looking
        key = f['filter_key']
        resourceValue = None
        
        for k in resourceData._specData.keys():
            if re.search(key, k) is not None:
                resourceValue = str(resourceData.__getattr__(k))
                break

        if  resourceValue is None:
            continue
            
        value = f['filter_value']
        log.info("\n"+str(key)+", "+str(value)+", "+ resourceValue+"\n")
        if(re.search(value,  resourceValue) is not None):
            matchResult = True
            envelopFilter = "Filter '"+str(f)+"' for key '"+str(key)+\
                                      "' matches '"+resourceValue+"'"
            break
    
    #Check if what matching means base on the include_exclude
    # True: the filters describe what documents to accept all others
    # are rejected
    # False: the filters describe what documents to reject
    # all others are accepted
    if LRNode.filterDescription.include_exclude is None or \
        LRNode.filterDescription.include_exclude == True:
        if matchResult == False:
            return True, "\nDocument failed to match filter: \n"+\
                           pprint.pformat(LRNode.filterDescription.specData, indent=4)+"\n"
    else:
        if matchResult == True:
           return True, "\nExcluded by filter: \n"+envelopFilter
         
    return [False, None]
    
def publish(envelopData):
    result={_OK: True}
    resourceData = None
    try:
        resourceData = ResourceDataModel(envelopData)
        isFilteredOut, reason = isResourceDataFilteredOut(resourceData)
        if isFilteredOut:
            output_message = "filter out document: "+reason+"\n"
            log.debug(output_message +
                            pprint.pformat(envelopData, indent=4, width=80)+"\n\n")
            result[_OK] = False
            result['error'] = output_message.replace("\n", "<br />")
            return result
        resourceData.publishing_node = LRNode.nodeDescription.node_id
        resourceData.save()
    except Exception as ex:
        error_message = "\n"+pprint.pformat(str(ex), indent=4)+"\n"+\
                                     pprint.pformat(envelopData, indent=4)+"\n"
        log.exception(ex)
        result[_OK]= False
        result[_ERROR] = error_message.replace("\n", "<br />")
        return result
    
    result[resourceData._DOC_ID] = resourceData.doc_ID    
    return result
