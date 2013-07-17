#    Copyright 2011 Lockheed Martin

'''
Created on Feb 24, 2011

@author: John Poyau
'''

from pylons import *
from lr.lib import ModelParser, SpecValidationException, helpers as h
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
from resource_data_monitor import MonitorResourceDataChanges


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

# # Start process that listens the resource_data  databasechange feed in order 
# # to mirror distributable/resource_data type documents, udpate views and fire
# # periodic distribution.
MonitorResourceDataChanges.getInstance()



