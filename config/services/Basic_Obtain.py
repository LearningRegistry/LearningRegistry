'''
Created on Aug 16, 2011

@author: jklo
'''
from service_template import ServiceTemplate
from setup_utils import getInput, PublishDoc, isBoolean, YES, isInt
import pystache, uuid
import json


def install(server, dbname, setupInfo):
    custom_opts = {}
    active = getInput("Enable Basic Obtain?", "T", isBoolean)
    custom_opts["active"] = active.lower() in YES
    
    active = getInput("Enable Basic Obtain Flow Control?", "T", isBoolean)
    custom_opts["flow_control"] = active.lower() in YES
    
    if custom_opts["flow_control"]:
        active = getInput("Maximum IDs to Return?", "100", isInt)
        custom_opts["id_limit"] = int(active)
        active = getInput("Maximum Docs to Return?", "100", isInt)
        custom_opts["doc_limit"] = int(active)
        
        
    custom_opts["node_endpoint"] = setupInfo["nodeUrl"]
    custom_opts["service_id"] = uuid.uuid4().hex
    
    return __BasicObtainServiceTemplate().install(server, dbname, custom_opts)


class __BasicObtainServiceTemplate(ServiceTemplate):
    def __init__(self):
        ServiceTemplate.__init__(self)    
        self.service_data_template = '''{
            "spec_kv_only": false,
            "flow_control": {{flow_control}}{{#id_limit}},
            "id_limit": {{id_limit}}{{/id_limit}}{{#doc_limit}},
            "doc_limit": {{doc_limit}}{{/doc_limit}}
        }'''  
        # Returns keys/pair where the keys is the destination database name
        # and value is the couchapp directory name.  This assumes a central
        # location for all couchapps.
        self.couchapps ={'resource_data': ['apps/learningregistry-resources',
                                                                   'apps/learningregistry-resource-location']
                                    }

    def _optsoverride(self):
        opts = {
            "active": "false",
            "service_name": "Basic Obtain",
            "service_version": "0.21",
            "service_endpoint": "/obtain",
            "service_key": "false", 
            "service_https": "false",
            "service_type": "access",   
            "spec_kv_only": False,
            "flow_control": False,
            "id_limit": None,
            "doc_limit":None
        }
        return opts
 

if __name__ == "__main__":
    import couchdb
    
    nodeSetup = {
                 'couchDBUrl': "http://localhost:5984",
                 'node_service_endpoint_url': "http://test.example.com"
    }
    
    def doesNotEndInSlash(input=None):
        return input is not None and input[-1] != "/"
    
    def notExample(input=None):
        return input is not None and input != nodeSetup["nodeUrl"]
    
    nodeSetup["couchDBUrl"] = getInput("Enter the CouchDB URL:", nodeSetup["couchDBUrl"], doesNotEndInSlash)
    nodeSetup["nodeUrl"] = getInput("Enter the public URL of the LR Node", nodeSetup["nodeUrl"], notExample)
    
    server =  couchdb.Server(url= nodeSetup['couchDBUrl'])
    install(server, "node", nodeSetup)
    
