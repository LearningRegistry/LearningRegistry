'''
Created on Aug 16, 2011

@author: jklo
'''
from services import ServiceTemplate
from setup_utils import getInput, PublishDoc, isBoolean, YES, isInt
import pystache, uuid
import json


def install(server, dbname, setupInfo):
    custom_opts = {}
    active = getInput("Enable Slice?", "T", isBoolean)
    custom_opts["active"] = active.lower() in YES
    
    active = getInput("Enable Flow Control for Slice?", "F", isBoolean)
    custom_opts["flow_control"] = active.lower() in YES
    
    if custom_opts["flow_control"]:
        active = getInput("Maximum IDs to Return?", "100", isInt)
        custom_opts["id_limit"] = int(active)
        active = getInput("Maximum Docs to Return?", "100", isInt)
        custom_opts["doc_limit"] = int(active)
        
        
    custom_opts["node_endpoint"] = setupInfo["nodeUrl"]
    custom_opts["service_id"] = uuid.uuid4().hex
    
    must = __SliceServiceTemplate()
    config_doc = must.render(**custom_opts)
    doc = json.loads(config_doc)
    PublishDoc(server, dbname,doc["service_type"]+":slice", doc)
    print("Configured Slice service:\n{0}\n".format(json.dumps(doc, indent=4, sort_keys=True)))




class __SliceServiceTemplate(ServiceTemplate):
    def __init__(self):
        ServiceTemplate.__init__(self)
        self.service_data_template = '''{
            "flow_control": {{flow_control}}{{#id_limit}},
            "id_limit": {{id_limit}}{{/id_limit}}{{#doc_limit}},
            "doc_limit": {{doc_limit}}{{/doc_limit}}
        }'''
    
    
    
    def _optsoverride(self):
        opts = {
            "active": "false",
            "service_name": "Slice",
            "service_version": "0.10.0",
            "service_endpoint": "/slice",
            "service_key": "false", 
            "service_https": "false",
            "service_type": "access",
            "flow_control": False,
            "id_limit": None,
            "doc_limit": None,
            
        }
        return opts
        
if __name__ == "__main__":
    import couchdb
    
    nodeSetup = {
                 'couchDBUrl': "http://localhost:5984",
                 'nodeUrl': "http://test.example.com"
    }
    
    def doesNotEndInSlash(input=None):
        return input is not None and input[-1] != "/"
    
    def notExample(input=None):
        return input is not None and input != nodeSetup["nodeUrl"]
    
    nodeSetup["couchDBUrl"] = getInput("Enter the CouchDB URL:", nodeSetup["couchDBUrl"], doesNotEndInSlash)
    nodeSetup["nodeUrl"] = getInput("Enter the public URL of the LR Node", nodeSetup["nodeUrl"], notExample)
    
    server =  couchdb.Server(url= nodeSetup['couchDBUrl'])
    install(server, "node", nodeSetup)
    
