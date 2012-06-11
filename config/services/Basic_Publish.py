'''
Created on Oct16, 2011

@author: jpoyau
'''
from service_template import ServiceTemplate
from setup_utils import getInput, PublishDoc, isBoolean, YES, isInt
import pystache, uuid
import json



def install(server, dbname, setupInfo):
    custom_opts = {}
    active = getInput("Enable Basic Publish?", "T", isBoolean)
    custom_opts["active"] = active.lower() in YES

    
    active = getInput("Maximum documents the node will accepts?", "1000", isInt)
    custom_opts["doc_limit"] = int(active)

    active = getInput("Enter message size limit in octet. \n"+
                    "This should the maximum data size the the node will accept", 4194304, isInt)

    custom_opts["msg_size_limit"] = int(active)

    custom_opts["authz"] = []
    active = getInput("Secure publish with Basic Authentication?", "T", isBoolean)
    if active:
        custom_opts["authz"].append("basicauth")

    active = getInput("Secure publish with OAuth and enable Node Signing?", "T", isBoolean)
    if active:
        custom_opts["authz"].append("oauth")

    if len(custom_opts["authz"]) == 0:
        del custom_opts["authz"]

    custom_opts["node_endpoint"] = setupInfo["nodeUrl"]
    custom_opts["service_id"] = uuid.uuid4().hex
    
    return __BasicPublishServiceTemplate().install(server, dbname, custom_opts)
  

class __BasicPublishServiceTemplate(ServiceTemplate):
    def __init__(self):
        ServiceTemplate.__init__(self)    
        self.service_data_template = '''{
            "msg_size_limit": {{msg_size_limit}}{{/msg_size_limit}},
            "doc_limit": {{doc_limit}}{{/doc_limit}}
        }'''
    
    def _optsoverride(self):
        opts = {
            "active": "false",
            "service_type": "publish",
            "service_name": "Basic Publish",
            "service_version": "0.23.0",
            "service_endpoint": "/publish",
            "service_key": "false", 
            "service_https": "false",
            "doc_limit": None ,
            "msg_size_limit": None
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
    
