import time

node_description ={
    "doc_type":		"node_description",
    "doc_version":		"0.21.0",
    "doc_scope":		"node",	
    "active":			True,
    "node_id":		"<nodeid>",	
    "node_name": 		"<user provided nodename>",
    "node_description":	"<user provided nodedesciption>",
    "node_admin_identity":	"<user provided nodeadmin>",	
    "network_id":		"Learning Registry Open, Public Network",
    "community_id":		"Learning Registry Open, Public Community",	
    "gateway_node":	False,
    "open_connect_source": True,	
    "open_connect_dest":	True,
    "node_policy":		 { "deleted_data_policy":	"no" }
}

connection_description =   {
    "doc_type":		"connection_description",
    "doc_version":		"0.10.0",
    "doc_scope":		"node",	
    "active":			True,
    "connection_id":		"<connectionID>",		
    "source_node_url":	"<URL>",	
    "destination_node_url":	"<DestURL>",	
    "gateway_connection":	False
    }
    
network_description =  {
    "doc_type":		"network_description",
    "doc_version":		"0.20.0",
    "doc_scope":		"network",
    "active":			True,	
    "network_id":		"Learning Registry Open, Public Network",
    "network_name":	"Learning Registry Open, Public Network",
    "network_description":	"Learning Registry Open, Public Network",
    "community_id":		"Learning Registry Open, Public Community",	
    "network_admin_identity":	"network.admin@learningregistry.org"
}

network_policy_description ={
    "doc_type":		"policy_description",
    "doc_version":		"0.10.0",
    "doc_scope":		"network",
    "active":			True,
    "network_id":		"Learning Registry Open, Public Network",
    "policy_id":		"Learning Registry Open, Public Network Policy",
     "policy_version":	"0.10.0",
     "TTL":			400
}

community_description ={
    "doc_type":		"community_description",
    "doc_version":		"0.20.0",
    "doc_scope":		"community",
    "active":			True,
    "community_id":		"Learning Registry Open, Public Community",	
    "community_name":	"Learning Registry Open, Public Community",	
    "community_description":"Learning Registry Open, Public Community",
    "community_admin_identity":"community.admin@learningregistry.org",
    "social_community":	True
}

service_description= {
        "doc_type": "service_description",
        "doc_version": "0.20.0",
        "doc_scope": "node", 
        "active": True,
        "service_id": "<service_id>",
        "service_type": "<server type>",
        "service_name": "<service name>",
        "service_description": "<service description>", 
        "service_version": "0.1", 
        "service_endpoint": "string", 
        "service_auth": 
                    {"service_authz":"none",
                      "service_key":False,
                     "service_https":False},
        "service_data":{}
}
